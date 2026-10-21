"""Resultado común de interpretar un código y registro de formatos «estructurados» (facturas, pagos,
productos, documentos…). Cada formato es una función texto -> Result | None que se registra con
@register; analyze() prueba los registrados y, si ninguno lo reconoce, usa los tipos básicos."""
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


@dataclass
class Result:
    kind: str                      # clave de KINDS (color e icono): invoice, payment, link…
    title: str                     # tipo, en pequeño sobre el dato principal: «Factura», «Pago QR»…
    items: list                    # [(etiqueta, valor)] con botón «Copiar» cada uno
    actions: list                  # [(texto del botón, acción, argumento)]; nada se ejecuta sin pulsarlo
    warnings: list = field(default_factory=list)   # franja ámbar: algo no cuadra
    headline: tuple = None         # (etiqueta, valor) del dato en grande; si falta, se elige uno de items
    subtitle: str = None           # línea pequeña bajo el dato principal
    private: bool = False          # datos personales (DNI, embarque): no se guardan en el historial


PARSERS = []


def register(fn):
    PARSERS.append(fn)
    return fn


def detect(text):
    """Primer formato estructurado que reconoce el texto, o None. Un formato que falla no rompe nada."""
    for fn in PARSERS:
        try:
            r = fn(text)
        except Exception:
            r = None
        if r is not None:
            return r
    return None


# ---------------------------------------------------------------- importes

# país -> (separador de miles, separador decimal, decimales)
NUMBER_STYLE = {
    "AR": (".", ",", 2), "ES": (".", ",", 2), "UY": (".", ",", 2), "CO": (".", ",", 2), "BR": (".", ",", 2),
    "CL": (".", ",", 0), "PT": (" ", ",", 2), "DE": (".", ",", 2), "MX": (",", ".", 2), "PE": (",", ".", 2),
    "EC": (",", ".", 2), "CH": ("'", ".", 2), "US": (",", ".", 2),
}
# moneda ISO -> (símbolo, va detrás)
CURRENCY = {
    "ARS": ("$", False), "USD": ("US$", False), "EUR": ("€", True), "BRL": ("R$", False), "MXN": ("$", False),
    "CLP": ("$", False), "PEN": ("S/", False), "COP": ("$", False), "UYU": ("$", False), "CHF": ("CHF", False),
    "GBP": ("£", False), "INR": ("₹", False), "PYG": ("₲", False), "BOB": ("Bs", False),
}


def to_decimal(value):
    """«1234.5», «1.234,50», 1234.5 -> Decimal; None si no es un número."""
    if value is None:
        return None
    s = str(value).strip().replace(" ", "")
    if "," in s and "." in s:  # el último separador es el decimal
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def format_money(amount, currency="ARS", country="AR"):
    """Importe con el formato del país: AR «$ 12.345,67», ES «12.345,67 €», MX «$12,345.67»."""
    amount = to_decimal(amount)
    if amount is None:
        return ""
    thousands, decimal_sep, decimals = NUMBER_STYLE.get(country, (".", ",", 2))
    q = Decimal(1).scaleb(-decimals)
    neg = amount < 0
    digits = f"{abs(amount).quantize(q, rounding=ROUND_HALF_UP):.{decimals}f}"
    whole, _, frac = digits.partition(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    number = thousands.join(groups) + (decimal_sep + frac if decimals else "")
    symbol, after = CURRENCY.get(currency, (currency, True))
    spaced = country not in ("MX", "PE", "EC", "US") or len(symbol) > 1
    text = f"{number} {symbol}" if after else (f"{symbol} {number}" if spaced else f"{symbol}{number}")
    return ("−" if neg else "") + text
