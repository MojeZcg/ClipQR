"""Perú: comprobante de pago electrónico (SUNAT). El QR de la representación impresa lleva los datos
separados por «|» (RS 113-2018/SUNAT, anexo A, numeral 6.4.3):

    RUC | TIPO DE DOCUMENTO | SERIE | NUMERO | MTO TOTAL IGV | MTO TOTAL DEL COMPROBANTE |
    FECHA DE EMISION | TIPO DE DOCUMENTO ADQUIRENTE | NUMERO DE DOCUMENTO ADQUIRENTE | VALOR RESUMEN

(el PDF417 añade además el valor de la firma). Los campos que no existen van vacíos pero se mantienen."""
import re

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, fecha_dmy, importe
from clipqr.fiscal.ids_latam import format_ruc_pe, ruc_pe_valid
from clipqr.i18n import N_, _
from clipqr.structured import format_money, register

URL_SUNAT = "https://e-consulta.sunat.gob.pe/ol-ti-itconsvalicpe/ConsValiCpe.htm"  # Consulta de validez del CPE

TIPOS = {  # catálogo 01 de SUNAT
    "01": N_("Factura electrónica"), "03": N_("Boleta de venta electrónica"),
    "07": N_("Nota de crédito electrónica"), "08": N_("Nota de débito electrónica"),
    "09": N_("Guía de remisión remitente"), "12": N_("Ticket de máquina registradora"),
    "14": N_("Recibo de servicios públicos"), "20": N_("Comprobante de retención electrónico"),
    "31": N_("Guía de remisión transportista"), "40": N_("Comprobante de percepción electrónico"),
}
DOC_ADQUIRENTE = {  # catálogo 06
    "0": N_("Doc. tributario no domiciliado"), "1": "DNI", "4": N_("Carné de extranjería"), "6": "RUC",
    "7": N_("Pasaporte"), "A": N_("Cédula diplomática"), "B": N_("Doc. del país de residencia"),
}
_INICIO = re.compile(r"^\d{11}\|\d{2}\|[A-Z0-9]{4}\|", re.I)


@register
def parse_pe_sunat(text):
    s = text.strip()
    if not _INICIO.match(s):
        return None
    campos = [c.strip() for c in s.split("|")] + [""] * 10
    ruc, tipo, serie, numero, igv, total, fecha_txt, tipo_adq, num_adq, resumen = campos[:10]

    avisos = []
    if s.count("|") < 6 or not numero or not total:
        avisos.append(_(AVISO_INCOMPLETO))
    if not ruc_pe_valid(ruc):
        avisos.append(_("El RUC del emisor ({ruc}) no es válido: el QR puede estar modificado", ruc=ruc))
    if numero and not numero.isdigit():
        avisos.append(_("El número «{numero}» no es válido", numero=numero))
    monto = importe(total)
    if total and monto is None:
        avisos.append(_("El importe total «{total}» no es válido", total=total))
    fecha = fecha_dmy(fecha_txt)
    if fecha_txt and not fecha:
        avisos.append(_("La fecha de emisión «{fecha}» no es válida", fecha=fecha_txt))

    receptor, receptor_label = "", _("Adquirente")
    if num_adq and num_adq != "-" and set(num_adq) != {"0"}:
        doc = _(DOC_ADQUIRENTE.get(tipo_adq.upper(), N_("Documento")))
        receptor_label = _("{doc} adquirente", doc=doc)
        receptor = num_adq
        if tipo_adq == "6" and not ruc_pe_valid(num_adq):
            avisos.append(_("El RUC del adquirente ({ruc}) no es válido", ruc=num_adq))
    extra = []
    if importe(igv) is not None:
        extra.append(("IGV", format_money(igv, "PEN", "PE")))
    if resumen:
        extra.append((_("Valor resumen"), resumen))

    num = f"{serie.upper()}-{numero}"
    tipo_txt = _(TIPOS[tipo]) if tipo in TIPOS else _("Comprobante electrónico (tipo {tipo})", tipo=tipo)
    # El QR no indica la moneda: se asume PEN, que es lo habitual (uno en dólares saldría con «S/»).
    return invoice_result(Comprobante(
        "PE", "SUNAT", tipo_txt, num, fecha or fecha_txt,
        emisor=format_ruc_pe(ruc), emisor_label=_("RUC emisor"), receptor=receptor,
        receptor_label=receptor_label, importe=monto, moneda="PEN", url_verificacion=URL_SUNAT,
        organismo="SUNAT", extra=extra, avisos=avisos))
