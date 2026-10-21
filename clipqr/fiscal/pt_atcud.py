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
from clipqr.i18n import N_, _
from clipqr.structured import format_money, register

# Tipos del SAF-T (PT): InvoiceType, MovementType, WorkType y PaymentType
TIPOS = {
    "FT": N_("Factura"), "FS": N_("Factura simplificada"), "FR": N_("Factura-recibo"),
    "NC": N_("Nota de crédito"), "ND": N_("Nota de débito"),
    "GR": N_("Guía de remisión"), "GT": N_("Guía de transporte"),
    "GA": N_("Guía de movimiento de activos propios"),
    "GC": N_("Guía de consignación"), "GD": N_("Guía de devolución"),
    "CM": N_("Consulta de mesa"), "CC": N_("Crédito de consignación"), "FC": N_("Factura de consignación"),
    "FO": N_("Hoja de obra"), "NE": N_("Nota de encargo"), "OU": N_("Otro documento"),
    "OR": N_("Presupuesto"), "PF": N_("Factura proforma"), "DC": N_("Documento de conferencia"),
    "RP": N_("Recibo de prima"), "RE": N_("Recibo de extorno"), "CS": N_("Imputación a coaseguradoras"),
    "LD": N_("Imputación a coaseguradora líder"), "RA": N_("Reaseguro aceptado"),
    "RC": N_("Recibo (IVA de caja)"), "RG": N_("Recibo"),
}
# Estados del SAF-T (PT): InvoiceStatus, MovementStatus, WorkStatus y PaymentStatus
ESTADOS = {"N": N_("Normal"), "S": N_("Autofacturación"), "A": N_("Anulado"),
           "R": N_("Documento de resumen"), "F": N_("Facturado"), "T": N_("Por cuenta de terceros")}
OBLIGATORIOS = ("A", "B", "C", "D", "E", "F", "G", "H", "N", "O", "Q", "R")
CONSUMIDOR_FINAL = "999999990"
INCOMPLETO = N_("QR de factura incompleto o modificado")


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
        avisos.append(_(INCOMPLETO))
    if nif_emisor and not nif_pt_valid(nif_emisor):
        avisos.append(_("El NIF del emisor no es válido (dígito de control incorrecto)"))
    if nif_cliente and pais == "PT" and not nif_pt_valid(nif_cliente):
        avisos.append(_("El NIF del adquirente no es válido (dígito de control incorrecto)"))
    if fecha and fecha > datetime.date.today():
        avisos.append(_("La fecha del documento es posterior a hoy"))
    if get("E").upper() == "A":
        avisos.append(_("Documento anulado"))

    if nif_cliente == CONSUMIDOR_FINAL:
        receptor = _("Consumidor final")
    elif nif_cliente:
        receptor = format_nif_pt(nif_cliente) if pais in ("", "PT") else f"{nif_cliente} ({pais})"
    else:
        receptor = ""
    tipo = get("D").upper()
    atcud = get("H")
    extra = []
    if impuestos is not None:
        extra.append((_("Total de impuestos"), format_money(impuestos, "EUR", "PT")))
    estado = get("E").upper()
    # «Estado del documento» y no «Estado» a secas: en Brasil «Estado» es la unidad federativa
    for etiqueta, valor in ((_("Estado del documento"),
                             (_(ESTADOS[estado]) if estado in ESTADOS else estado) if estado != "N" else ""),
                            (_("Espacio fiscal"), get("I1") if get("I1") != "0" else ""),
                            ("Hash", get("Q")), (_("Certificado del programa"), get("R")),
                            (_("Otras informaciones"), get("S"))):
        if valor:
            extra.append((etiqueta, valor))

    c = Comprobante(
        "PT", "AT Portugal",
        _(TIPOS[tipo]) if tipo in TIPOS else _("Documento {tipo}", tipo=tipo) if tipo else _("Documento"),
        numero=get("G"), fecha=fecha.strftime("%d/%m/%Y") if fecha else "",
        emisor=format_nif_pt(nif_emisor) if nif_emisor else "", emisor_label=_("NIF emisor"),
        receptor=receptor, receptor_label=_("NIF adquirente"),
        importe=total, moneda="EUR",
        # «0»: documentos sin ATCUD (anteriores a su obligatoriedad)
        autorizacion=atcud if atcud != "0" else "", autorizacion_label="ATCUD",
        organismo="AT", extra=extra, avisos=avisos,
    )
    return invoice_result(c)
