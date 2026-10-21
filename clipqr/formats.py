"""Importa todos los formatos estructurados para que se registren (el orden importa: los más específicos
primero). Añadir un país o formato nuevo = crear su módulo e importarlo aquí."""
from clipqr import gs1, identity, links, payments
from clipqr.fiscal import ar_arca, es_ticketbai, es_verifactu, pt_atcud  # registran sus formatos
from clipqr.fiscal import br_nfe, cl_sii, co_dian, ec_sri, mx_cfdi, pe_sunat, uy_dgi  # registran sus formatos

__all__ = ["ar_arca", "es_verifactu", "es_ticketbai", "pt_atcud", "mx_cfdi", "cl_sii", "pe_sunat", "co_dian",
           "uy_dgi", "br_nfe", "ec_sri", "payments", "gs1", "identity", "links"]


def load():
    """No hace nada: importar este módulo ya registra los formatos. Existe para que analyze() lo importe
    con un import normal (visible para PyInstaller) sin que pyflakes lo marque como no usado."""
