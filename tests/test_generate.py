"""Crear QR: cada tipo se arma, se dibuja, se vuelve a leer y se interpreta con los mismos datos."""
import pytest

from clipqr import generate as g
from clipqr.icons import make_icon
from clipqr.payloads import parse_payload

CASES = [
    ("wifi", g.build_wifi("Casa;Oficina", 'cla\\ve:"1"', "WPA"), {"Red (SSID)": "Casa;Oficina", "Contraseña": 'cla\\ve:"1"'}),
    ("wifi", g.build_wifi("Libre"), {"Red (SSID)": "Libre"}),
    ("contact", g.build_vcard("Ana Pérez", "+54 9 11 1234-5678", "ana@example.com", "Estudio, S.A."),
     {"Nombre": "Ana Pérez", "Teléfono": "+54 9 11 1234-5678", "Email": "ana@example.com", "Empresa": "Estudio, S.A."}),
    ("email", g.build_email("hola@example.com", "Asunto con ñ", "Línea 1"),
     {"Email": "hola@example.com", "Asunto": "Asunto con ñ", "Mensaje": "Línea 1"}),
    ("phone", g.build_tel("+54 (11) 1234-5678"), {"Número": "+541112345678"}),
    ("sms", g.build_sms("+541112345678", "Hola"), {"Número": "+541112345678", "Mensaje": "Hola"}),
    ("geo", g.build_geo("-34.603722", "-58.381592"), {"Coordenadas": "-34.603722,-58.381592"}),
    ("link", g.build_url("www.example.com"), {"Dominio": "example.com"}),
]


@pytest.mark.parametrize("kind, text, expected", CASES)
def test_build_and_parse_roundtrip(kind, text, expected):
    got_kind, _, items, _ = parse_payload(text)
    assert got_kind == kind
    assert expected.items() <= dict(items).items()


@pytest.mark.parametrize("kind, text, expected", CASES)
def test_generated_image_scans_back(kind, text, expected):
    assert g.verify(g.make_qr(text), text)


def test_whatsapp_link():
    assert g.build_whatsapp("+54 9 11 1234-5678", "Hola qué tal") == "https://wa.me/5491112345678?text=Hola%20qu%C3%A9%20tal"


@pytest.mark.parametrize("ec", g.EC_LEVELS)
def test_every_error_correction_level_scans(ec):
    assert g.verify(g.make_qr("https://github.com/MojeZcg/ClipQR", ec_level=ec), "https://github.com/MojeZcg/ClipQR")


def test_logo_in_the_middle_still_scans():
    img = g.make_qr("https://github.com/MojeZcg/ClipQR", logo=make_icon(size=128))
    assert g.verify(img, "https://github.com/MojeZcg/ClipQR")


def test_colors_and_contrast():
    img = g.make_qr("color", fg="#1e3a8a", bg="#fef3c7")
    assert img.getpixel((0, 0)) == (0xfe, 0xf3, 0xc7)  # margen = fondo
    assert g.verify(img, "color")
    assert g.contrast_ratio("#000000", "#ffffff") == pytest.approx(21)
    assert g.contrast_ratio("#777777", "#888888") < 2


def test_svg_export():
    svg = g.make_svg("svg")
    assert svg.lstrip().startswith("<?xml") and "<svg" in svg
