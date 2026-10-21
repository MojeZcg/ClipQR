"""Formulario de «Crear QR» y lectura de la Wi‑Fi actual de Windows."""
from clipqr.actions import parse_wifi_profile
from clipqr.ui.create_qr import FIELDS, TYPES, build_payload


def empty(kind):
    return {k: "" for k, _, _ in FIELDS[kind]}


def test_every_type_has_a_form():
    assert {k for k, _ in TYPES} == set(FIELDS)


def test_empty_form_gives_no_code():
    for kind in FIELDS:
        assert build_payload(kind, empty(kind)) == "", kind


def test_payloads_from_form():
    assert build_payload("text", {"text": "www.example.com"}) == "https://www.example.com"
    assert build_payload("wifi", {"ssid": "Casa", "password": "x"}, "WPA", True) == "WIFI:T:WPA;S:Casa;P:x;H:true;;"
    assert build_payload("whatsapp", {"number": "+54 9 11 1234", "message": ""}) == "https://wa.me/549111234"
    assert build_payload("geo", {"lat": "-34,6037", "lon": "-58,3816"}) == "geo:-34.603700,-58.381600"
    assert build_payload("geo", {"lat": "no", "lon": "1"}) == ""


ES = """
Configuración de seguridad
--------------------------
    Autenticación           : WPA2-Personal
    Cifrado                 : CCMP
    Clave de seguridad      : Presente
    Contenido de la clave   : mi clave: secreta
"""
EN = """
Security settings
-----------------
    Authentication         : WEP
    Key Content            : abcde
"""


def test_parse_wifi_profile_spanish_and_english():
    assert parse_wifi_profile(ES) == ("mi clave: secreta", "WPA")
    assert parse_wifi_profile(EN) == ("abcde", "WEP")
    assert parse_wifi_profile("Authentication : Open") == ("", "nopass")
