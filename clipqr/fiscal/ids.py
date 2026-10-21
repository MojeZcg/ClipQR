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
