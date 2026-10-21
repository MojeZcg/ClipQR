"""DNI argentino y tarjetas de embarque (datos ficticios)."""
from datetime import date

from clipqr.identity import julian_to_date, parse_bcbp
from clipqr.payloads import analyze

DNI_NUEVO = "00123456789@PEREZ@JUAN CARLOS@M@12345678@A@15/03/1990@20/05/2020@200"
DNI_VIEJO = "@12345678    @A@1@PEREZ@JUAN CARLOS@ARGENTINO@15/03/1990@M@20/05/2010@00123456789@7777@20/05/2025@123@0@ILR:2.01 C:110523.01 (No Cap.)@UNIDAD #20 || S/N: 0040>2008>>0006"
# Ejemplo con la estructura de la Resolución 792 de IATA
BCBP = "M1PEREZ/JUAN CARLOS   EABC123 EZEMADAR 1132 294Y012A0045 100"


def test_dni_nuevo():
    r = analyze(DNI_NUEVO)
    items = dict(r.items)
    assert r.kind == "identity" and r.private
    assert r.headline == ("Titular", "Juan Carlos Perez")
    assert items["DNI"] == "12.345.678" and items["Sexo"] == "Masculino"
    assert items["Nacimiento"] == "15/03/1990" and items["Ejemplar"] == "A"
    assert ("Copiar DNI", "copy", "12345678") in r.actions


def test_dni_viejo():
    r = analyze(DNI_VIEJO)
    items = dict(r.items)
    assert r.private and items["DNI"] == "12.345.678" and items["Apellido"] == "Perez"
    assert items["Emisión"] == "20/05/2010"


def test_no_es_dni():
    assert analyze("hola@mundo@x").kind != "identity"
    assert analyze("persona@example.com").kind != "identity"


def test_julian():
    assert julian_to_date(294, date(2026, 10, 21)) == date(2026, 10, 21)
    assert julian_to_date(2, date(2026, 12, 30)) == date(2027, 1, 2)
    assert julian_to_date(360, date(2027, 1, 3)) == date(2026, 12, 26)


def test_tarjeta_de_embarque():
    r = parse_bcbp(BCBP, today=date(2026, 10, 20))
    items = dict(r.items)
    assert r.kind == "boarding" and r.private
    assert r.headline == ("Vuelo", "AR 1132")
    assert items["Pasajero"] == "Juan Carlos Perez" and items["Reserva"] == "ABC123"
    assert items["Asiento"] == "12A" and items["Fecha"] == "21/10/2026" and items["Clase"] == "Turista"
    assert r.subtitle.startswith("EZE → MAD · 21/10/2026")
    assert analyze(BCBP).kind == "boarding"


def test_no_es_embarque():
    assert analyze("M1 hola").kind != "boarding"
    assert analyze("M1" + "x" * 70).kind != "boarding"


def test_privados_fuera_del_historial():
    assert analyze(DNI_NUEVO).private and analyze(BCBP).private
    assert not analyze("https://example.com").private
