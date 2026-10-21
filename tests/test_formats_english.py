"""Interpretación de los códigos con la interfaz en inglés."""
from datetime import date, timedelta

import pytest

from clipqr import i18n
from clipqr.fiscal import Comprobante, invoice_result
from clipqr.gs1 import product_result
from clipqr.identity import parse_bcbp
from clipqr.payloads import analyze, format_name, headline

PIX = ("00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-4266554400005204000053039865802BR"
       "5913Fulano de Tal6008BRASILIA62070503***63041D3D")
BCBP = "M1PEREZ/JUAN CARLOS   EABC123 EZEMADAR 1132 294Y012A0045 100"


@pytest.fixture(autouse=True)
def english():
    i18n.set_language("en")


def test_wifi():
    r = analyze("WIFI:S:MiCasa;T:WPA;P:clave;;")
    assert r.title == "Wi-Fi"
    assert dict(r.items) == {"Network (SSID)": "MiCasa", "Password": "clave", "Security": "WPA"}
    assert r.actions[0][:2] == ("Connect to network", "wifi")
    assert headline(r.kind, r.items, "") == ("Network (SSID)", "MiCasa")
    assert format_name("QRCode") == "QR code"


def test_contacto_sigue_creando_botones():
    r = analyze("BEGIN:VCARD\nVERSION:3.0\nFN:Ana\nTEL:+34 600 111 222\nURL:example.com\nEND:VCARD")
    assert [a[0] for a in r.actions] == ["Save contact", "Call", "Open website ↗"]
    assert headline(r.kind, r.items, "") == ("Name", "Ana")
    mecard = analyze("MECARD:N:Perez,Ana;TEL:123;;")
    assert "FN:Ana Perez" in mecard.actions[0][2][0] and "TEL:123" in mecard.actions[0][2][0]


def test_enlace():
    r = analyze("https://docs.example.com/guia")
    assert r.title == "Link"
    assert ("Domain", "example.com") in r.items and ("Server", "docs.example.com") in r.items
    assert r.actions[0][0] == "Open link ↗"
    assert analyze("https://www.linkedin.com/company/acme").title == "LinkedIn · company"


def test_producto_vencido():
    r = product_result([("01", "09506000134352"), ("17", "200101"), ("10", "AB1")])
    assert r.title == "Product · GS1"
    assert r.warnings == ["Product expired on 01/01/2020"] and r.warning_level == "bad"
    assert dict(r.items)["Expiry date"] == "01/01/2020"
    assert r.subtitle == "Batch AB1 · Expires 01/01/2020"
    soon = date.today() + timedelta(days=1)
    assert product_result([("01", "09506000134352"), ("17", soon.strftime("%y%m%d"))]).warnings == \
        ["Expires in 1 day"]


def test_pix():
    r = analyze(PIX)
    assert r.title == "QR payment · Pix"
    items = dict(r.items)
    assert items["Payee"] == "Fulano de Tal" and items["Country"] == "Brazil" and "Pix key" in items
    assert r.headline == ("Payee", "Fulano de Tal")
    assert r.subtitle == "No amount: you choose it in the app when paying"
    assert r.actions[0][0] == "Copy payment code" and r.actions[1][0] == "Copy Pix key"


def test_tarjeta_de_embarque():
    r = parse_bcbp(BCBP, today=date(2026, 10, 20))
    assert r.title == "Boarding pass" and r.headline == ("Flight", "AR 1132")
    items = dict(r.items)
    assert items["Passenger"] == "Juan Carlos Perez" and items["Class"] == "Economy" and items["Seat"] == "12A"
    assert r.subtitle == "EZE → MAD · 21/10/2026 · not saved to history"
    assert [a[0] for a in r.actions] == ["Copy booking ref.", "Flight status ↗"]


def test_factura():
    c = Comprobante("AR", "ARCA", "Invoice B", "00003-00001234", "21/10/2026", emisor="20-17254359-7",
                    importe="12345.67", moneda="ARS", autorizacion="74123456789012",
                    url_verificacion="https://example.com/v", organismo="ARCA")
    r = invoice_result(c)
    assert r.title == "Invoice · ARCA"
    assert r.headline == ("Amount", "$ 12.345,67")
    assert r.subtitle == "Invoice B · 00003-00001234 · 21/10/2026"
    assert ("Issuer", "20-17254359-7") in r.items and ("Authorization", "74123456789012") in r.items
    assert all(label != "Amount" for label, _value in r.items)
    assert [a[0] for a in r.actions] == ["Verify with ARCA ↗", "Copy summary"]
    resumen = r.actions[-1][2]
    assert resumen.splitlines()[:2] == ["Invoice B 00003-00001234", "Date: 21/10/2026"]
    assert "Amount: $ 12.345,67" in resumen and "Verification: https://example.com/v" in resumen
    assert "Number:" not in resumen


def test_factura_sin_tipo_ni_importe():
    r = invoice_result(Comprobante("BR", "SEFAZ", numero="123", clase="NFC-e"))
    assert r.title == "NFC-e · SEFAZ" and r.headline == ("Tax document", "123")
