"""QR de pago con el estándar EMVCo (Merchant Presented Mode): Transferencias 3.0 de Argentina (Mercado
Pago, MODO, bancos…), Pix de Brasil, Bre-B de Colombia y muchos más.

El texto es una lista TLV: id de 2 dígitos, largo de 2 dígitos y valor (los ids 26–51 y 62 llevan otra
lista dentro). Termina en «6304» + CRC16 (CCITT-FALSE) de todo lo anterior. ClipQR solo muestra y copia:
nunca paga ni abre la app del banco por su cuenta.
"""
import re

from clipqr.fiscal.ids import cbu_valid, cnpj_valid, cpf_valid
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
