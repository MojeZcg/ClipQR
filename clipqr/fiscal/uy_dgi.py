"""Uruguay: comprobante fiscal electrónico, CFE (DGI). El QR es la URL de la consulta pública de la DGI con
los datos separados por comas (el propio formulario de la DGI documenta el orden):

    https://www.efactura.dgi.gub.uy/consultaQR/cfe?<RUC emisor>,<tipo CFE>,<serie>,<número>,<monto total>,
        <fecha dd/mm/aaaa>,<código de seguridad (hash)>
"""
import re
from urllib.parse import unquote, urlsplit

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, fecha_dmy, importe
from clipqr.fiscal.ids_latam import format_ruc_uy, ruc_uy_valid
from clipqr.structured import register

TIPOS_CFE = {
    "101": "e-Ticket", "102": "Nota de crédito de e-Ticket", "103": "Nota de débito de e-Ticket",
    "111": "e-Factura", "112": "Nota de crédito de e-Factura", "113": "Nota de débito de e-Factura",
    "121": "e-Factura de exportación", "122": "Nota de crédito de e-Factura de exportación",
    "123": "Nota de débito de e-Factura de exportación", "124": "e-Remito de exportación",
    "131": "e-Ticket venta por cuenta ajena", "132": "Nota de crédito de e-Ticket venta por cuenta ajena",
    "133": "Nota de débito de e-Ticket venta por cuenta ajena", "141": "e-Factura venta por cuenta ajena",
    "142": "Nota de crédito de e-Factura venta por cuenta ajena",
    "143": "Nota de débito de e-Factura venta por cuenta ajena", "151": "e-Boleta de entrada",
    "152": "Nota de crédito de e-Boleta de entrada", "153": "Nota de débito de e-Boleta de entrada",
    "181": "e-Remito", "182": "e-Resguardo",
}


def tipo_cfe(codigo):
    """Los CFE de contingencia usan el código del tipo más 100 (211 = e-Factura de contingencia)."""
    if codigo in TIPOS_CFE:
        return TIPOS_CFE[codigo]
    if codigo.isdigit() and str(int(codigo) - 100) in TIPOS_CFE:
        return TIPOS_CFE[str(int(codigo) - 100)] + " (contingencia)"
    return f"CFE (tipo {codigo or '?'})"


@register
def parse_uy_dgi(text):
    s = text.strip()
    parts = urlsplit(s) if s.lower().startswith(("http://", "https://")) else None
    if (not parts or not (parts.hostname or "").lower().endswith("efactura.dgi.gub.uy")
            or not parts.path.lower().startswith("/consultaqr")):
        return None
    campos = [c.strip() for c in unquote(parts.query).split(",")]
    campos += [""] * (7 - len(campos))
    ruc, tipo, serie, numero, monto_txt, fecha_txt, hash_ = campos[:7]

    avisos = []
    if not all((ruc, tipo, numero, monto_txt, fecha_txt)):
        avisos.append(AVISO_INCOMPLETO)
    if ruc and not ruc_uy_valid(ruc):
        avisos.append(f"El RUC del emisor ({ruc}) no es válido: el QR puede estar modificado")
    # TODO verificar con la especificación oficial: el QR no indica la moneda; se asume pesos uruguayos
    # aunque el CFE puede estar emitido en dólares.
    monto = importe(monto_txt)
    if monto_txt and monto is None:
        avisos.append(f"El monto «{monto_txt}» no es un importe válido")
    fecha = fecha_dmy(fecha_txt)
    if fecha_txt and not fecha:
        avisos.append(f"La fecha «{fecha_txt}» no es válida")
    if numero and not re.fullmatch(r"\d{1,7}", numero):
        avisos.append(f"El número de comprobante «{numero}» no es válido")

    return invoice_result(Comprobante(
        "UY", "DGI (CFE)", tipo_cfe(tipo), f"{serie} {numero}".strip(), fecha or fecha_txt,
        emisor=format_ruc_uy(ruc), emisor_label="RUC emisor", importe=monto, moneda="UYU",
        autorizacion=hash_, autorizacion_label="Código de seguridad", url_verificacion=s, organismo="DGI",
        avisos=avisos))
