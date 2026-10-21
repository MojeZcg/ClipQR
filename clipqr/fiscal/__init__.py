"""Comprobantes fiscales (facturas) con QR de distintos países.

Cada país es un módulo que registra una función con @register (ver clipqr.structured) y construye un
Comprobante; invoice_result() lo convierte en el Result común que muestra el aviso.
"""
from dataclasses import dataclass, field

from clipqr.structured import Result, format_money


@dataclass
class Comprobante:
    pais: str                     # código ISO: AR, MX, ES…
    sistema: str                  # «ARCA», «SAT (CFDI)», «VeriFactu»…
    tipo: str = "Comprobante"     # «Factura B», «Nota de crédito A»…
    numero: str = ""
    fecha: str = ""               # dd/mm/aaaa
    emisor: str = ""              # identificador fiscal formateado (CUIT, RFC, NIF…)
    emisor_label: str = "Emisor"
    receptor: str = ""
    receptor_label: str = "Receptor"
    importe: object = None        # Decimal o texto numérico
    moneda: str = ""              # ISO 4217
    cotizacion: object = None
    autorizacion: str = ""        # CAE, UUID, CUFE…
    autorizacion_label: str = "Autorización"
    url_verificacion: str = ""
    organismo: str = ""           # para el botón: «Verificar en ARCA»
    extra: list = field(default_factory=list)      # [(etiqueta, valor)] propios del país
    avisos: list = field(default_factory=list)
    acciones: list = field(default_factory=list)   # botones adicionales

    def importe_texto(self):
        return format_money(self.importe, self.moneda or "ARS", self.pais) if self.importe is not None else ""

    def resumen(self):
        """Texto con todos los datos, para pegar en una planilla o en un correo."""
        lines = [f"{self.tipo} {self.numero}".strip(), f"Fecha: {self.fecha}" if self.fecha else ""]
        for label, value in self.items():
            lines.append(f"{label}: {value}")
        if self.url_verificacion:
            lines.append(f"Verificación: {self.url_verificacion}")
        return "\n".join(l for l in lines if l)

    def items(self):
        items = []
        if self.importe is not None:
            items.append(("Importe", self.importe_texto()))
        if self.cotizacion is not None:
            items.append(("Cotización", str(self.cotizacion)))
        for label, value in ((self.emisor_label, self.emisor), (self.receptor_label, self.receptor),
                             ("Número", self.numero), ("Fecha", self.fecha),
                             (self.autorizacion_label, self.autorizacion)):
            if value:
                items.append((label, value))
        return items + list(self.extra)


def invoice_result(c):
    """Comprobante -> Result: importe en grande, «Factura B · 0003-00001234 · 21/10/2026» debajo."""
    actions = []
    if c.url_verificacion:
        actions.append((f"Verificar en {c.organismo or c.sistema} ↗", "open", c.url_verificacion))
    actions += c.acciones
    actions.append(("Copiar resumen", "copy", c.resumen()))
    subtitle = " · ".join(x for x in (c.tipo, c.numero, c.fecha) if x)
    headline = ("Importe", c.importe_texto()) if c.importe is not None else (c.tipo, c.numero or c.tipo)
    return Result("invoice", f"{c.tipo.split()[0] if c.tipo else 'Factura'} · {c.sistema}",
                  [i for i in c.items() if i[0] != "Importe"], actions, list(c.avisos), headline, subtitle)
