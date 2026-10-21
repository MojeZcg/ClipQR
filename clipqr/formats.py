"""Importa todos los formatos estructurados para que se registren (el orden importa: los más específicos
primero). Añadir un país o formato nuevo = crear su módulo e importarlo aquí."""
from clipqr import payments
from clipqr.fiscal import ar_arca  # registran sus formatos

__all__ = ["ar_arca", "payments"]
