"""QR de pago con el estándar EMVCo (Merchant Presented Mode): Transferencias 3.0 de Argentina (Mercado
Pago, MODO, bancos…), Pix de Brasil, Bre-B de Colombia y muchos más.

El texto es una lista TLV: id de 2 dígitos, largo de 2 dígitos y valor (los ids 26–51 y 62 llevan otra
lista dentro). Termina en «6304» + CRC16 (CCITT-FALSE) de todo lo anterior. ClipQR solo muestra y copia:
nunca paga ni abre la app del banco por su cuenta.
"""
import re

from clipqr.fiscal.ids import cbu_valid, cnpj_valid, cpf_valid, format_iban, iban_valid
from clipqr.structured import Result, format_money, register, to_decimal

# ISO 4217 numérico -> alfabético
CURRENCIES = {"032": "ARS", "986": "BRL", "170": "COP", "484": "MXN", "604": "PEN", "152": "CLP",
              "858": "UYU", "840": "USD", "978": "EUR", "600": "PYG", "068": "BOB", "356": "INR"}
COUNTRY_NAMES = {"AR": "Argentina", "BR": "Brasil", "CO": "Colombia", "MX": "México", "PE": "Perú",
                 "CL": "Chile", "UY": "Uruguay", "PY": "Paraguay", "BO": "Bolivia"}
# Fragmentos del identificador (GUI) de la red de pago -> nombre que se muestra
NETWORKS = [("br.gov.bcb.pix", "Pix"), ("mercadopago", "Mercado Pago"), ("mercadolibre", "Mercado Pago"),
            ("modo", "MODO"), ("naranjax", "Naranja X"), ("uala", "Ualá"), ("bre-b", "Bre-B"),
            ("breb", "Bre-B"), ("coelsa", "Transferencias 3.0"), ("prisma", "Transferencias 3.0"),
            ("redlink", "Transferencias 3.0"), ("banelco", "Transferencias 3.0"), ("codi", "CoDi"),
            ("dimo", "DiMo"), ("yape", "Yape"), ("plin", "Plin")]

DAMAGED = "QR de pago alterado o dañado (el código de control no coincide)"


def crc16(data):
    """CRC16/CCITT-FALSE (polinomio 0x1021, valor inicial 0xFFFF) como 4 dígitos hexadecimales."""
    crc = 0xFFFF
    for byte in data.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def parse_tlv(text):
    """«000201…» -> [(id, valor)], o None si la estructura no cuadra."""
    out, i = [], 0
    while i < len(text):
        tag, size = text[i:i + 2], text[i + 2:i + 4]
        if not (tag.isdigit() and size.isdigit()) or i + 4 + int(size) > len(text):
            return None
        out.append((tag, text[i + 4:i + 4 + int(size)]))
        i += 4 + int(size)
    return out


def _network(gui):
    low = gui.lower()
    for fragment, name in NETWORKS:
        if fragment in low:
            return name
    return None


def _pix_key_warning(key):
    """Aviso si una clave Pix con forma de CPF/CNPJ no tiene dígitos verificadores válidos."""
    if re.fullmatch(r"\d{11}", key) and not cpf_valid(key):
        return "La clave Pix parece un CPF pero no es válido"
    if re.fullmatch(r"\d{14}", key) and not cnpj_valid(key):
        return "La clave Pix parece un CNPJ pero no es válido"
    return None


@register
def parse_emv(text):
    text = text.strip()
    if not text.startswith("000201") or not re.search(r"6304[0-9A-Fa-f]{4}$", text):
        return None
    fields = parse_tlv(text)
    if fields is None:
        return Result("payment", "Pago QR", [("Código", text)], [("Copiar código de pago", "copy", text)],
                      [DAMAGED])
    top = dict(fields)
    warnings = []
    if crc16(text[:-4]) != text[-4:].upper():
        warnings.append(DAMAGED)

    country = top.get("58", "").upper()
    currency = CURRENCIES.get(top.get("53", ""), top.get("53", ""))
    amount = to_decimal(top.get("54"))
    merchant = top.get("59", "").strip()

    network, accounts, pix_key, pix_url = None, [], None, None
    for tag, value in fields:
        if not 26 <= int(tag) <= 51:
            continue
        sub = dict(parse_tlv(value) or [])
        gui = sub.get("00", "")
        network = network or _network(gui)
        if gui.lower() == "br.gov.bcb.pix":
            pix_key, pix_url = sub.get("01"), sub.get("25")
            continue
        for k, v in sub.items():
            if k != "00" and re.fullmatch(r"\d{22}", v):
                accounts.append(v)

    items = []
    if merchant:
        items.append(("Cobra", merchant))
    if pix_key:
        items.append(("Clave Pix", pix_key))
        w = _pix_key_warning(pix_key)
        if w:
            warnings.append(w)
    if pix_url:
        items.append(("Cobro Pix", pix_url))
    for acc in accounts:
        label = "CVU" if acc.startswith("000") else "CBU"
        items.append((label, acc))
        if not cbu_valid(acc):
            warnings.append(f"El {label} no es válido (dígito verificador)")
    if top.get("60"):
        items.append(("Ciudad", top["60"].strip()))
    if country:
        items.append(("País", COUNTRY_NAMES.get(country, country)))
    extra = dict(parse_tlv(top.get("62", "")) or [])
    for sub, label in (("01", "Factura"), ("05", "Referencia"), ("03", "Tienda"), ("07", "Terminal")):
        if extra.get(sub) and extra[sub] != "***":
            items.append((label, extra[sub]))
    if network:
        items.append(("Red", network))
    if top.get("01") == "12":
        items.append(("Tipo", "QR de un solo cobro"))

    title = f"Pago QR · {network}" if network else "Pago QR"
    if amount is not None:
        headline = ("Importe", format_money(amount, currency or "ARS", country or "AR"))
        subtitle = f"Para {merchant}" if merchant else None
    else:
        headline = ("Cobra", merchant or network or "Comercio")
        subtitle = "Sin importe: lo eliges en la app al pagar"
    actions = [("Copiar código de pago", "copy", text)]
    if pix_key:
        actions.append(("Copiar clave Pix", "copy", pix_key))
    for acc in accounts[:1]:
        actions.append((f"Copiar {'CVU' if acc.startswith('000') else 'CBU'}", "copy", acc))
    return Result("payment", title, items, actions, warnings, headline, subtitle)


# ---------------------------------------------------------------- Europa: transferencia SEPA y QR-factura suiza

SEPA_PURPOSES = {"GDDS": "Compra de bienes", "SALA": "Salario", "RENT": "Alquiler", "CHAR": "Donación",
                 "SUPP": "Pago a proveedor", "TAXS": "Impuestos"}


def _transfer_result(title, name, iban, amount, currency, country, reference, message, warnings, extra=()):
    items = [("Beneficiario", name)] if name else []
    items.append(("IBAN", format_iban(iban)))
    if not iban_valid(iban):
        warnings.append("El IBAN no es válido (dígitos de control)")
    items += [i for i in extra if i[1]]
    if reference:
        items.append(("Referencia", reference))
    if message:
        items.append(("Concepto", message))
    actions = [("Copiar IBAN", "copy", iban.replace(" ", ""))]
    if reference:
        actions.append(("Copiar referencia", "copy", reference))
    if amount is not None:
        headline = ("Importe", format_money(amount, currency, country))
        subtitle = f"Para {name}" if name else None
    else:
        headline = ("Beneficiario", name or format_iban(iban))
        subtitle = "Sin importe: lo eliges en la app al pagar"
    return Result("payment", title, items, actions, warnings, headline, subtitle)


@register
def parse_epc(text):
    """QR de transferencia SEPA (EPC069-12, «código GiroCode»): líneas BCD / versión / codificación / SCT…"""
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0].strip() != "BCD" or len(lines) < 7:
        return None
    lines += [""] * (12 - len(lines))
    version, service, bic, name, iban, amount_txt, purpose, ref, msg = (
        lines[1].strip(), lines[3].strip(), lines[4].strip(), lines[5].strip(), lines[6].strip(),
        lines[7].strip(), lines[8].strip(), lines[9].strip(), lines[10].strip())
    warnings = []
    if version not in ("001", "002") or service not in ("SCT", "INST") or not name or not iban:
        warnings.append("QR de transferencia incompleto o con un formato que no se reconoce")
    amount = None
    m = re.fullmatch(r"EUR(\d{1,9}(\.\d{1,2})?)", amount_txt)
    if m:
        amount = to_decimal(m[1])
    elif amount_txt:
        warnings.append("El importe no tiene el formato «EUR123.45»")
    extra = [("BIC", bic), ("Motivo", SEPA_PURPOSES.get(purpose, purpose))]
    title = "Transferencia SEPA" + (" inmediata" if service == "INST" else "")
    return _transfer_result(title, name, iban, amount, "EUR", iban[:2].upper() if iban else "ES",
                            ref, msg, warnings, extra)


@register
def parse_swiss_qr(text):
    """QR-factura suiza (Swiss Payment Standards): líneas SPC / 0200 / 1 / IBAN / acreedor… / importe…"""
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0].strip() != "SPC" or len(lines) < 28:
        return None
    lines += [""] * (32 - len(lines))
    get = lambda i: lines[i].strip()
    warnings = []
    if not get(1).startswith("02") or get(30) not in ("EPD", ""):
        warnings.append("QR-factura suiza incompleta o con un formato que no se reconoce")
    iban, name = get(3), get(5)
    city = get(9) if get(4) == "S" else get(7)
    place = " ".join(x for x in (get(8) if get(4) == "S" else "", city) if x)
    amount = to_decimal(get(18)) if get(18) else None
    currency = get(19) or "CHF"
    ref_type, ref = get(27), get(28)
    return _transfer_result("QR-factura suiza", name, iban, amount, currency, "CH", ref, get(29), warnings,
                            [("Localidad", place), ("País", get(10)),
                             ("Tipo de referencia", {"QRR": "Referencia QR", "SCOR": "Referencia ISO 11649"}
                              .get(ref_type, ""))])
