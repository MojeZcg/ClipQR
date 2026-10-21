"""Colombia: factura electrónica de venta (DIAN). Según el Anexo Técnico 1.9 (Resolución 000165 de 2023,
numeral 11.1.7 «Código bidimensional QR») el QR lleva una línea por dato y al final la URL de consulta:

    NumFac: 323200000129
    FecFac: 2019-01-16
    HorFac: 10:53:10-05:00
    NitFac: 700085371            (sin dígito de verificación, sin puntos ni guiones)
    DocAdq: 800199436
    ValFac: 1500000.00           (punto decimal, dos decimales, sin separador de miles)
    ValIva: 285000.00
    ValOtroIm: 0.00
    ValTolFac: 1785000.00
    CUFE: e5bac48e…
    https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=<CUFE>

Las notas y demás documentos llevan «CUDE» en lugar de «CUFE». Algunos emisores ponen solo la URL."""
import re

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, fecha_dmy, importe
from clipqr.fiscal.ids_latam import format_nit, nit_dv, nit_valid
from clipqr.i18n import N_, _
from clipqr.structured import format_money, register

_CAMPO = re.compile(r"\b(NumFac|FecFac|HorFac|NitFac|DocAdq|ValFac|ValIva|ValOtroIm|ValFacIm|ValTolFac|CUFE|CUDE)"
                    r"\s*[:=]\s*([^\s|;]*)", re.I)
_URL = re.compile(r"https?://catalogo-vpfe(-hab)?\.dian\.gov\.co/document/searchqr\?documentkey=([0-9a-f]+)", re.I)
URL_DIAN = "https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey="
_CLAVES = {k.lower(): k for k in ("NumFac", "FecFac", "HorFac", "NitFac", "DocAdq", "ValFac", "ValIva",
                                  "ValOtroIm", "ValFacIm", "ValTolFac", "CUFE", "CUDE")}
VALORES = (("ValFac", N_("Valor antes de impuestos")), ("ValIva", "IVA"),
           ("ValOtroIm", N_("Otros impuestos")), ("ValFacIm", N_("Impuestos")))


def _nit(valor, avisos):
    """NIT del facturador. El QR lo trae sin DV; se muestra con el DV calculado. Si trae «-DV», se comprueba."""
    if re.fullmatch(r"\d{5,15}-\d", valor):
        if not nit_valid(valor):
            avisos.append(_("El NIT del facturador ({nit}) no es válido: el QR puede estar modificado", nit=valor))
        return format_nit(valor, con_dv=True)
    if re.fullmatch(r"\d{5,15}", valor):
        return f"{format_nit(valor)}-{nit_dv(valor)}"
    avisos.append(_("El NIT del facturador «{nit}» no es un número válido: el QR puede estar modificado",
                    nit=valor))
    return valor


@register
def parse_co_dian(text):
    url_m = _URL.search(text)
    campos = {}
    for k, v in _CAMPO.findall(text):
        campos.setdefault(_CLAVES[k.lower()], v)
    if not url_m and not ("NumFac" in campos and ("CUFE" in campos or "CUDE" in campos or "NitFac" in campos)):
        return None

    avisos = []
    clave = campos.get("CUFE") or campos.get("CUDE") or ""
    codigo = "CUDE" if "CUDE" in campos else "CUFE"
    if url_m:
        if clave and clave.lower() != url_m.group(2).lower():
            avisos.append(_("El CUFE no coincide con el del enlace de la DIAN: el QR puede estar modificado"))
        clave = clave or url_m.group(2)
        url = url_m.group(0)
        if url_m.group(1):
            avisos.append(_("Documento del ambiente de habilitación (pruebas) de la DIAN"))
    else:
        url = URL_DIAN + clave if clave else ""
    solo_url = not campos
    if not solo_url and not (campos.get("NumFac") and campos.get("ValTolFac") and clave):
        avisos.append(_(AVISO_INCOMPLETO))
    if clave and not re.fullmatch(r"[0-9a-fA-F]{64,96}", clave):
        avisos.append(_("El {codigo} no tiene el formato de la DIAN", codigo=codigo))

    total_txt = campos.get("ValTolFac", "")
    total = importe(total_txt)
    if total_txt and total is None:
        avisos.append(_("El valor total «{total}» no es válido", total=total_txt))
    fecha_txt = campos.get("FecFac", "")
    fecha = fecha_dmy(fecha_txt)
    if fecha_txt and not fecha:
        avisos.append(_("La fecha de la factura «{fecha}» no es válida", fecha=fecha_txt))

    emisor = _nit(campos["NitFac"], avisos) if campos.get("NitFac") else ""
    receptor = campos.get("DocAdq", "")
    extra = []
    if campos.get("HorFac"):
        extra.append((_("Hora"), campos["HorFac"]))
    for clave_campo, label in VALORES:
        if importe(campos.get(clave_campo)) is not None:
            extra.append((_(label), format_money(campos[clave_campo], "COP", "CO")))

    tipo = _("Documento electrónico") if "CUDE" in campos else _("Factura electrónica de venta")
    return invoice_result(Comprobante(
        "CO", "DIAN", tipo, campos.get("NumFac", ""), fecha or fecha_txt,
        emisor=emisor, emisor_label=_("NIT facturador"), receptor=receptor,
        receptor_label=_("Documento adquirente"), importe=total, moneda="COP", autorizacion=clave.lower(),
        autorizacion_label=codigo, url_verificacion=url, organismo=_("la DIAN"), extra=extra, avisos=avisos))
