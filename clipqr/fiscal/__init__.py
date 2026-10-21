"""Comprobantes fiscales (facturas) con QR de distintos países.

Cada país es un módulo que registra una función con @register (ver clipqr.structured) y construye un
Comprobante; invoice_result() lo convierte en el Result común que muestra el aviso.

Los textos (tipo, etiquetas, avisos) llegan ya traducidos desde cada país. Las etiquetas por defecto quedan
vacías y se traducen al usarlas: los valores por defecto de un dataclass se evalúan al importar, antes de
elegir el idioma.
"""
from dataclasses import dataclass, field

from clipqr.i18n import _
from clipqr.structured import Result, format_money


@dataclass
class Comprobante:
    pais: str                     # código ISO: AR, MX, ES…
    sistema: str                  # «ARCA», «SAT (CFDI)», «VeriFactu»…
    tipo: str = ""                # «Factura B», «Nota de crédito A»… (vacío: «Comprobante»)
    numero: str = ""
    fecha: str = ""               # dd/mm/aaaa
    emisor: str = ""              # identificador fiscal formateado (CUIT, RFC, NIF…)
    emisor_label: str = ""        # vacío: «Emisor»
    receptor: str = ""
    receptor_label: str = ""      # vacío: «Receptor»
    importe: object = None        # Decimal o texto numérico
    moneda: str = ""              # ISO 4217
    cotizacion: object = None
    autorizacion: str = ""        # CAE, UUID, CUFE…
    autorizacion_label: str = ""  # vacío: «Autorización»
    url_verificacion: str = ""
    organismo: str = ""           # para el botón: «Verificar en ARCA»
    extra: list = field(default_factory=list)      # [(etiqueta, valor)] propios del país
    avisos: list = field(default_factory=list)
    acciones: list = field(default_factory=list)   # botones adicionales
    clase: str = ""               # palabra corta para el título («Factura», «Boleta»…); si falta, la 1.ª del tipo

    def importe_texto(self):
        return format_money(self.importe, self.moneda or "ARS", self.pais) if self.importe is not None else ""

    def tipo_texto(self):
        return self.tipo or _("Comprobante")

    def _rows(self):
        """[(clave, etiqueta, valor)]: la clave interna no depende del idioma de la etiqueta."""
        rows = []
        if self.importe is not None:
            rows.append(("importe", _("Importe"), self.importe_texto()))
        if self.cotizacion is not None:
            rows.append(("cotizacion", _("Cotización"), str(self.cotizacion)))
        for key, label, value in (("emisor", self.emisor_label or _("Emisor"), self.emisor),
                                  ("receptor", self.receptor_label or _("Receptor"), self.receptor),
                                  ("numero", _("Número"), self.numero), ("fecha", _("Fecha"), self.fecha),
                                  ("autorizacion", self.autorizacion_label or _("Autorización"), self.autorizacion)):
            if value:
                rows.append((key, label, value))
        return rows + [("extra", label, value) for label, value in self.extra]

    def resumen(self):
        """Texto con todos los datos, para pegar en una planilla o en un correo."""
        lines = [f"{self.tipo_texto()} {self.numero}".strip(), f"{_('Fecha')}: {self.fecha}" if self.fecha else ""]
        for key, label, value in self._rows():
            if key not in ("numero", "fecha"):  # ya van en las dos primeras líneas
                lines.append(f"{label}: {value}")
        if self.url_verificacion:
            lines.append(f"{_('Verificación')}: {self.url_verificacion}")
        return "\n".join(l for l in lines if l)

    def items(self):
        return [(label, value) for _key, label, value in self._rows()]


def _clase(tipo):
    """«Nota de crédito A» -> «Nota de crédito», «Credit note B» -> «Credit note»: el tipo sin la letra
    de clase, para el título pequeño (antes era solo la 1.ª palabra, que en inglés daba «Credit»)."""
    words = tipo.split()
    while len(words) > 1 and len(words[-1]) <= 2:
        words.pop()
    return " ".join(words[:3]) or _("Factura")


def invoice_result(c):
    """Comprobante -> Result: importe en grande, «Factura B · 0003-00001234 · 21/10/2026» debajo."""
    actions = []
    if c.url_verificacion:
        actions.append((_("Verificar en {organismo} ↗", organismo=c.organismo or c.sistema), "open",
                        c.url_verificacion))
    actions += c.acciones
    actions.append((_("Copiar resumen"), "copy", c.resumen()))
    tipo = c.tipo_texto()
    subtitle = " · ".join(x for x in (tipo, c.numero, c.fecha) if x)
    headline = (_("Importe"), c.importe_texto()) if c.importe is not None else (tipo, c.numero or tipo)
    clase = c.clase or _clase(tipo)
    return Result("invoice", f"{clase} · {c.sistema}",
                  [(label, value) for key, label, value in c._rows() if key != "importe"], actions,
                  list(c.avisos), headline, subtitle)
