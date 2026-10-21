"""Brasil: NFC-e / NF-e (SEFAZ). El QR de la NFC-e es la URL de consulta de la SEFAZ de cada estado
(NT 2025.001 y «Manual de Padrões Técnicos do DANFE NFC-e e QR-Code»):

    versión 1: …?chNFe=<chave>&nVersao=100&tpAmb=…&vNF=…&…&cHashQRCode=…
    versión 2: …?p=<chave>|2|<tpAmb>|<id CSC>|<hash>                          (en línea)
               …?p=<chave>|2|<tpAmb>|<día>|<vNF>|<digVal>|<id CSC>|<hash>      (contingencia)
    versión 3: …?p=<chave>|3|<tpAmb>                                         (en línea)
               …?p=<chave>|3|<tpAmb>|<día>|<vNF>|<tp_idDest>|<idDest>|<firma> (contingencia)

La «chave de acesso» (44 posiciones) es cUF(2) AAMM(4) CNPJ/CPF(14) modelo(2) serie(3) número(9)
tpEmis(1) cNF(8) cDV(1, módulo 11). También se reconoce la clave sola (código de barras del DANFE de la
NF-e), pero solo si cuadran el dígito, el estado, el modelo y el CNPJ/CPF."""
import re
from urllib.parse import parse_qs, unquote, urlsplit

from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, importe
from clipqr.fiscal.ids_latam import cnpj_valid, cpf_valid, format_cnpj, format_cpf
from clipqr.i18n import N_, _
from clipqr.structured import register

UF = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
    "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
    "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}
MODELOS = {"55": "NF-e", "65": "NFC-e"}
TP_EMIS = {"1": N_("normal"), "2": N_("contingencia FS-IA"), "3": N_("contingencia SCAN"),
           "4": N_("contingencia EPEC"), "5": N_("contingencia FS-DA"), "6": N_("contingencia SVC-AN"),
           "7": N_("contingencia SVC-RS"), "9": N_("contingencia offline")}
_CHAVE = re.compile(r"^[0-9]{6}[0-9A-Z]{12}[0-9]{26}$")  # el CNPJ puede ser alfanumérico desde 2026


def chave_dv(chave):
    """Dígito verificador módulo 11 de las 43 primeras posiciones (pesos 2..9 desde la derecha; resto 0 o 1
    -> 0). Las letras del CNPJ alfanumérico valen su código ASCII menos 48."""
    # TODO verificar con la especificación oficial: el valor de las letras en el DV de la clave con CNPJ
    # alfanumérico se toma igual que en el DV del propio CNPJ.
    total = sum((ord(c) - 48) * (2 + i % 8) for i, c in enumerate(reversed(chave[:43])))
    r = total % 11
    return 0 if r < 2 else 11 - r


def chave_valida(chave):
    return bool(_CHAVE.match(chave)) and chave_dv(chave) == int(chave[43])


def _emitente(doc):
    """La clave guarda 14 posiciones: un CNPJ, o un CPF (productor rural) con tres ceros delante.
    Devuelve (tipo de documento, documento formateado, válido)."""
    if cnpj_valid(doc):
        return "CNPJ", format_cnpj(doc), True
    if doc.startswith("000") and cpf_valid(doc[3:]):
        return "CPF", format_cpf(doc[3:]), True
    return "CNPJ", format_cnpj(doc), False


def _comprobante(chave, url="", tp_amb="", dia="", valor_txt="", avisos=None):
    avisos = list(avisos or [])
    cuf, aamm, doc, modelo, serie, numero, tp_emis = (chave[:2], chave[2:6], chave[6:20], chave[20:22],
                                                     chave[22:25], chave[25:34], chave[34])
    if not chave_valida(chave):
        avisos.append(_("La clave de acceso no supera el dígito verificador: el QR puede estar modificado"))
    tipo_doc, emisor, doc_ok = _emitente(doc)
    label = _("CPF emisor") if tipo_doc == "CPF" else _("CNPJ emisor")
    if not doc_ok:
        avisos.append(_("El {doc} del emisor ({numero}) no es válido: el QR puede estar modificado",
                        doc=tipo_doc, numero=emisor))
    if tp_amb == "2":
        avisos.append(_("Emitida en ambiente de homologación (pruebas): sin valor fiscal"))
    valor = importe(valor_txt)
    if valor_txt and valor is None:
        avisos.append(_("El valor total «{total}» no es válido", total=valor_txt))

    mes, anio = aamm[2:], "20" + aamm[:2]
    fecha = ""
    if dia.isdigit() and 1 <= int(dia) <= 31:
        fecha = f"{int(dia):02d}/{mes}/{anio}"
    extra = [(_("Serie"), str(int(serie)) if serie.isdigit() else serie), (_("Estado"), UF.get(cuf, cuf))]
    if not fecha:
        extra.append((_("Mes de emisión"), f"{mes}/{anio}"))
    if tp_emis != "1":
        extra.append((_("Emisión"), _(TP_EMIS[tp_emis]) if tp_emis in TP_EMIS
                      else _("tipo {tipo}", tipo=tp_emis)))

    num = f"{numero[:3]}.{numero[3:6]}.{numero[6:]}" if numero.isdigit() else numero
    clave_txt = " ".join(chave[i:i + 4] for i in range(0, len(chave), 4))
    sefaz = f"SEFAZ-{UF[cuf]}" if cuf in UF else "SEFAZ"
    return invoice_result(Comprobante(
        "BR", sefaz, MODELOS.get(modelo) or _("Nota fiscal (modelo {modelo})", modelo=modelo),
        num, fecha, emisor=emisor, emisor_label=label, importe=valor, moneda="BRL", autorizacion=clave_txt,
        autorizacion_label=_("Clave de acceso"), url_verificacion=url, organismo=_("la {sefaz}", sefaz=sefaz),
        extra=extra, avisos=avisos, acciones=[(_("Copiar clave"), "copy", chave)]))


def _incompleto(url):
    """URL de la SEFAZ con una clave que no tiene 44 posiciones."""
    return invoice_result(Comprobante("BR", "SEFAZ", "NFC-e", url_verificacion=url,
                                      organismo=_("la {sefaz}", sefaz="SEFAZ"), avisos=[_(AVISO_INCOMPLETO)]))


@register
def parse_br_nfe(text):
    s = text.strip()
    compacto = re.sub(r"\s", "", s)
    if re.fullmatch(r"\d{44}", compacto):  # clave sola: solo si todo cuadra
        if (chave_valida(compacto) and compacto[:2] in UF and compacto[20:22] in MODELOS
                and _emitente(compacto[6:20])[2]):
            return _comprobante(compacto)
        return None

    if not s.lower().startswith(("http://", "https://")):
        return None
    parts = urlsplit(s)
    if not (parts.hostname or "").lower().endswith(".gov.br"):
        return None
    query = unquote(parts.query)
    m = re.match(r"(?:.*&)?p=([^&]*)", query, re.I)
    if m:
        campos = m.group(1).split("|")
        chave = campos[0].strip().upper()
        if not re.fullmatch(r"[0-9A-Z]{44}", chave):
            if re.fullmatch(r"[0-9A-Z]{20,50}", chave):
                return _incompleto(s)
            return None
        campos += [""] * 8
        version, tp_amb = campos[1], campos[2]
        avisos = [] if version in ("2", "3") else [_(AVISO_INCOMPLETO)]
        offline = len([c for c in campos if c]) > (5 if version == "2" else 3)
        dia, valor = (campos[3], campos[4]) if offline else ("", "")
        return _comprobante(chave, s, tp_amb, dia, valor, avisos)

    q = {k.lower(): v[0] for k, v in parse_qs(parts.query).items()}
    if "chnfe" in q:  # versión 1
        chave = q["chnfe"].strip().upper()
        if not re.fullmatch(r"[0-9A-Z]{44}", chave):
            return _incompleto(s)
        return _comprobante(chave, s, q.get("tpamb", ""), "", q.get("vnf", ""))
    return None
