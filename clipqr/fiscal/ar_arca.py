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
from clipqr.i18n import N_, _
from clipqr.structured import format_money, register, to_decimal

HOSTS = ("afip.gob.ar", "www.afip.gob.ar", "arca.gob.ar", "www.arca.gob.ar")
CONSTATAR = "https://serviciosweb.afip.gob.ar/genericos/comprobantes/cae.aspx"

TIPOS = {
    1: N_("Factura A"), 2: N_("Nota de débito A"), 3: N_("Nota de crédito A"), 4: N_("Recibo A"),
    6: N_("Factura B"), 7: N_("Nota de débito B"), 8: N_("Nota de crédito B"), 9: N_("Recibo B"),
    11: N_("Factura C"), 12: N_("Nota de débito C"), 13: N_("Nota de crédito C"), 15: N_("Recibo C"),
    19: N_("Factura E"), 20: N_("Nota de débito E"), 21: N_("Nota de crédito E"),
    51: N_("Factura M"), 52: N_("Nota de débito M"), 53: N_("Nota de crédito M"), 54: N_("Recibo M"),
    201: N_("Factura de crédito MiPyME A"), 202: N_("Nota de débito MiPyME A"),
    203: N_("Nota de crédito MiPyME A"),
    206: N_("Factura de crédito MiPyME B"), 207: N_("Nota de débito MiPyME B"),
    208: N_("Nota de crédito MiPyME B"),
    211: N_("Factura de crédito MiPyME C"), 212: N_("Nota de débito MiPyME C"),
    213: N_("Nota de crédito MiPyME C"),
}
# código de moneda de ARCA -> ISO 4217
MONEDAS = {"PES": "ARS", "DOL": "USD", "060": "EUR", "012": "BRL", "011": "UYU", "033": "CLP"}
DOCUMENTOS = {80: "CUIT", 86: "CUIL", 87: "CDI", 89: "LE", 90: "LC", 91: N_("CI extranjera"),
              94: N_("Pasaporte"), 96: "DNI", 99: N_("Consumidor final")}

DAMAGED = N_("QR de factura incompleto o modificado")


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
    c = Comprobante("AR", "ARCA", _("Comprobante"), organismo="ARCA", url_verificacion=text.strip(),
                    emisor_label=_("CUIT emisor"))
    if data is None:
        c.avisos.append(_(DAMAGED))
        return invoice_result(c)

    tipo = _int(data.get("tipoCmp"))
    if tipo in TIPOS:
        c.tipo = _(TIPOS[tipo])
    elif tipo is not None:
        c.tipo = _("Comprobante tipo {tipo}", tipo=tipo)
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
        doc = _(DOCUMENTOS.get(tipo_doc, N_("Documento")))
        c.receptor_label = _("{doc} receptor", doc=doc)
        c.receptor = format_cuit(nro_doc) if tipo_doc in (80, 86) else nro_doc
    elif tipo_doc == 99:
        c.receptor_label, c.receptor = _("Receptor"), _("Consumidor final")

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
        c.avisos.append(_(DAMAGED))
    if cuit and not cuit_valid(cuit):
        c.avisos.append(_("El CUIT del emisor no es válido (dígito verificador)"))
    if not aut or len(aut) != 14:
        c.avisos.append(_("Falta el {codigo} o no tiene 14 dígitos", codigo=c.autorizacion_label))
    if fecha and fecha > date.today():
        c.avisos.append(_("La fecha del comprobante es futura"))

    c.acciones.append((_("Constatar comprobante ↗"), "open", CONSTATAR))
    datos = [_("CUIT emisor: {cuit}", cuit=digits(cuit)), _("Tipo: {tipo}", tipo=tipo),
             _("Punto de venta: {pto}", pto=pto), _("Número: {nro}", nro=nro),
             _("Fecha: {fecha}", fecha=c.fecha), _("Importe: {importe}", importe=data.get("importe")),
             f"{c.autorizacion_label}: {aut}"]
    c.acciones.append((_("Copiar datos para constatar"), "copy", "\n".join(datos)))
    return invoice_result(c)
