"""Facturas de España (VeriFactu, TicketBAI) y Portugal (ATCUD), y validación de NIF/NIE/CIF y NIF portugués.

Los ejemplos válidos son los de la documentación oficial (AEAT, especificaciones TicketBAI y AT); sus NIF son
ficticios de prueba con el control correcto.
"""
import pytest

from clipqr.fiscal.es_ticketbai import crc8, parse_ticketbai
from clipqr.fiscal.es_verifactu import parse_verifactu
from clipqr.fiscal.ids_europe import (cif_valid, dni_valid, format_nif_es, format_nif_pt, nie_valid, nif_es_valid,
                                      nif_pt_valid)
from clipqr.fiscal.pt_atcud import parse_atcud
from clipqr.payloads import analyze

INCOMPLETO = "QR de factura incompleto o modificado"

# AEAT, «Características del QR y especificaciones del servicio de cotejo», apartado 8
VF_PROD = ("https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR?nif=89890001K&numserie=12345678-G33"
           "&fecha=01-09-2024&importe=241.4")
VF_PRUEBAS = VF_PROD.replace("www2.agenciatributaria.gob.es", "prewww2.aeat.es")
VF_NO_VERIFACTU = VF_PROD.replace("ValidarQR?", "ValidarQRNoVerifactu?")

# Especificaciones TicketBAI v1.1, apartado 4.3.3
TBAI = "https://batuz.eus/QRTBAI/?id=TBAI-00000006Y-251019-btFpwP8dcLGAF-237&s=T&nf=27174&i=4.70&cr=007"

# AT, «Especificações Técnicas — Código QR», exemplo 2 (fatura simplificada) y 5 (cliente de Francia)
PT_FS = ("A:123456789*B:999999990*C:PT*D:FS*E:N*F:20190812*G:FS CDVF/12345*H:CDF7T5HD-12345*I1:PT"
         "*I7:0.65*I8:0.15*N:0.15*O:0.80*Q:YhGV*R:9999*S:NU;0.80")
PT_FR = ("A:123456789*B:4443332215*C:FR*D:FT*E:N*F:20190526*G:ABC BNH/4561*H:DK5ZJ2HN-4561*I1:FR"
         "*I7:100.00*I8:20.00*N:20.00*O:120.00*Q:YJRE*R:9999")


def items(r):
    return dict(r.items)


# ---------------------------------------------------------------- validadores

@pytest.mark.parametrize("nif, ok", [
    ("12345678Z", True), ("00000006Y", True), ("89890001K", True), ("12345678-z", True), ("ES12345678Z", True),
    ("12345678A", False), ("1234567Z", False), ("", False),
])
def test_dni(nif, ok):
    assert dni_valid(nif) is ok


@pytest.mark.parametrize("nie, ok", [
    ("X1234567L", True), ("Y1234567X", True), ("Z1234567R", True), ("X1234567A", False), ("W1234567L", False),
])
def test_nie(nie, ok):
    assert nie_valid(nie) is ok


@pytest.mark.parametrize("cif, ok", [
    ("B12345674", True), ("A12345674", True), ("P1234567D", True), ("G12345674", True), ("G1234567D", True),
    ("B1234567D", False),   # sociedades: el control es un dígito
    ("P12345674", False),   # entidades públicas: el control es una letra
    ("B12345675", False), ("I12345674", False),
])
def test_cif(cif, ok):
    assert cif_valid(cif) is ok


def test_nif_es_acepta_dni_nie_y_cif():
    assert all(nif_es_valid(x) for x in ("12345678Z", "X1234567L", "B12345674"))
    assert not nif_es_valid("B12345675")
    assert format_nif_es(" b-12345674 ") == "B12345674"


@pytest.mark.parametrize("nif, ok", [
    ("123456789", True), ("500000000", True), ("999999990", True), ("PT123456789", True), ("123 456 789", True),
    ("123456788", False), ("12345678", False), ("abc", False),
])
def test_nif_pt(nif, ok):
    assert nif_pt_valid(nif) is ok


def test_format_nif_pt():
    assert format_nif_pt("PT 123 456 789") == "123456789"


# ---------------------------------------------------------------- VeriFactu

def test_verifactu_valido():
    r = parse_verifactu(VF_PROD)
    assert r.kind == "invoice" and r.title == "Factura · VeriFactu"
    assert r.headline == ("Importe", "241,40 €")
    assert r.subtitle == "Factura · 12345678-G33 · 01/09/2024"
    d = items(r)
    assert d["NIF emisor"] == "89890001K" and d["Número"] == "12345678-G33"
    assert r.warnings == []
    assert ("Comprobar en la AEAT ↗", "open", VF_PROD) in r.actions


def test_verifactu_entorno_de_pruebas():
    assert "QR del entorno de pruebas de la AEAT" in parse_verifactu(VF_PRUEBAS).warnings


def test_verifactu_no_verificable():
    r = parse_verifactu(VF_NO_VERIFACTU)
    assert items(r)["Modalidad"] == "Sistema no VERI*FACTU" and r.warnings == []


def test_verifactu_nif_alterado():
    r = parse_verifactu(VF_PROD.replace("89890001K", "89890001J"))
    assert any("NIF" in w for w in r.warnings)


def test_verifactu_fecha_futura():
    r = parse_verifactu(VF_PROD.replace("01-09-2024", "01-09-2099"))
    assert "La fecha de la factura es posterior a hoy" in r.warnings


@pytest.mark.parametrize("url", [
    VF_PROD.split("&importe")[0],                       # falta el importe
    VF_PROD.replace("importe=241.4", "importe=7,2"),    # coma decimal (error 2005 de la AEAT)
    VF_PROD.replace("01-09-2024", "2024-09-01"),
    VF_PROD.replace("12345678-G33", "12345678&G33"),    # «&» sin codificar (ejemplo erróneo de la AEAT)
    "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR",
    "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR?nif=891K&numserie=%%&fecha=99-99-9999",
])
def test_verifactu_mal_formado_avisa_sin_fallar(url):
    r = parse_verifactu(url)
    assert r is not None and INCOMPLETO in r.warnings


def test_verifactu_en_otro_dominio_no_ofrece_abrirlo():
    r = parse_verifactu(VF_PROD.replace("www2.agenciatributaria.gob.es", "aeat-cotejo.example.com"))
    assert any("no es de la AEAT" in w for w in r.warnings)
    assert all(a[1] != "open" for a in r.actions)


@pytest.mark.parametrize("text", [
    "https://www2.agenciatributaria.gob.es/", "https://example.com/?nif=89890001K&importe=1", "hola",
    "https://sede.agenciatributaria.gob.es/Sede/inicio.html",
])
def test_verifactu_ignora_otros_textos(text):
    assert parse_verifactu(text) is None


# ---------------------------------------------------------------- TicketBAI

def test_crc8_del_anexo():
    assert crc8("TBAI-00000006Y-251019-btFpwP8dcLGAF-") == "237"
    assert crc8(TBAI.split("&cr=")[0]) == "007"


def test_ticketbai_valido():
    r = parse_ticketbai(TBAI)
    assert r.title == "Factura · TicketBAI"
    assert r.headline == ("Importe", "4,70 €")
    d = items(r)
    assert d["NIF emisor"] == "00000006Y" and d["Número"] == "T-27174" and d["Fecha"] == "25/10/2019"
    assert d["Territorio"] == "Bizkaia"
    assert d["Identificador TicketBAI"] == "TBAI-00000006Y-251019-btFpwP8dcLGAF-237"
    assert r.warnings == []
    assert ("Comprobar en Hacienda Foral ↗", "open", TBAI) in r.actions


@pytest.mark.parametrize("host, territorio", [
    ("https://ticketbai.araba.eus/TBAI/QRTBAI", "Álava"), ("https://tbai.egoitza.gipuzkoa.eus/qr/", "Gipuzkoa"),
])
def test_ticketbai_territorios(host, territorio):
    base = f"{host}?id=TBAI-00000006Y-251019-btFpwP8dcLGAF-237&s=T&nf=27174&i=4.70"
    r = parse_ticketbai(f"{base}&cr={crc8(base)}")
    assert items(r)["Territorio"] == territorio and r.warnings == []


def test_ticketbai_importe_alterado():
    r = parse_ticketbai(TBAI.replace("i=4.70", "i=47.00"))
    assert any("QR de TicketBAI alterado" in w for w in r.warnings)


def test_ticketbai_identificador_alterado():
    r = parse_ticketbai(TBAI.replace("btFpwP8dcLGAF", "btFpwP8dcLGAX"))
    assert any("QR de TicketBAI alterado" in w for w in r.warnings)


def test_ticketbai_nif_alterado():
    # NIF con letra incorrecta pero CRC recalculados: el QR es coherente, el NIF no
    ident = "TBAI-00000006X-251019-btFpwP8dcLGAF-"
    ident += crc8(ident)
    base = f"https://batuz.eus/QRTBAI/?id={ident}&s=T&nf=27174&i=4.70"
    r = parse_ticketbai(f"{base}&cr={crc8(base)}")
    assert any("NIF" in w for w in r.warnings)
    assert not any("alterado" in w for w in r.warnings)


@pytest.mark.parametrize("url", [
    "https://batuz.eus/QRTBAI/",
    "https://batuz.eus/QRTBAI/?id=TBAI-roto&s=T&nf=1&i=x&cr=abc",
    TBAI.split("&cr=")[0],
    TBAI.replace("251019", "321319"),
])
def test_ticketbai_mal_formado_avisa_sin_fallar(url):
    r = parse_ticketbai(url)
    assert r is not None and r.warnings


def test_ticketbai_en_otro_dominio_no_ofrece_abrirlo():
    r = parse_ticketbai(TBAI.replace("batuz.eus/QRTBAI", "batuz-eus.example.com/QRTBAI"))
    assert any("Hacienda Foral" in w for w in r.warnings)
    assert all(a[1] != "open" for a in r.actions)


@pytest.mark.parametrize("text", ["https://batuz.eus/", "https://example.com/?id=123", "TBAI-00000006Y", ""])
def test_ticketbai_ignora_otros_textos(text):
    assert parse_ticketbai(text) is None


# ---------------------------------------------------------------- Portugal (ATCUD)

def test_atcud_fatura_simplificada():
    r = parse_atcud(PT_FS)
    assert r.title == "Factura · AT Portugal"
    assert r.headline == ("Importe", "0,80 €")
    assert r.subtitle == "Factura simplificada · FS CDVF/12345 · 12/08/2019"
    d = items(r)
    assert d["NIF emisor"] == "123456789" and d["NIF adquirente"] == "Consumidor final"
    assert d["ATCUD"] == "CDF7T5HD-12345" and d["Total de impuestos"] == "0,15 €"
    assert r.warnings == []
    assert [a[0] for a in r.actions] == ["Copiar resumen"]


def test_atcud_cliente_extranjero():
    r = parse_atcud(PT_FR)
    assert items(r)["NIF adquirente"] == "4443332215 (FR)"
    assert r.headline == ("Importe", "120,00 €") and r.warnings == []


def test_atcud_importe_con_separador_de_miles_pt():
    r = parse_atcud(PT_FS.replace("O:0.80", "O:513600.58"))
    assert r.headline == ("Importe", "513 600,58 €")


def test_atcud_nif_alterado():
    r = parse_atcud(PT_FS.replace("A:123456789", "A:123456788"))
    assert any("NIF del emisor" in w for w in r.warnings)


def test_atcud_documento_anulado():
    assert "Documento anulado" in parse_atcud(PT_FS.replace("E:N", "E:A")).warnings


@pytest.mark.parametrize("text", [
    "A:123456789*B:999999990*C:PT",
    PT_FS.replace("F:20190812", "F:2019-08-12"),
    PT_FS.replace("O:0.80", "O:0,80"),
    PT_FS.replace("*H:CDF7T5HD-12345", ""),
    "A:*B:*C:*D:*E:*F:*G:*H:*N:*O:*Q:*R:",
])
def test_atcud_mal_formado_avisa_sin_fallar(text):
    r = parse_atcud(text)
    assert r is not None and INCOMPLETO in r.warnings


@pytest.mark.parametrize("text", ["A:1", "B:123456789*A:1*C:PT", "hola*B:x", "https://example.com"])
def test_atcud_ignora_otros_textos(text):
    assert parse_atcud(text) is None


# ---------------------------------------------------------------- registro

@pytest.mark.parametrize("text, title", [
    (VF_PROD, "Factura · VeriFactu"), (TBAI, "Factura · TicketBAI"), (PT_FS, "Factura · AT Portugal"),
])
def test_analyze_reconoce_los_formatos(text, title):
    assert analyze(text).title == title


def test_analyze_sigue_reconociendo_enlaces_normales():
    assert analyze("https://example.com/factura?id=1").kind == "link"
