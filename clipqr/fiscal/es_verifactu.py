"""España — VeriFactu (Real Decreto 1007/2023 y Orden HAC/1177/2024).

El QR de la factura es una URL al servicio de cotejo de la AEAT con cuatro parámetros: nif (emisor),
numserie (serie + número), fecha (dd-mm-aaaa) e importe (con punto decimal). Fuente: AEAT, «Características
del QR y especificaciones del servicio de cotejo o remisión de información de la factura» (v0.5.0).
"""
import datetime
import re
import urllib.parse
from decimal import Decimal, InvalidOperation

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.ids_europe import format_nif_es, nif_es_valid
from clipqr.structured import register

HOST_PRODUCCION = "www2.agenciatributaria.gob.es"
HOST_PRUEBAS = "prewww2.aeat.es"
# ruta -> facturas verificables (VERI*FACTU) o no
RUTAS = {"/wlpl/tike-cont/validarqr": True, "/wlpl/tike-cont/validarqrnoverifactu": False}
# los 4 obligatorios y el opcional «idioma» («formato» nunca puede ir en el QR)
PARAMETROS = {"nif", "numserie", "fecha", "importe", "idioma"}
INCOMPLETO = "QR de factura incompleto o modificado"


def _fecha(valor):
    """«01-09-2024» -> date, o None si no tiene el formato dd-mm-aaaa."""
    if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", valor or ""):
        return None
    try:
        return datetime.datetime.strptime(valor, "%d-%m-%Y").date()
    except ValueError:
        return None


def _importe(valor):
    """Importe con punto decimal (máx. 12 enteros y 2 decimales); None si no cumple el formato."""
    if not re.fullmatch(r"-?\d{1,12}(\.\d{1,2})?", valor or ""):
        return None
    try:
        return Decimal(valor)
    except InvalidOperation:
        return None


@register
def parse_verifactu(text):
    s = text.strip()
    if not re.match(r"https?://", s, re.I):
        return None
    parts = urllib.parse.urlsplit(s)
    host = (parts.hostname or "").lower()
    ruta = parts.path.rstrip("/").lower()
    if ruta not in RUTAS:
        return None
    verificable = RUTAS[ruta]
    query = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
    get = lambda k: (query.get(k) or [""])[0].strip()
    nif, numserie, fecha_txt, importe_txt = get("nif"), get("numserie"), get("fecha"), get("importe")

    avisos = []
    oficial = host in (HOST_PRODUCCION, HOST_PRUEBAS)
    if not oficial:
        # Misma forma que el QR de la AEAT en otro dominio: posible suplantación, no se ofrece abrirlo.
        avisos.append(f"El enlace no es de la AEAT: apunta a {host or 'un dominio desconocido'}")
    if host == HOST_PRUEBAS:
        avisos.append("QR del entorno de pruebas de la AEAT")

    fecha = _fecha(fecha_txt)
    importe = _importe(importe_txt)
    if not (nif and numserie and fecha_txt and importe_txt) or fecha is None or importe is None \
            or len(numserie) > 60 or set(query) - PARAMETROS:
        # un parámetro de más suele ser un «&» sin codificar dentro de numserie (ejemplo erróneo de la AEAT)
        avisos.append(INCOMPLETO)
    if nif and not nif_es_valid(nif):
        avisos.append("El NIF del emisor no es válido (letra o dígito de control incorrecto)")
    if fecha and fecha > datetime.date.today():
        avisos.append("La fecha de la factura es posterior a hoy")

    c = Comprobante(
        "ES", "VeriFactu" if verificable else "AEAT (no VERI*FACTU)", "Factura",
        numero=numserie, fecha=fecha.strftime("%d/%m/%Y") if fecha else fecha_txt,
        emisor=format_nif_es(nif) if nif else "", emisor_label="NIF emisor",
        importe=importe, moneda="EUR", organismo="AEAT",
        extra=[("Modalidad", "VERI*FACTU (verificable en la AEAT)" if verificable
                else "Sistema no VERI*FACTU")],
        avisos=avisos,
        acciones=[("Comprobar en la AEAT ↗", "open", s)] if oficial else [],
    )
    return invoice_result(c)
