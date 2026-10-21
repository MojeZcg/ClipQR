"""Base común de formatos estructurados: importes por país, CUIT, comprobantes y registro."""
from decimal import Decimal

import pytest

from clipqr import structured
from clipqr.fiscal import Comprobante, invoice_result
from clipqr.fiscal.ids import cuit_valid, format_cuit
from clipqr.payloads import analyze, parse_payload
from clipqr.structured import Result, format_money, to_decimal


@pytest.mark.parametrize("amount, currency, country, expected", [
    ("12345.67", "ARS", "AR", "$ 12.345,67"),
    ("100", "USD", "AR", "US$ 100,00"),
    ("12345.67", "EUR", "ES", "12.345,67 €"),
    ("12345.67", "MXN", "MX", "$12,345.67"),
    ("12345.5", "CLP", "CL", "$ 12.346"),
    ("1234.5", "PEN", "PE", "S/ 1,234.50"),
    ("1234567.891", "BRL", "BR", "R$ 1.234.567,89"),
    ("-50", "ARS", "AR", "−$ 50,00"),
    ("0.5", "ARS", "AR", "$ 0,50"),
])
def test_format_money(amount, currency, country, expected):
    assert format_money(amount, currency, country) == expected


@pytest.mark.parametrize("text, expected", [
    ("1234.5", Decimal("1234.5")), ("1.234,50", Decimal("1234.50")), ("1,234.50", Decimal("1234.50")),
    ("12,5", Decimal("12.5")), ("abc", None), (None, None), (100, Decimal("100")),
])
def test_to_decimal(text, expected):
    assert to_decimal(text) == expected


@pytest.mark.parametrize("cuit, ok", [
    ("20-17254359-7", True), ("30-71519344-9", True), ("33-69345023-9", True),  # el último: CUIT de AFIP
    ("30-71519344-0", False), ("23-10000017-9", False),
    ("20172543597", True), ("20-17254359-6", False), ("2017254359", False), ("", False),
])
def test_cuit(cuit, ok):
    assert cuit_valid(cuit) is ok


def test_format_cuit():
    assert format_cuit("20172543597") == "20-17254359-7"


def test_invoice_result_shape():
    c = Comprobante("AR", "ARCA", "Factura B", "00003-00001234", "21/10/2026", emisor="20-17254359-7",
                    emisor_label="CUIT emisor", importe="12345.67", moneda="ARS", autorizacion="74123456789012",
                    autorizacion_label="CAE", url_verificacion="https://example.com/v", organismo="ARCA")
    r = invoice_result(c)
    assert r.kind == "invoice"
    assert r.headline == ("Importe", "$ 12.345,67")
    assert r.subtitle == "Factura B · 00003-00001234 · 21/10/2026"
    assert ("CAE", "74123456789012") in r.items
    labels = [a[0] for a in r.actions]
    assert labels[0] == "Verificar en ARCA ↗" and labels[-1] == "Copiar resumen"
    resumen = r.actions[-1][2]
    assert "Importe: $ 12.345,67" in resumen and "CAE: 74123456789012" in resumen


def test_registered_format_wins_and_errors_are_ignored(monkeypatch):
    def broken(text):
        raise ValueError("formato roto")

    def fake(text):
        return Result("invoice", "Prueba", [("A", "1")], []) if text.startswith("PRUEBA:") else None

    monkeypatch.setattr(structured, "PARSERS", [broken, fake])
    assert analyze("PRUEBA:123").title == "Prueba"
    assert analyze("https://example.com").kind == "link"  # los tipos básicos siguen funcionando


def test_parse_payload_is_the_short_form_of_analyze():
    r = analyze("WIFI:S:Casa;T:WPA;P:x;;")
    assert parse_payload("WIFI:S:Casa;T:WPA;P:x;;") == (r.kind, r.title, r.items, r.actions)


def test_link_warnings_come_with_analyze():
    assert analyze("http://bit.ly/x").warnings
