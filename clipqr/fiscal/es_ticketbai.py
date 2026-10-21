"""España (País Vasco) — TicketBAI de las Diputaciones Forales de Álava, Bizkaia (Batuz) y Gipuzkoa.

El QR es una URL de la Hacienda Foral con los parámetros id (identificador TBAI), s (serie), nf (número),
i (importe) y cr (CRC-8 de la URL hasta antes de «&cr=»). El identificador es
TBAI-<NIF 9>-<ddmmaa>-<13 caracteres de la firma>-<CRC-8 de los 36 primeros caracteres, 3 dígitos>.
Fuente: «TicketBAI — Especificaciones funcionales y técnicas» v1.1 (apartados 4.3.2 y 4.3.3, anexo 3).
"""
import datetime
import re
import urllib.parse
from decimal import Decimal, InvalidOperation

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.ids_europe import format_nif_es, nif_es_valid
from clipqr.structured import register

# host -> (territorio, prefijo de la ruta en minúsculas, entorno de pruebas)
HOSTS = {
    "ticketbai.araba.eus": ("Álava", "/tbai/qrtbai", False),
    "batuz.eus": ("Bizkaia", "/qrtbai", False),
    "tbai.egoitza.gipuzkoa.eus": ("Gipuzkoa", "/qr", False),
    # TODO verificar con la especificación oficial: hosts del QR en los entornos de pruebas de Álava y Gipuzkoa
    "pruebas-ticketbai.araba.eus": ("Álava", "/tbai/qrtbai", True),
    "tbai.prep.gipuzkoa.eus": ("Gipuzkoa", "/qr", True),
}
ID_RE = re.compile(r"TBAI-([0-9A-Z]{9})-(\d{6})-(.{13})-(\d{3})")
INCOMPLETO = "QR de factura incompleto o modificado"
ALTERADO = "QR de TicketBAI alterado: el código de control no coincide"


def crc8(texto):
    """CRC-8 del anexo 3 (polinomio x⁸+x²+x+1 = 0x07, inicio 0, sin reflejar, sin XOR final) en 3 dígitos."""
    crc = 0
    for byte in texto.encode("utf-8"):
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return f"{crc:03d}"


def _fecha(ddmmaa):
    try:
        return datetime.datetime.strptime(ddmmaa, "%d%m%y").date()
    except ValueError:
        return None


@register
def parse_ticketbai(text):
    s = text.strip()
    if not re.match(r"https?://", s, re.I):
        return None
    parts = urllib.parse.urlsplit(s)
    host = (parts.hostname or "").lower()
    query = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
    get = lambda k: (query.get(k) or [""])[0].strip()
    ident = get("id")
    conocido = host in HOSTS and parts.path.lower().startswith(HOSTS[host][1])
    if not conocido and not ident.upper().startswith("TBAI-"):
        return None

    avisos = []
    territorio = HOSTS[host][0] if conocido else ""
    if not conocido:
        # Forma de QR de TicketBAI en un dominio ajeno: posible suplantación, no se ofrece abrirlo.
        avisos.append(f"El enlace no es de ninguna Hacienda Foral: apunta a {host or 'un dominio desconocido'}")
    elif HOSTS[host][2]:
        avisos.append("QR del entorno de pruebas de TicketBAI")

    serie, nf, importe_txt, cr = get("s"), get("nf"), get("i"), get("cr")
    m = ID_RE.fullmatch(ident)
    nif = fecha = None
    alterado = False
    if m:
        nif, fecha = m.group(1), _fecha(m.group(2))
        alterado = crc8(ident[:36]) != m.group(4)
    try:
        importe = Decimal(importe_txt) if re.fullmatch(r"-?\d+(\.\d+)?", importe_txt) else None
    except InvalidOperation:
        importe = None
    corte = s.rfind("&cr=")
    if corte >= 0 and re.fullmatch(r"\d{3}", cr):
        alterado = alterado or crc8(s[:corte]) != cr

    if not (m and nf and importe is not None and cr) or fecha is None or corte < 0:
        avisos.append(INCOMPLETO)
    if alterado:
        avisos.append(ALTERADO)
    if nif and not nif_es_valid(nif):
        avisos.append("El NIF del emisor no es válido (letra o dígito de control incorrecto)")
    if fecha and fecha > datetime.date.today():
        avisos.append("La fecha de la factura es posterior a hoy")

    c = Comprobante(
        "ES", "TicketBAI", "Factura",
        numero=f"{serie}-{nf}" if serie and nf else nf,
        fecha=fecha.strftime("%d/%m/%Y") if fecha else "",
        emisor=format_nif_es(nif) if nif else "", emisor_label="NIF emisor",
        importe=importe, moneda="EUR",
        autorizacion=ident, autorizacion_label="Identificador TicketBAI",
        organismo=f"Hacienda Foral de {territorio}" if territorio else "Hacienda Foral",
        extra=[("Territorio", territorio)] if territorio else [],
        avisos=avisos,
        acciones=[("Comprobar en Hacienda Foral ↗", "open", s)] if conocido else [],
    )
    return invoice_result(c)
