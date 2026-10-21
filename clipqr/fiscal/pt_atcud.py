"""Portugal — código QR de los documentos fiscales (Portaria n.º 195/2020, ATCUD).

Texto de campos «código:valor» separados por «*», en orden fijo: A NIF del emisor, B NIF del adquirente,
C país del adquirente, D tipo de documento, E estado, F fecha AAAAMMDD, G identificación del documento,
H ATCUD, I1… espacio fiscal y bases/IVA, N total de impuestos, O total con impuestos, Q 4 caracteres del hash,
R n.º de certificado del programa, S otras informaciones. Fuente: AT, «Especificações Técnicas — Código de
Barras Bidimensional — Código QR» v1.1.
"""
import datetime
import re
from decimal import Decimal, InvalidOperation

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.ids_europe import format_nif_pt, nif_pt_valid
from clipqr.structured import format_money, register

# Tipos del SAF-T (PT): InvoiceType, MovementType, WorkType y PaymentType
TIPOS = {
    "FT": "Factura", "FS": "Factura simplificada", "FR": "Factura-recibo",
    "NC": "Nota de crédito", "ND": "Nota de débito",
    "GR": "Guía de remisión", "GT": "Guía de transporte", "GA": "Guía de movimiento de activos propios",
    "GC": "Guía de consignación", "GD": "Guía de devolución",
    "CM": "Consulta de mesa", "CC": "Crédito de consignación", "FC": "Factura de consignación",
    "FO": "Hoja de obra", "NE": "Nota de encargo", "OU": "Otro documento", "OR": "Presupuesto",
    "PF": "Factura proforma", "DC": "Documento de conferencia", "RP": "Recibo de prima",
    "RE": "Recibo de extorno", "CS": "Imputación a coaseguradoras", "LD": "Imputación a coaseguradora líder",
    "RA": "Reaseguro aceptado", "RC": "Recibo (IVA de caja)", "RG": "Recibo",
}
# Estados del SAF-T (PT): InvoiceStatus, MovementStatus, WorkStatus y PaymentStatus
ESTADOS = {"N": "Normal", "S": "Autofacturación", "A": "Anulado", "R": "Documento de resumen",
           "F": "Facturado", "T": "Por cuenta de terceros"}
OBLIGATORIOS = ("A", "B", "C", "D", "E", "F", "G", "H", "N", "O", "Q", "R")
CONSUMIDOR_FINAL = "999999990"
INCOMPLETO = "QR de factura incompleto o modificado"


def _importe(valor):
    """Importe con punto decimal y 2 decimales («513600.58»); None si no cumple el formato."""
    if not re.fullmatch(r"-?\d+\.\d{2}", valor or ""):
        return None
    try:
        return Decimal(valor)
    except InvalidOperation:
        return None


@register
def parse_atcud(text):
    s = text.strip()
    if not re.match(r"A:[^*]*\*B:[^*]*\*C:", s):
        return None
    campos = {}
    for parte in s.split("*"):
        codigo, sep, valor = parte.partition(":")
        if sep and codigo.strip():
            campos.setdefault(codigo.strip().upper(), valor.strip())
    get = lambda k: campos.get(k, "")

    avisos = []
    nif_emisor, nif_cliente, pais = get("A"), get("B"), get("C").upper()
    fecha = None
    if re.fullmatch(r"\d{8}", get("F")):
        try:
            fecha = datetime.datetime.strptime(get("F"), "%Y%m%d").date()
        except ValueError:
            fecha = None
    total, impuestos = _importe(get("O")), _importe(get("N"))
    if any(not get(k) for k in OBLIGATORIOS) or fecha is None or total is None or impuestos is None:
        avisos.append(INCOMPLETO)
    if nif_emisor and not nif_pt_valid(nif_emisor):
        avisos.append("El NIF del emisor no es válido (dígito de control incorrecto)")
    if nif_cliente and pais == "PT" and not nif_pt_valid(nif_cliente):
        avisos.append("El NIF del adquirente no es válido (dígito de control incorrecto)")
    if fecha and fecha > datetime.date.today():
        avisos.append("La fecha del documento es posterior a hoy")
    if get("E").upper() == "A":
        avisos.append("Documento anulado")

    if nif_cliente == CONSUMIDOR_FINAL:
        receptor = "Consumidor final"
    elif nif_cliente:
        receptor = format_nif_pt(nif_cliente) if pais in ("", "PT") else f"{nif_cliente} ({pais})"
    else:
        receptor = ""
    tipo = get("D").upper()
    atcud = get("H")
    extra = []
    if impuestos is not None:
        extra.append(("Total de impuestos", format_money(impuestos, "EUR", "PT")))
    estado = get("E").upper()
    for etiqueta, valor in (("Estado", ESTADOS.get(estado, estado) if estado != "N" else ""),
                            ("Espacio fiscal", get("I1") if get("I1") != "0" else ""),
                            ("Hash", get("Q")), ("Certificado del programa", get("R")),
                            ("Otras informaciones", get("S"))):
        if valor:
            extra.append((etiqueta, valor))

    c = Comprobante(
        "PT", "AT Portugal", TIPOS.get(tipo, f"Documento {tipo}".strip()),
        numero=get("G"), fecha=fecha.strftime("%d/%m/%Y") if fecha else "",
        emisor=format_nif_pt(nif_emisor) if nif_emisor else "", emisor_label="NIF emisor",
        receptor=receptor, receptor_label="NIF adquirente",
        importe=total, moneda="EUR",
        # «0»: documentos sin ATCUD (anteriores a su obligatoriedad)
        autorizacion=atcud if atcud != "0" else "", autorizacion_label="ATCUD",
        organismo="AT", extra=extra, avisos=avisos,
    )
    return invoice_result(c)
