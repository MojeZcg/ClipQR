"""Avisos de seguridad de enlaces."""
import pytest

from clipqr.linksafety import link_warnings, registrable_domain


@pytest.mark.parametrize("host, expected", [
    ("github.com", "github.com"),
    ("www.github.com", "github.com"),
    ("login.banco.com.ar", "banco.com.ar"),
    ("afip.gob.ar", "afip.gob.ar"),
    ("www.afip.gob.ar", "afip.gob.ar"),
    ("a.b.c.example.co.uk", "example.co.uk"),
])
def test_registrable_domain(host, expected):
    assert registrable_domain(host) == expected


@pytest.mark.parametrize("url", [
    "https://github.com/MojeZcg/ClipQR",
    "https://www.afip.gob.ar/fe/qr/?p=abc",
    "https://login.banco.com.ar/inicio",
    "https://www.mercadopago.com.ar/home",
])
def test_normal_links_have_no_warnings(url):
    assert link_warnings(url) == []


@pytest.mark.parametrize("url, fragment", [
    ("http://example.com", "no está cifrada"),
    ("https://bit.ly/3abcde", "acortado"),
    ("https://qrco.de/bfXyz", "acortado"),
    ("https://xn--pypal-4ve.com/login", "otros alfabetos"),
    ("https://pаypal.com/login", "otros alfabetos"),  # «а» cirílica
    ("https://192.168.1.20/admin", "dirección IP"),
    ("http://3232235777/", "dirección IP"),
    ("https://banco.com@malo.xyz/login", "destino real es malo.xyz"),
    ("https://banco.com.ar.cuenta-segura.xyz/login", "el dominio real es cuenta-segura.xyz"),
])
def test_suspicious_links(url, fragment):
    assert any(fragment in w for w in link_warnings(url)), link_warnings(url)
