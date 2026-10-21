"""QR de comprobantes de ARCA (ex AFIP)."""
import base64
import json

import pytest

from clipqr.payloads import analyze

# Ejemplo con los mismos campos que la especificación de ARCA; CUIT de AFIP (33-69345023-9)
BASE = {"ver": 1, "fecha": "2025-10-13", "cuit": 33693450239, "ptoVta": 3, "tipoCmp": 6, "nroCmp": 1234,
        "importe": 12345.67, "moneda": "PES", "ctz": 1, "tipoDocRec": 96, "nroDocRec": 12345678,
        "tipoCodAut": "E", "codAut": 74123456789012}


def qr(data=None, host="www.afip.gob.ar", urlsafe=False, pad=True, **changes):
    data = dict(BASE if data is None else data, **changes)
    raw = json.dumps(data).encode()
    p = (base64.urlsafe_b64encode if urlsafe else base64.b64encode)(raw).decode()
    if not pad:
        p = p.rstrip("=")
    return f"https://{host}/fe/qr/?p={p}"


def test_factura_b():
    r = analyze(qr())
    assert r.kind == "invoice" and r.title == "Factura · ARCA"
    assert r.headline == ("Importe", "$ 12.345,67")
    assert r.subtitle == "Factura B · 00003-00001234 · 13/10/2025"
    items = dict(r.items)
    assert items["CUIT emisor"] == "33-69345023-9"
    assert items["DNI receptor"] == "12345678"
    assert items["CAE"] == "74123456789012"
    assert not r.warnings
    labels = [a[0] for a in r.actions]
    assert labels == ["Verificar en ARCA ↗", "Constatar comprobante ↗", "Copiar datos para constatar",
                      "Copiar resumen"]
    datos = r.actions[2][2]
    assert "CUIT emisor: 33693450239" in datos and "Número: 1234" in datos


@pytest.mark.parametrize("tipo, nombre", [(1, "Factura A"), (11, "Factura C"), (3, "Nota de crédito A"),
                                          (51, "Factura M"), (201, "Factura de crédito MiPyME A"),
                                          (999, "Comprobante tipo 999")])
def test_tipos(tipo, nombre):
    assert analyze(qr(tipoCmp=tipo)).subtitle.startswith(nombre)


def test_dolares_con_cotizacion_y_receptor_cuit():
    r = analyze(qr(moneda="DOL", ctz=1450.5, importe=100, tipoDocRec=80, nroDocRec=20172543597))
    items = dict(r.items)
    assert r.headline == ("Importe", "US$ 100,00")
    assert items["Cotización"] == "$ 1.450,50"
    assert items["CUIT receptor"] == "20-17254359-7"


def test_consumidor_final_y_caea():
    r = analyze(qr(tipoDocRec=99, nroDocRec=0, tipoCodAut="A"))
    items = dict(r.items)
    assert items["Receptor"] == "Consumidor final"
    assert "CAEA" in items


@pytest.mark.parametrize("kwargs", [dict(urlsafe=True), dict(pad=False), dict(host="arca.gob.ar"),
                                    dict(host="afip.gob.ar")])
def test_variantes_de_url(kwargs):
    assert analyze(qr(**kwargs)).subtitle.startswith("Factura B")


def test_cuit_alterado():
    r = analyze(qr(cuit=33693450238))
    assert any("CUIT" in w for w in r.warnings)


def test_sin_cae_y_fecha_futura():
    r = analyze(qr(codAut="", fecha="2999-01-01"))
    assert any("CAE" in w for w in r.warnings)
    assert any("futura" in w for w in r.warnings)


@pytest.mark.parametrize("url", ["https://www.afip.gob.ar/fe/qr/?p=no-es-base64!!",
                                 "https://www.afip.gob.ar/fe/qr/",
                                 "https://www.afip.gob.ar/fe/qr/?p=" + base64.b64encode(b"[1,2]").decode()])
def test_qr_roto_avisa_sin_romper(url):
    r = analyze(url)
    assert r.kind == "invoice"
    assert "QR de factura incompleto o modificado" in r.warnings


def test_faltan_campos():
    data = dict(BASE)
    del data["importe"]
    assert "QR de factura incompleto o modificado" in analyze(qr(data)).warnings


@pytest.mark.parametrize("text", ["https://www.afip.gob.ar/", "https://evil.example/fe/qr/?p=e30=",
                                  "hola"])
def test_no_es_arca(text):
    assert analyze(text).kind != "invoice"
