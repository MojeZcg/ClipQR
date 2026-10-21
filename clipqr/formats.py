"""Importa todos los formatos estructurados para que se registren (el orden importa: los más específicos
primero). Añadir un país o formato nuevo = crear su módulo e importarlo aquí."""
from clipqr import gs1, payments
from clipqr.fiscal import ar_arca, es_ticketbai, es_verifactu, pt_atcud  # registran sus formatos

__all__ = ["ar_arca", "es_verifactu", "es_ticketbai", "pt_atcud", "payments", "gs1"]
