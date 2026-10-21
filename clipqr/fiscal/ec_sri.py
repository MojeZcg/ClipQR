"""Ecuador: comprobante electrónico (SRI). El código de barras o QR del RIDE lleva la «clave de acceso» de
49 dígitos (Ficha técnica de comprobantes electrónicos, esquema offline, tabla 1):

    fecha ddmmaaaa(8) tipo(2) RUC(13) ambiente(1) serie(6 = establecimiento 3 + punto de emisión 3)
    secuencial(9) código numérico(8) tipo de emisión(1) dígito verificador(1)

El dígito es módulo 11 con pesos 2..7 desde la derecha (11 -> 0, 10 -> 1). Como un número de 49 cifras
cualquiera no debe tomarse por una clave, solo se reconoce si cuadran el dígito, la fecha, el tipo, el
ambiente y el tipo de emisión. La clave no lleva importe."""
import re

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import fecha_dmy
from clipqr.fiscal.ids_latam import format_ruc_ec, ruc_ec_valid
from clipqr.i18n import N_, _
from clipqr.structured import register

URL_SRI = ("https://srienlinea.sri.gob.ec/comprobantes-electronicos-internet/publico/"
           "validezComprobantes.jsf")  # consulta pública de validez de comprobantes electrónicos

TIPOS = {  # tabla 3 de la ficha técnica
    "01": N_("Factura"), "03": N_("Liquidación de compra"), "04": N_("Nota de crédito"),
    "05": N_("Nota de débito"), "06": N_("Guía de remisión"), "07": N_("Comprobante de retención"),
}


def clave_dv(clave):
    total = sum(int(c) * (2 + i % 6) for i, c in enumerate(reversed(clave[:48])))
    r = 11 - total % 11
    return {11: 0, 10: 1}.get(r, r)


def clave_valida(clave):
    """Clave de acceso de 49 dígitos con dígito verificador, fecha, tipo, ambiente y emisión coherentes."""
    return (bool(re.fullmatch(r"\d{49}", clave)) and clave_dv(clave) == int(clave[48])
            and fecha_dmy(f"{clave[0:2]}/{clave[2:4]}/{clave[4:8]}") is not None
            and clave[8:10] in TIPOS and clave[23] in "12" and clave[47] in "12")


@register
def parse_ec_sri(text):
    clave = re.sub(r"\s", "", text)
    if not clave_valida(clave):
        return None
    tipo, ruc, ambiente = clave[8:10], clave[10:23], clave[23]
    estab, punto, secuencial = clave[24:27], clave[27:30], clave[30:39]

    avisos = []
    if not ruc_ec_valid(ruc):
        avisos.append(_("El RUC del emisor ({ruc}) no supera la verificación: comprueba la clave en el SRI",
                        ruc=ruc))
    if ambiente == "1":
        avisos.append(_("Comprobante del ambiente de pruebas: sin validez tributaria"))
    extra = [(_("Ambiente"), _("Pruebas") if ambiente == "1" else _("Producción"))]
    if clave[47] == "2":
        extra.append((_("Emisión"), _("Contingencia")))

    return invoice_result(Comprobante(
        "EC", "SRI", _(TIPOS[tipo]), f"{estab}-{punto}-{secuencial}",
        fecha_dmy(f"{clave[0:2]}/{clave[2:4]}/{clave[4:8]}"), emisor=format_ruc_ec(ruc),
        emisor_label=_("RUC emisor"), moneda="USD", autorizacion=clave, autorizacion_label=_("Clave de acceso"),
        url_verificacion=URL_SRI, organismo=_("el SRI"), extra=extra, avisos=avisos,
        acciones=[(_("Copiar clave"), "copy", clave)]))
