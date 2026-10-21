"""Productos GS1: GTIN, Digital Link, cadenas de AI y vencimientos."""
from datetime import date, timedelta

import pytest

from clipqr.gs1 import gs1_date, gtin_valid, parse_digital_link, parse_element_string, product_result
from clipqr.payloads import analyze

GTIN = "09506000134352"  # ejemplo de la documentación de GS1


@pytest.mark.parametrize("gtin, ok", [(GTIN, True), ("9506000134352", True), ("4006381333931", True),
                                      ("96385074", True), ("036000291452", True), ("4006381333932", False),
                                      ("12345", False)])
def test_gtin(gtin, ok):
    assert gtin_valid(gtin) is ok


def test_gs1_date():
    assert gs1_date("250131") == date(2025, 1, 31)
    assert gs1_date("250200") == date(2025, 2, 28)  # día 00 = fin de mes
    assert gs1_date("251301") is None


def test_element_string_con_parentesis():
    pairs = parse_element_string("(01)09506000134352(17)301231(10)ABC123")
    assert pairs == [("01", GTIN), ("17", "301231"), ("10", "ABC123")]


def test_element_string_crudo_con_fnc1():
    raw = "]d20109506000134352" + "10LOTE7\x1d" + "17301231" + "21SER9"
    assert parse_element_string(raw) == [("01", GTIN), ("10", "LOTE7"), ("17", "301231"), ("21", "SER9")]


def test_digital_link():
    pairs = parse_digital_link("https://id.gs1.org/01/09506000134352/10/ABC/21/123?17=301231")
    assert pairs == [("01", GTIN), ("10", "ABC"), ("21", "123"), ("17", "301231")]


def test_producto_completo():
    r = analyze("(01)09506000134352(17)301231(10)ABC123(3103)001250")
    items = dict(r.items)
    assert r.kind == "product" and r.title == "Producto · GS1"
    assert r.headline == ("Producto", "9506000134352")
    assert r.subtitle == "Lote ABC123 · Vence 31/12/2030"
    assert items["Vencimiento"] == "31/12/2030" and items["Peso neto"] == "1,250 kg"
    assert "Registrado en" not in items  # prefijo 950: la oficina global de GS1, no un país
    assert not r.warnings


def test_vencido_es_rojo():
    r = product_result([("01", GTIN), ("17", "200101")])
    assert r.warnings == ["Producto vencido el 01/01/2020"] and r.warning_level == "bad"


def test_vence_pronto():
    soon = date.today() + timedelta(days=10)
    r = product_result([("01", GTIN), ("17", soon.strftime("%y%m%d"))])
    assert r.warnings == ["Vence en 10 días"] and r.warning_level == "warn"


def test_ean_suelto():
    r = analyze("7790070410122")
    assert r.kind == "product" and dict(r.items)["Registrado en"] == "Argentina"
    assert analyze("7790070410123").title == "Producto"  # dígito mal: queda el tipo básico


def test_gtin_mal_leido_avisa():
    assert analyze("(01)09506000134353").warnings


@pytest.mark.parametrize("text", ["https://example.com/01/abc", "(99)hola", "0123", "https://example.com/"])
def test_no_es_gs1(text):
    assert analyze(text).title != "Producto · GS1"
