"""Productos GS1: códigos de barras EAN/UPC/GTIN, GS1 Digital Link (https://…/01/<GTIN>/10/<lote>…) y
cadenas de identificadores de aplicación (AI) de GS1 DataMatrix, GS1 QR y GS1-128: «(01)…(17)…(10)…».

Muestra el GTIN (con su dígito verificador comprobado), el lote, la serie y las fechas; avisa si el
producto está vencido o vence en los próximos 30 días.
"""
import calendar
import re
from datetime import date
from urllib.parse import parse_qsl, quote, urlsplit

from clipqr.structured import Result, register

GS = "\x1d"  # separador FNC1 dentro de los datos

# AI -> (nombre, largo fijo o None si es variable, largo máximo)
AIS = {
    "00": ("SSCC (envío)", 18, 18), "01": ("GTIN", 14, 14), "02": ("GTIN contenido", 14, 14),
    "10": ("Lote", None, 20), "11": ("Fabricado", 6, 6), "12": ("Vence el pago", 6, 6),
    "13": ("Envasado", 6, 6), "15": ("Consumir preferentemente antes de", 6, 6),
    "16": ("Vender antes de", 6, 6), "17": ("Vencimiento", 6, 6), "20": ("Variante", 2, 2),
    "21": ("Número de serie", None, 20), "22": ("Variante de consumo", None, 20),
    "30": ("Cantidad", None, 8), "37": ("Unidades", None, 8), "240": ("Referencia", None, 30),
    "241": ("Pieza del cliente", None, 30), "250": ("Serie secundaria", None, 30),
    "400": ("Pedido", None, 30), "410": ("Enviar a (GLN)", 13, 13), "414": ("Ubicación (GLN)", 13, 13),
    "422": ("País de origen", 3, 3), "7003": ("Vence (fecha y hora)", 10, 10),
}
DATES = {"11", "12", "13", "15", "16", "17"}
# 4 dígitos: 310n peso neto (kg), 320n (lb), 330n peso bruto, 392n/393n precio
MEASURES = {"310": ("Peso neto", "kg"), "311": ("Largo", "m"), "320": ("Peso neto", "lb"),
            "330": ("Peso bruto", "kg"), "392": ("Precio", ""), "393": ("Precio", "")}

# Prefijo GS1 -> país de la organización que asignó el código (no siempre el de fabricación)
PREFIXES = [
    (0, 19, "EE. UU. y Canadá"), (30, 39, "EE. UU."), (60, 139, "EE. UU. y Canadá"), (300, 379, "Francia"),
    (380, 380, "Bulgaria"), (400, 440, "Alemania"), (450, 459, "Japón"), (460, 469, "Rusia"),
    (471, 471, "Taiwán"), (480, 480, "Filipinas"), (489, 489, "Hong Kong"), (490, 499, "Japón"),
    (500, 509, "Reino Unido"), (520, 521, "Grecia"), (539, 539, "Irlanda"), (540, 549, "Bélgica y Luxemburgo"),
    (560, 560, "Portugal"), (570, 579, "Dinamarca"), (590, 590, "Polonia"), (600, 601, "Sudáfrica"),
    (690, 699, "China"), (700, 709, "Noruega"), (729, 729, "Israel"), (730, 739, "Suecia"),
    (740, 740, "Guatemala"), (741, 741, "El Salvador"), (742, 742, "Honduras"), (743, 743, "Nicaragua"),
    (744, 744, "Costa Rica"), (745, 745, "Panamá"), (746, 746, "República Dominicana"), (750, 750, "México"),
    (754, 755, "Canadá"), (759, 759, "Venezuela"), (760, 769, "Suiza"), (770, 771, "Colombia"),
    (773, 773, "Uruguay"), (775, 775, "Perú"), (777, 777, "Bolivia"), (778, 779, "Argentina"),
    (780, 780, "Chile"), (784, 784, "Paraguay"), (786, 786, "Ecuador"), (789, 790, "Brasil"),
    (800, 839, "Italia"), (840, 849, "España"), (850, 850, "Cuba"), (858, 858, "Eslovaquia"),
    (859, 859, "República Checa"), (869, 869, "Turquía"), (870, 879, "Países Bajos"), (880, 880, "Corea del Sur"),
    (885, 885, "Tailandia"), (888, 888, "Singapur"), (890, 890, "India"), (893, 893, "Vietnam"),
    (899, 899, "Indonesia"), (900, 919, "Austria"), (930, 939, "Australia"), (940, 949, "Nueva Zelanda"),
    (955, 955, "Malasia"), (977, 977, "Revista (ISSN)"), (978, 979, "Libro (ISBN)"),
]


def gtin_valid(gtin):
    """GTIN-8/12/13/14: dígito verificador módulo 10 (pesos 3 y 1 desde la derecha)."""
    if not re.fullmatch(r"\d{8}|\d{12,14}", gtin or ""):
        return False
    body = gtin[:-1]
    total = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - total % 10) % 10 == int(gtin[-1])


def short_gtin(gtin):
    """GTIN-14 -> la forma impresa: EAN-8 si lleva 6 ceros delante, EAN-13 si lleva uno."""
    return gtin[6:] if gtin.startswith("000000") else gtin[1:] if gtin.startswith("0") else gtin


def prefix_country(gtin):
    g = gtin.zfill(14)
    if g.startswith("000000"):  # EAN-8: otra tabla de prefijos
        return None
    p = int(g[1:4])
    if 20 <= p <= 29 or 40 <= p <= 49 or 200 <= p <= 299:
        return "Uso interno de la tienda"
    return next((name for lo, hi, name in PREFIXES if lo <= p <= hi), None)


def gs1_date(yymmdd):
    """«250131» -> date. DD «00» = último día del mes; el siglo, el más cercano (regla de GS1)."""
    if not re.fullmatch(r"\d{6}", yymmdd or ""):
        return None
    yy, mm, dd = int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:])
    year = 2000 + yy
    if year - date.today().year > 50:
        year -= 100
    if not 1 <= mm <= 12:
        return None
    try:
        return date(year, mm, dd or calendar.monthrange(year, mm)[1])
    except ValueError:
        return None


def parse_element_string(text):
    """«(01)09501101530003(17)250101(10)AB1» o el texto crudo con FNC1 -> [(ai, valor)], o None."""
    text = re.sub(r"^\][A-Za-z]\d", "", text.strip())  # prefijo de simbología: ]C1, ]d2, ]Q3…
    if text.startswith("("):
        pairs = re.findall(r"\((\d{2,4})\)([^(]*)", text)
        if not pairs or "".join(f"({a}){v}" for a, v in pairs) != text:
            return None
        return [(a, v.strip(GS)) for a, v in pairs]
    out, i = [], 0
    while i < len(text):
        if text[i] == GS:
            i += 1
            continue
        ai = next((text[i:i + n] for n in (2, 3, 4) if text[i:i + n] in AIS), None)
        if ai is None and text[i:i + 3] in MEASURES and text[i + 3:i + 4].isdigit():
            ai = text[i:i + 4]
        if ai is None:
            return None
        i += len(ai)
        fixed = AIS[ai][1] if ai in AIS else 6
        if fixed:
            value = text[i:i + fixed]
            if len(value) != fixed:
                return None
        else:
            end = text.find(GS, i)
            value = text[i:end if end >= 0 else len(text)][:AIS[ai][2]]
        out.append((ai, value))
        i += len(value)
    return out or None


def parse_digital_link(text):
    """https://dominio/…/01/<GTIN>[/10/<lote>][/21/<serie>][?17=AAMMDD…] -> [(ai, valor)], o None."""
    url = urlsplit(text.strip())
    if url.scheme not in ("http", "https"):
        return None
    parts = url.path.split("/")
    try:
        i = next(k for k, p in enumerate(parts) if p in ("01", "gtin") and k + 1 < len(parts))
    except StopIteration:
        return None
    gtin = parts[i + 1]
    if not re.fullmatch(r"\d{8}|\d{12,14}", gtin):
        return None
    out = [("01", gtin.zfill(14))]
    rest = parts[i + 2:]
    for k in range(0, len(rest) - 1, 2):
        if rest[k] in ("10", "21", "22", "lot", "ser"):
            out.append(({"lot": "10", "ser": "21"}.get(rest[k], rest[k]), rest[k + 1]))
    for key, value in parse_qsl(url.query):
        if key in AIS or (key[:3] in MEASURES and len(key) == 4):
            out.append((key, value))
    return out


def _measure(ai, value):
    name, unit = MEASURES[ai[:3]]
    decimals = int(ai[3])
    try:
        number = int(value) / 10 ** decimals
    except ValueError:
        return name, value
    return name, (f"{number:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
                  + (f" {unit}" if unit else ""))


def product_result(pairs, source="", today=None):
    today = today or date.today()
    data = dict(pairs)
    gtin = data.get("01", "")
    items, warnings = [], []
    if gtin:
        items.append(("GTIN", short_gtin(gtin)))
        if not gtin_valid(gtin):
            warnings.append("El dígito verificador del GTIN no cuadra: el código puede estar mal leído")
        country = prefix_country(gtin)
        if country:
            items.append(("Registrado en", country))
    expiry = None
    for ai, value in pairs:
        if ai == "01":
            continue
        if ai in DATES:
            d = gs1_date(value)
            items.append((AIS[ai][0], d.strftime("%d/%m/%Y") if d else value))
            if ai in ("17", "15") and d and expiry is None:
                expiry = (ai, d)
        elif ai in AIS:
            items.append((AIS[ai][0], value))
        elif ai[:3] in MEASURES:
            items.append(_measure(ai, value))
    level = "warn"
    if expiry:
        ai, d = expiry
        days = (d - today).days
        if days < 0:
            warnings.append(f"Producto vencido el {d:%d/%m/%Y}" if ai == "17"
                            else f"Pasó la fecha de consumo preferente ({d:%d/%m/%Y})")
            level = "bad" if ai == "17" else "warn"
        elif days <= 30:
            warnings.append("Vence hoy" if days == 0 else f"Vence en {days} día{'s' if days != 1 else ''}")
    actions = []
    if gtin:
        actions.append(("Buscar producto ↗", "open", "https://www.google.com/search?q=" + quote(items[0][1])))
        actions.append(("Ver en GS1 ↗", "open", f"https://id.gs1.org/01/{gtin}"))
    if source.startswith(("http://", "https://")):
        actions.append(("Abrir enlace del fabricante ↗", "open", source))
    head = ("Producto", items[0][1]) if gtin else (items[0] if items else ("Código GS1", source))
    lot = data.get("10")
    subtitle = " · ".join(x for x in (f"Lote {lot}" if lot else "",
                                      f"Vence {expiry[1]:%d/%m/%Y}" if expiry else "") if x) or None
    return Result("product", "Producto · GS1", items, actions, warnings, head, subtitle,
                  warning_level=level)


@register
def parse_gs1(text):
    t = text.strip()
    if re.fullmatch(r"\d{8}|\d{12,14}", t):  # EAN/UPC suelto: solo si el dígito verificador cuadra
        return product_result([("01", t.zfill(14))], t) if gtin_valid(t) else None
    if t.startswith(("http://", "https://")):
        pairs = parse_digital_link(t)  # el dígito verificador evita confundir fechas de una URL con un GTIN
        return product_result(pairs, t) if pairs and gtin_valid(pairs[0][1]) else None
    if not (t.startswith("(") or re.match(r"^(\][A-Za-z]\d)?(01\d{14}|00\d{18})", t)):
        return None
    pairs = parse_element_string(t)
    if not pairs or not any(ai in AIS or ai[:3] in MEASURES for ai, _ in pairs):
        return None
    return product_result(pairs, t)
