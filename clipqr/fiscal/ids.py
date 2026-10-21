"""Identificadores fiscales: validación del dígito verificador y formato para mostrar."""
import re


def digits(s):
    return re.sub(r"\D", "", str(s))


# ---------------------------------------------------------------- Argentina: CUIT / CUIL

def cuit_valid(cuit):
    """CUIT/CUIL de 11 dígitos con dígito verificador módulo 11 (pesos 5,4,3,2,7,6,5,4,3,2)."""
    d = digits(cuit)
    if len(d) != 11:
        return False
    total = sum(int(a) * w for a, w in zip(d[:10], (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)))
    check = 11 - total % 11
    if check == 10:  # combinación que no se emite (en su lugar ARCA usa el prefijo 23, que ya cuadra)
        return False
    return (0 if check == 11 else check) == int(d[10])


def format_cuit(cuit):
    d = digits(cuit)
    return f"{d[:2]}-{d[2:10]}-{d[10:]}" if len(d) == 11 else str(cuit)


# ---------------------------------------------------------------- Argentina: CBU / CVU

def cbu_valid(cbu):
    """CBU o CVU de 22 dígitos: dos bloques (8 y 14) con su dígito verificador (pesos 7,1,3,9…)."""
    d = digits(cbu)
    if len(d) != 22 or d != str(cbu).strip():
        return False

    def ok(block):
        weights = (3, 9, 7, 1) if len(block) == 14 else (7, 1, 3, 9)
        total = sum(int(a) * weights[i % 4] for i, a in enumerate(block[:-1]))
        return (10 - total % 10) % 10 == int(block[-1])

    return ok(d[:8]) and ok(d[8:])


# ---------------------------------------------------------------- Brasil: CPF / CNPJ

def cpf_valid(cpf):
    d = digits(cpf)
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for n in (9, 10):
        total = sum(int(a) * w for a, w in zip(d[:n], range(n + 1, 1, -1)))
        if (total * 10 % 11) % 10 != int(d[n]):
            return False
    return True


def cnpj_valid(cnpj):
    d = digits(cnpj)
    if len(d) != 14 or len(set(d)) == 1:
        return False
    for n in (12, 13):
        weights = list(range(n - 7, 1, -1)) + list(range(9, 1, -1))
        total = sum(int(a) * w for a, w in zip(d[:n], weights))
        check = 11 - total % 11
        if (0 if check >= 10 else check) != int(d[n]):
            return False
    return True
