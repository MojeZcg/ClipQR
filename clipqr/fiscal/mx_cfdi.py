"""México: CFDI (SAT). El QR de la representación impresa es la URL del servicio de verificación:

    https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id=<UUID>&re=<RFC emisor>
        &rr=<RFC receptor>&tt=<total>&fe=<últimos 8 caracteres del sello>

(Anexo 20 de la RMF, «Especificación técnica del código de barras bidimensional»; igual en CFDI 3.3 y
4.0). Los CFDI 3.2 llevaban solo «?re=…&rr=…&tt=…&id=…», sin dominio ni «fe»; también se aceptan."""
import re
from urllib.parse import unquote_plus, urlencode, urlsplit

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, importe
from clipqr.fiscal.ids_latam import format_rfc, rfc_valid
from clipqr.i18n import _
from clipqr.structured import register

HOST = "verificacfdi.facturaelectronica.sat.gob.mx"
URL_SAT = f"https://{HOST}/default.aspx"
_UUID = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$", re.I)


def _params(query):
    """Parámetros de la consulta sin alterar «+», «/» ni «=» del sello (parse_qs los estropearía)."""
    out = {}
    for part in query.lstrip("?").split("&"):
        key, sep, value = part.partition("=")
        if sep and key.strip():
            out.setdefault(key.strip().lower(), unquote_plus(value.replace("+", "%2B")).strip())
    return out


def _rfc(value, del_emisor, avisos):
    rfc = format_rfc(value)
    if not rfc_valid(rfc):
        avisos.append(_("El RFC del emisor ({rfc}) no es válido: el QR puede estar modificado", rfc=rfc)
                      if del_emisor else
                      _("El RFC del receptor ({rfc}) no es válido: el QR puede estar modificado", rfc=rfc))
    elif rfc == "XAXX010101000":
        return _("{rfc} (público en general)", rfc=rfc)
    elif rfc == "XEXX010101000":
        return _("{rfc} (residente en el extranjero)", rfc=rfc)
    return rfc


@register
def parse_mx_cfdi(text):
    s = text.strip()
    if s.lower().startswith(("http://", "https://")):
        parts = urlsplit(s)
        if (parts.hostname or "").lower() != HOST:
            return None
        params, url = _params(parts.query), s
    elif re.match(r"^\?re=", s, re.I):  # CFDI 3.2: solo los parámetros
        params = _params(s)
        url = URL_SAT + "?" + urlencode({k: params[k] for k in ("id", "re", "rr", "tt", "fe") if k in params})
    else:
        return None

    avisos = []
    uuid = params.get("id", "").upper()
    if not uuid or not params.get("re") or not params.get("tt"):
        avisos.append(_(AVISO_INCOMPLETO))
    elif not _UUID.match(uuid):
        avisos.append(_("El folio fiscal (UUID) «{uuid}» no tiene el formato del SAT", uuid=uuid))
    # El QR no dice la moneda: «tt» es el Total del CFDI, casi siempre en MXN (puede ser USD u otra).
    total = importe(params.get("tt"))
    if params.get("tt") and total is None:
        avisos.append(_("El total «{total}» no es un importe válido", total=params["tt"]))
    emisor = _rfc(params["re"], True, avisos) if params.get("re") else ""
    receptor = _rfc(params["rr"], False, avisos) if params.get("rr") else ""
    extra = [(_("Sello (últimos 8)"), params["fe"])] if params.get("fe") else []

    return invoice_result(Comprobante(
        "MX", "SAT (CFDI)", _("Factura (CFDI)"), emisor=emisor, emisor_label=_("RFC emisor"), receptor=receptor,
        receptor_label=_("RFC receptor"), importe=total, moneda="MXN", autorizacion=uuid,
        autorizacion_label=_("Folio fiscal (UUID)"), url_verificacion=url, organismo=_("el SAT"),
        extra=extra, avisos=avisos))
