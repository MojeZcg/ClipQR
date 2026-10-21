"""Chile: DTE (SII). El PDF417 impreso es el «timbre electrónico» (TED), un trozo de XML:

    <TED version="1.0"><DD><RE>97975000-5</RE><TD>33</TD><F>60</F><FE>2003-10-13</FE>
      <RR>77777777-7</RR><RSR>EMPRESA  LTDA</RSR><MNT>119000</MNT><IT1>…</IT1><CAF>…</CAF>
      <TSTED>2003-10-13T09:33:20</TSTED></DD><FRMT>…</FRMT></TED>

(esquema y ejemplo oficial «F60T33-ejemplo.xml» del SII). Se lee con expresiones regulares y no con un
parser XML: los lectores de PDF417 a veces cortan la firma o cambian la codificación."""
import html
import re

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, fecha_dmy
from clipqr.fiscal.ids_latam import format_rut, rut_valid
from clipqr.structured import register

# Menú oficial del SII: Factura electrónica > Consultas de recepción de DTE > «Verificar contenido de un
# documento» (pide RUT emisor, tipo, folio, fecha y monto; requiere clave del SII).
URL_SII = "https://palena.sii.cl/cgi_dte/UPL/DTEauth?6"

TIPOS_DTE = {
    "29": "Factura de inicio", "30": "Factura", "32": "Factura exenta", "33": "Factura electrónica",
    "34": "Factura exenta electrónica", "35": "Boleta", "38": "Boleta exenta", "39": "Boleta electrónica",
    "40": "Liquidación factura", "41": "Boleta exenta electrónica", "43": "Liquidación factura electrónica",
    "45": "Factura de compra", "46": "Factura de compra electrónica", "48": "Comprobante de pago electrónico",
    "50": "Guía de despacho", "52": "Guía de despacho electrónica", "55": "Nota de débito",
    "56": "Nota de débito electrónica", "60": "Nota de crédito", "61": "Nota de crédito electrónica",
    "110": "Factura de exportación electrónica", "111": "Nota de débito de exportación electrónica",
    "112": "Nota de crédito de exportación electrónica",
}
EXPORTACION = {"110", "111", "112"}  # el monto va en la moneda de la operación, no en pesos


def _tag(dd, name):
    m = re.search(rf"<{name}>\s*(.*?)\s*</{name}>", dd, re.S)
    return html.unescape(m.group(1)).strip() if m else ""


@register
def parse_cl_sii(text):
    if "<TED" not in text or "<DD>" not in text:
        return None
    dd = text.split("<CAF", 1)[0]  # el CAF repite RE y TD: solo interesa lo de antes
    re_, td, folio, fe = (_tag(dd, t) for t in ("RE", "TD", "F", "FE"))
    rr, rsr, mnt, it1 = (_tag(dd, t) for t in ("RR", "RSR", "MNT", "IT1"))
    tsted = _tag(text, "TSTED")

    avisos = []
    if not (re_ and td and folio and mnt) or "<FRMT" not in text:
        avisos.append(AVISO_INCOMPLETO)
    for rut, label in ((re_, "del emisor"), (rr, "del receptor")):
        if rut and not rut_valid(rut):
            avisos.append(f"El RUT {label} ({rut}) no es válido: el timbre puede estar modificado")
    fecha = fecha_dmy(fe)
    if fe and not fecha:
        avisos.append(f"La fecha de emisión «{fe}» no es válida")
    if folio and not folio.isdigit():
        avisos.append(f"El folio «{folio}» no es un número")
    monto = mnt if re.fullmatch(r"\d+", mnt) else None
    if mnt and monto is None:
        avisos.append(f"El monto «{mnt}» no es un importe válido")

    extra = []
    if rsr:
        extra.append(("Razón social receptor", rsr))
    if td in EXPORTACION and monto is not None:
        extra.append(("Monto total (moneda de la operación)", monto))
        monto = None
    if it1:
        extra.append(("Primer ítem", it1))
    if tsted:
        extra.append(("Timbrado", tsted.replace("T", " ")))

    datos = "\n".join(f"{k}: {v}" for k, v in (("RUT emisor", re_), ("Tipo de documento", td),
                                                 ("Folio", folio), ("Fecha de emisión", fecha or fe),
                                                 ("Monto total", mnt)) if v)
    return invoice_result(Comprobante(
        "CL", "SII (DTE)", TIPOS_DTE.get(td, f"Documento tributario electrónico (tipo {td or '?'})"),
        numero=f"N° {folio}" if folio else "", fecha=fecha or fe,
        emisor=format_rut(re_) if re_ else "", emisor_label="RUT emisor",
        receptor=format_rut(rr) if rr else "", receptor_label="RUT receptor",
        importe=monto, moneda="CLP", url_verificacion=URL_SII, organismo="el SII", extra=extra,
        avisos=avisos, acciones=[("Copiar datos", "copy", datos)] if datos else []))
