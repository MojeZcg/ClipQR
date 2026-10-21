"""Argentina: QR de comprobantes electrónicos de ARCA (ex AFIP), RG 4291.

El QR es https://www.afip.gob.ar/fe/qr/?p=<JSON en base64> con los campos ver, fecha, cuit, ptoVta,
tipoCmp, nroCmp, importe, moneda, ctz, tipoDocRec, nroDocRec, tipoCodAut («E» = CAE, «A» = CAEA) y codAut.
"""
import base64
import binascii
import json
import re
from datetime import date
from urllib.parse import parse_qs, urlsplit

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.ids import cuit_valid, digits, format_cuit
from clipqr.structured import format_money, register, to_decimal

HOSTS = ("afip.gob.ar", "www.afip.gob.ar", "arca.gob.ar", "www.arca.gob.ar")
CONSTATAR = "https://serviciosweb.afip.gob.ar/genericos/comprobantes/cae.aspx"

TIPOS = {
    1: "Factura A", 2: "Nota de débito A", 3: "Nota de crédito A", 4: "Recibo A",
    6: "Factura B", 7: "Nota de débito B", 8: "Nota de crédito B", 9: "Recibo B",
    11: "Factura C", 12: "Nota de débito C", 13: "Nota de crédito C", 15: "Recibo C",
    19: "Factura E", 20: "Nota de débito E", 21: "Nota de crédito E",
    51: "Factura M", 52: "Nota de débito M", 53: "Nota de crédito M", 54: "Recibo M",
    201: "Factura de crédito MiPyME A", 202: "Nota de débito MiPyME A", 203: "Nota de crédito MiPyME A",
    206: "Factura de crédito MiPyME B", 207: "Nota de débito MiPyME B", 208: "Nota de crédito MiPyME B",
    211: "Factura de crédito MiPyME C", 212: "Nota de débito MiPyME C", 213: "Nota de crédito MiPyME C",
}
# código de moneda de ARCA -> ISO 4217
MONEDAS = {"PES": "ARS", "DOL": "USD", "060": "EUR", "012": "BRL", "011": "UYU", "033": "CLP"}
DOCUMENTOS = {80: "CUIT", 86: "CUIL", 87: "CDI", 89: "LE", 90: "LC", 91: "CI extranjera",
              94: "Pasaporte", 96: "DNI", 99: "Consumidor final"}

DAMAGED = "QR de factura incompleto o modificado"


def _decode(p):
    """Base64 normal o URL-safe, con o sin relleno -> dict, o None."""
    p = p.strip().replace(" ", "+")
    p += "=" * (-len(p) % 4)
    for decoder in (base64.b64decode, base64.urlsafe_b64decode):
        try:
            data = json.loads(decoder(p).decode("utf-8"))
        except (binascii.Error, ValueError, UnicodeDecodeError):
            continue
        if isinstance(data, dict):
            return data
    return None


def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


@register
def parse_arca(text):
    url = urlsplit(text.strip())
    if url.scheme not in ("http", "https") or (url.hostname or "").lower() not in HOSTS:
        return None
    if not re.fullmatch(r"/fe/qr/?", url.path):
        return None
    p = (parse_qs(url.query).get("p") or [""])[0]
    data = _decode(p) if p else None
    c = Comprobante("AR", "ARCA", "Comprobante", organismo="ARCA", url_verificacion=text.strip(),
                    emisor_label="CUIT emisor")
    if data is None:
        c.avisos.append(DAMAGED)
        return invoice_result(c)

    tipo = _int(data.get("tipoCmp"))
    c.tipo = TIPOS.get(tipo, f"Comprobante tipo {tipo}" if tipo is not None else "Comprobante")
    pto, nro = _int(data.get("ptoVta")), _int(data.get("nroCmp"))
    if pto is not None and nro is not None:
        c.numero = f"{pto:05d}-{nro:08d}"

    fecha = None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(data.get("fecha", "")).strip())
    if m:
        try:
            fecha = date(int(m[1]), int(m[2]), int(m[3]))
            c.fecha = fecha.strftime("%d/%m/%Y")
        except ValueError:
            fecha = None

    cuit = digits(data.get("cuit", ""))
    if cuit:
        c.emisor = format_cuit(cuit)

    tipo_doc, nro_doc = _int(data.get("tipoDocRec")), digits(data.get("nroDocRec", ""))
    if tipo_doc is not None and nro_doc and nro_doc.strip("0"):
        doc = DOCUMENTOS.get(tipo_doc, "Documento")
        c.receptor_label = f"{doc} receptor"
        c.receptor = format_cuit(nro_doc) if tipo_doc in (80, 86) else nro_doc
    elif tipo_doc == 99:
        c.receptor_label, c.receptor = "Receptor", "Consumidor final"

    codigo = str(data.get("moneda", "PES")).strip().upper()
    c.moneda = MONEDAS.get(codigo, codigo)
    c.importe = to_decimal(data.get("importe"))
    ctz = to_decimal(data.get("ctz"))
    if ctz is not None and c.moneda != "ARS" and ctz != 1:
        c.cotizacion = format_money(ctz, "ARS", "AR")

    aut = digits(data.get("codAut", ""))
    c.autorizacion_label = "CAEA" if str(data.get("tipoCodAut", "")).strip().upper() == "A" else "CAE"
    c.autorizacion = aut

    # Lo que no cuadra
    if not (tipo and pto is not None and nro is not None and fecha and cuit and c.importe is not None):
        c.avisos.append(DAMAGED)
    if cuit and not cuit_valid(cuit):
        c.avisos.append("El CUIT del emisor no es válido (dígito verificador)")
    if not aut or len(aut) != 14:
        c.avisos.append(f"Falta el {c.autorizacion_label} o no tiene 14 dígitos")
    if fecha and fecha > date.today():
        c.avisos.append("La fecha del comprobante es futura")

    c.acciones.append(("Constatar comprobante ↗", "open", CONSTATAR))
    datos = [f"CUIT emisor: {digits(cuit)}", f"Tipo: {tipo}", f"Punto de venta: {pto}",
             f"Número: {nro}", f"Fecha: {c.fecha}", f"Importe: {data.get('importe')}",
             f"{c.autorizacion_label}: {aut}"]
    c.acciones.append(("Copiar datos para constatar", "copy", "\n".join(datos)))
    return invoice_result(c)
