"""Identificadores fiscales de Europa: España (NIF/NIE/CIF) y Portugal (NIF), con su control."""
import re

from clipqr.fiscal.ids import digits

# ---------------------------------------------------------------- España: DNI / NIE / CIF

_LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"   # letra = número mod 23
_LETRAS_CIF = "JABCDEFGHI"                # control en letra: posición = dígito de control


def _clean_es(nif):
    s = re.sub(r"[\s.\-]", "", str(nif)).upper()
    return s[2:] if s.startswith("ES") and len(s) == 11 else s


def dni_valid(dni):
    """DNI: 8 dígitos y letra de control (número mod 23)."""
    s = _clean_es(dni)
    return bool(re.fullmatch(r"\d{8}[A-Z]", s)) and _LETRAS_DNI[int(s[:8]) % 23] == s[8]


def nie_valid(nie):
    """NIE: X, Y o Z (valen 0, 1 y 2), 7 dígitos y letra de control como el DNI."""
    s = _clean_es(nie)
    if not re.fullmatch(r"[XYZ]\d{7}[A-Z]", s):
        return False
    return _LETRAS_DNI[int(str("XYZ".index(s[0])) + s[1:8]) % 23] == s[8]


def _cif_digit(seven):
    """Dígito de control del CIF: suma de las posiciones pares + dígitos del doble de las impares."""
    total = 0
    for i, ch in enumerate(seven):
        n = int(ch)
        if i % 2 == 0:  # posiciones 1, 3, 5 y 7
            n = n * 2
            n = n // 10 + n % 10
        total += n
    return (10 - total % 10) % 10


def cif_valid(cif):
    """CIF / NIF de persona jurídica: letra de entidad, 7 dígitos y control (dígito o letra según la entidad).
    También acepta los NIF especiales K, L y M (letra de control como el DNI sobre los 7 dígitos)."""
    s = _clean_es(cif)
    if re.fullmatch(r"[KLM]\d{7}[A-Z]", s):
        return _LETRAS_DNI[int(s[1:8]) % 23] == s[8]
    if not re.fullmatch(r"[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]", s):
        return False
    d = _cif_digit(s[1:8])
    letra, numero = _LETRAS_CIF[d], str(d)
    if s[0] in "PQRSWN" or s[1:3] == "00":  # entidades públicas, extranjeras o no residentes: letra
        return s[8] == letra
    if s[0] in "ABEH":                       # sociedades: siempre dígito
        return s[8] == numero
    return s[8] in (letra, numero)


def nif_es_valid(nif):
    """Cualquier NIF español: DNI, NIE o CIF (con o sin el prefijo «ES»)."""
    return dni_valid(nif) or nie_valid(nif) or cif_valid(nif)


def format_nif_es(nif):
    """NIF en mayúsculas y sin espacios, puntos ni guiones: «12345678Z», «B12345674»."""
    return _clean_es(nif)


# ---------------------------------------------------------------- Portugal: NIF

def nif_pt_valid(nif):
    """NIF portugués: 9 dígitos, el último de control módulo 11 (pesos 9…2; 10 se escribe 0)."""
    s = re.sub(r"\s", "", str(nif)).upper()
    s = s[2:] if s.startswith("PT") else s
    if not re.fullmatch(r"\d{9}", s):
        return False
    check = 11 - sum(int(a) * w for a, w in zip(s[:8], range(9, 1, -1))) % 11
    return (0 if check >= 10 else check) == int(s[8])


def format_nif_pt(nif):
    d = digits(nif)
    return d if len(d) == 9 else str(nif)
