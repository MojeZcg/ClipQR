"""Identificadores fiscales de Latinoamérica: validación del dígito verificador y formato para mostrar.

Cada país tiene xxx_valid(valor) -> bool y format_xxx(valor) -> str (devuelve el texto tal cual si no
tiene la forma esperada, para no esconder datos raros al usuario)."""
import re

from clipqr.fiscal.ids import digits


def _mod11(values, weights):
    """Suma ponderada módulo 11; los pesos se aplican de derecha a izquierda y se repiten en ciclo."""
    weights = list(weights)
    total = sum(v * weights[i % len(weights)] for i, v in enumerate(reversed(values)))
    return total % 11


def _clean(s):
    return re.sub(r"[\s.\-/]", "", str(s)).upper()


# ---------------------------------------------------------------- México: RFC

_RFC_CHARS = "0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ Ñ"
_RFC_RE = re.compile(r"^([A-ZÑ&]{3,4})(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([A-Z\d]{2})([A\d])$")
RFC_GENERICOS = {"XAXX010101000", "XEXX010101000"}  # público en general / residente en el extranjero


def rfc_valid(rfc):
    """RFC de 12 (persona moral) o 13 (persona física) caracteres: formato, fecha y dígito verificador
    (pesos 13..2 sobre el RFC rellenado a 13 con un espacio a la izquierda). Los RFC genéricos del SAT
    no cumplen el dígito pero son válidos."""
    r = _clean(rfc)
    if r in RFC_GENERICOS:
        return True
    if not _RFC_RE.match(r):
        return False
    padded = r.rjust(13)
    total = sum(_RFC_CHARS.index(c) * (13 - i) for i, c in enumerate(padded[:12]))
    check = 11 - total % 11
    expected = "0" if check == 11 else "A" if check == 10 else str(check)
    return r[-1] == expected


def format_rfc(rfc):
    return _clean(rfc)


# ---------------------------------------------------------------- Chile: RUT

def rut_valid(rut):
    """RUT/RUN con dígito verificador módulo 11 (pesos 2..7 desde la derecha; 10 -> K, 11 -> 0)."""
    r = _clean(rut)
    if not re.fullmatch(r"\d{1,9}[\dK]", r):
        return False
    check = 11 - _mod11([int(c) for c in r[:-1]], range(2, 8))
    expected = "0" if check == 11 else "K" if check == 10 else str(check)
    return r[-1] == expected


def format_rut(rut):
    """«97975000-5» -> «97.975.000-5»."""
    r = _clean(rut)
    if not re.fullmatch(r"\d{1,9}[\dK]", r):
        return str(rut).strip()
    body = f"{int(r[:-1]):,}".replace(",", ".")
    return f"{body}-{r[-1]}"


# ---------------------------------------------------------------- Perú: RUC

def ruc_pe_valid(ruc):
    """RUC de 11 dígitos (prefijo 10, 15, 16, 17 o 20) con dígito verificador módulo 11
    (pesos 5,4,3,2,7,6,5,4,3,2; 10 -> 0, 11 -> 1)."""
    d = _clean(ruc)
    if not re.fullmatch(r"\d{11}", d) or d[:2] not in ("10", "15", "16", "17", "20"):
        return False
    check = 11 - sum(int(a) * w for a, w in zip(d[:10], (5, 4, 3, 2, 7, 6, 5, 4, 3, 2))) % 11
    return {10: 0, 11: 1}.get(check, check) == int(d[10])


def format_ruc_pe(ruc):
    return _clean(ruc)


# ---------------------------------------------------------------- Colombia: NIT

_NIT_WEIGHTS = (3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71)


def nit_dv(nit):
    """Dígito de verificación DIAN del NIT sin DV (pesos primos desde la derecha)."""
    d = digits(nit)
    if not d or len(d) > 15:
        return None
    r = _mod11([int(c) for c in d], _NIT_WEIGHTS)
    return r if r < 2 else 11 - r


def nit_valid(nit):
    """NIT completo con su dígito de verificación al final («800197268-4» o «8001972684»)."""
    d = digits(nit)
    if len(d) < 6 or len(d) > 16:
        return False
    return nit_dv(d[:-1]) == int(d[-1])


def format_nit(nit, con_dv=False):
    """«800197268» -> «800.197.268»; con con_dv=True el último dígito es el DV: «800.197.268-4»."""
    d = digits(nit)
    if not d or len(d) > 16:
        return str(nit).strip()
    base, dv = (d[:-1], d[-1]) if con_dv else (d, None)
    text = f"{int(base):,}".replace(",", ".") if base else ""
    return f"{text}-{dv}" if dv is not None else text


# ---------------------------------------------------------------- Uruguay: RUC (RUT de DGI)

def ruc_uy_valid(ruc):
    """RUC de 12 dígitos: 2 de departamento (01-21), 6 de número, «001» y dígito verificador módulo 11
    (pesos 4,3,2,9,8,7,6,5,4,3,2; 11 -> 0; 10 no se emite)."""
    d = _clean(ruc)
    if not re.fullmatch(r"\d{12}", d) or not 1 <= int(d[:2]) <= 21 or d[2:8] == "000000" or d[8:11] != "001":
        return False
    check = 11 - sum(int(a) * w for a, w in zip(d[:11], (4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))) % 11
    if check == 10:
        return False
    return (0 if check == 11 else check) == int(d[11])


def format_ruc_uy(ruc):
    return _clean(ruc)


# ---------------------------------------------------------------- Brasil: CPF y CNPJ

def _br_dv(values, weights):
    r = sum(v * w for v, w in zip(values, weights)) % 11
    return 0 if r < 2 else 11 - r


def cpf_valid(cpf):
    """CPF de 11 dígitos con dos dígitos verificadores módulo 11; las secuencias repetidas no valen."""
    d = digits(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    v = [int(c) for c in d]
    return _br_dv(v[:9], range(10, 1, -1)) == v[9] and _br_dv(v[:10], range(11, 1, -1)) == v[10]


def format_cpf(cpf):
    d = digits(cpf)
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}" if len(d) == 11 else str(cpf).strip()


_CNPJ_W1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_CNPJ_W2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def cnpj_valid(cnpj):
    """CNPJ de 14 posiciones con dos dígitos verificadores módulo 11. Acepta el CNPJ alfanumérico
    (las 12 primeras posiciones pueden ser letras, que valen su código ASCII menos 48)."""
    c = _clean(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}\d{2}", c) or c == c[0] * 14:
        return False
    v = [ord(ch) - 48 for ch in c]
    return _br_dv(v[:12], _CNPJ_W1) == v[12] and _br_dv(v[:13], _CNPJ_W2) == v[13]


def format_cnpj(cnpj):
    c = _clean(cnpj)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else str(cnpj).strip()


# ---------------------------------------------------------------- Ecuador: RUC

def _cedula_ec_valid(d):
    """Cédula de 10 dígitos: provincia 01-24 (o 30), tercer dígito < 6 y verificador módulo 10."""
    if not (1 <= int(d[:2]) <= 24 or d[:2] == "30") or int(d[2]) >= 6:
        return False
    total = 0
    for i, c in enumerate(d[:9]):
        p = int(c) * (2 if i % 2 == 0 else 1)
        total += p - 9 if p > 9 else p
    return (10 - total % 10) % 10 == int(d[9])


def ruc_ec_valid(ruc):
    """RUC de 13 dígitos. Persona natural: cédula válida + establecimiento. Sociedad privada (tercer
    dígito 9): módulo 11 con pesos 4,3,2,7,6,5,4,3,2. Entidad pública (tercer dígito 6): módulo 11 con
    pesos 3,2,7,6,5,4,3,2."""
    # TODO verificar con la especificación oficial: el SRI ha emitido RUC de sociedades que no cumplen el
    # módulo 11; por eso los parsers usan este resultado solo para avisar, nunca para descartar.
    d = _clean(ruc)
    if not re.fullmatch(r"\d{13}", d) or not (1 <= int(d[:2]) <= 24 or d[:2] == "30"):
        return False
    third = int(d[2])
    if third < 6:
        return _cedula_ec_valid(d[:10]) and d[10:] != "000"
    if third == 6:
        r = sum(int(a) * w for a, w in zip(d[:8], (3, 2, 7, 6, 5, 4, 3, 2))) % 11
        return (0 if r == 0 else 11 - r) == int(d[8]) and d[9:] != "0000"
    if third == 9:
        r = sum(int(a) * w for a, w in zip(d[:9], (4, 3, 2, 7, 6, 5, 4, 3, 2))) % 11
        return (0 if r == 0 else 11 - r) == int(d[9]) and d[10:] != "000"
    return False


def format_ruc_ec(ruc):
    return _clean(ruc)
