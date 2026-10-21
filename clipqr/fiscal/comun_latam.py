"""Utilidades compartidas por los comprobantes de Latinoamérica: fechas y textos de aviso."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from clipqr.i18n import N_

AVISO_INCOMPLETO = N_("QR de factura incompleto o modificado")  # se traduce con _() al usarlo


def fecha_dmy(texto):
    """«2026-10-21», «20261021», «21/10/2026» o «21-10-2026» -> «21/10/2026». Si no es una fecha real
    devuelve None (el que llama decide si avisar)."""
    s = str(texto or "").strip()
    m = (re.fullmatch(r"(\d{4})-?(\d{2})-?(\d{2})(?:[T ].*)?", s)
         or re.fullmatch(r"(\d{2})[/-](\d{2})[/-](\d{4})", s))
    if not m:
        return None
    a, b, c = m.groups()
    y, mo, d = (int(a), int(b), int(c)) if len(a) == 4 else (int(c), int(b), int(a))
    try:
        return date(y, mo, d).strftime("%d/%m/%Y")
    except ValueError:
        return None


def importe(texto):
    """Importe con punto decimal y sin separadores de miles («1785000.00») -> Decimal, o None."""
    s = str(texto or "").strip()
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", s):
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None
