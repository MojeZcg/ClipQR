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
from clipqr.i18n import N_, _
from clipqr.structured import register

# Menú oficial del SII: Factura electrónica > Consultas de recepción de DTE > «Verificar contenido de un
# documento» (pide RUT emisor, tipo, folio, fecha y monto; requiere clave del SII).
URL_SII = "https://palena.sii.cl/cgi_dte/UPL/DTEauth?6"

TIPOS_DTE = {
    "29": N_("Factura de inicio"), "30": N_("Factura"), "32": N_("Factura exenta"),
    "33": N_("Factura electrónica"), "34": N_("Factura exenta electrónica"), "35": N_("Boleta"),
    "38": N_("Boleta exenta"), "39": N_("Boleta electrónica"), "40": N_("Liquidación factura"),
    "41": N_("Boleta exenta electrónica"), "43": N_("Liquidación factura electrónica"),
    "45": N_("Factura de compra"), "46": N_("Factura de compra electrónica"),
    "48": N_("Comprobante de pago electrónico"), "50": N_("Guía de despacho"),
    "52": N_("Guía de despacho electrónica"), "55": N_("Nota de débito"),
    "56": N_("Nota de débito electrónica"), "60": N_("Nota de crédito"), "61": N_("Nota de crédito electrónica"),
    "110": N_("Factura de exportación electrónica"), "111": N_("Nota de débito de exportación electrónica"),
    "112": N_("Nota de crédito de exportación electrónica"),
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
        avisos.append(_(AVISO_INCOMPLETO))
    if re_ and not rut_valid(re_):
        avisos.append(_("El RUT del emisor ({rut}) no es válido: el timbre puede estar modificado", rut=re_))
    if rr and not rut_valid(rr):
        avisos.append(_("El RUT del receptor ({rut}) no es válido: el timbre puede estar modificado", rut=rr))
    fecha = fecha_dmy(fe)
    if fe and not fecha:
        avisos.append(_("La fecha de emisión «{fecha}» no es válida", fecha=fe))
    if folio and not folio.isdigit():
        avisos.append(_("El folio «{folio}» no es un número", folio=folio))
    monto = mnt if re.fullmatch(r"\d+", mnt) else None
    if mnt and monto is None:
        avisos.append(_("El monto «{monto}» no es un importe válido", monto=mnt))

    extra = []
    if rsr:
        extra.append((_("Razón social receptor"), rsr))
    if td in EXPORTACION and monto is not None:
        extra.append((_("Monto total (moneda de la operación)"), monto))
        monto = None
    if it1:
        extra.append((_("Primer ítem"), it1))
    if tsted:
        extra.append((_("Timbrado"), tsted.replace("T", " ")))

    datos = "\n".join(f"{k}: {v}" for k, v in ((_("RUT emisor"), re_), (_("Tipo de documento"), td),
                                                 (_("Folio"), folio), (_("Fecha de emisión"), fecha or fe),
                                                 (_("Monto total"), mnt)) if v)
    tipo = (_(TIPOS_DTE[td]) if td in TIPOS_DTE
            else _("Documento tributario electrónico (tipo {tipo})", tipo=td or "?"))
    return invoice_result(Comprobante(
        "CL", "SII (DTE)", tipo,
        numero=_("N° {folio}", folio=folio) if folio else "", fecha=fecha or fe,
        emisor=format_rut(re_) if re_ else "", emisor_label=_("RUT emisor"),
        receptor=format_rut(rr) if rr else "", receptor_label=_("RUT receptor"),
        importe=monto, moneda="CLP", url_verificacion=URL_SII, organismo=_("el SII"), extra=extra,
        avisos=avisos, acciones=[(_("Copiar datos"), "copy", datos)] if datos else []))
