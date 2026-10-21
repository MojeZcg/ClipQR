"""Interpretación de cada tipo de código: tipo, datos y acciones."""
import pytest

from clipqr.payloads import format_name, headline, parse_payload, shorten


def items_of(text):
    return dict(parse_payload(text)[2])


def actions_of(text):
    return [(label, kind) for label, kind, _ in parse_payload(text)[3]]


@pytest.mark.parametrize("text, kind", [
    ("WIFI:S:MiCasa;T:WPA;P:clave;;", "wifi"),
    ("BEGIN:VCARD\nVERSION:3.0\nFN:Ana\nEND:VCARD", "contact"),
    ("MECARD:N:Perez,Ana;TEL:+34600111222;;", "contact"),
    ("BEGIN:VEVENT\nSUMMARY:Cena\nEND:VEVENT", "event"),
    ("otpauth://totp/ACME:ana?secret=JBSWY3DP&issuer=ACME", "otp"),
    ("mailto:hola@example.com?subject=Hola", "email"),
    ("MATMSG:TO:hola@example.com;SUB:Hola;BODY:Que tal;;", "email"),
    ("tel:+34600111222", "phone"),
    ("SMSTO:+34600111222:Hola", "sms"),
    ("geo:40.4168,-3.7038", "geo"),
    ("https://github.com/MojeZcg/ClipQR", "link"),
    ("www.example.com", "link"),
    ("8410000810004", "product"),
    ("Hola mundo", "text"),
])
def test_kind(text, kind):
    assert parse_payload(text)[0] == kind


def test_wifi_with_escaped_separator():
    items = items_of(r"WIFI:T:WPA;S:Casa\;Oficina;P:cla\;ve\\1;;")
    assert items["Red (SSID)"] == "Casa;Oficina"
    assert items["Contraseña"] == "cla;ve\\1"


def test_wifi_connect_action_has_profile_data():
    _, _, _, actions = parse_payload("WIFI:T:WPA;S:Bar;P:secreto;H:true;;")
    label, kind, arg = actions[0]
    assert (label, kind) == ("Conectar a la red", "wifi")
    assert arg == {"ssid": "Bar", "password": "secreto", "auth": "WPA", "hidden": True}


def test_wifi_without_ssid_has_no_connect_button():
    assert actions_of("WIFI:T:WPA;P:secreto;;") == []


def test_vcard_fields_and_actions():
    text = ("BEGIN:VCARD\nVERSION:3.0\nFN:Ana Pérez\nORG:Estudio\nTEL;TYPE=CELL:+34 600 111 222\n"
            "EMAIL:ana@example.com\nURL:example.com\nADR:;;Calle 1;Madrid;;28001;España\nEND:VCARD")
    items = items_of(text)
    assert items["Nombre"] == "Ana Pérez"
    assert items["Teléfono"] == "+34 600 111 222"
    assert items["Dirección"] == "Calle 1, Madrid, 28001, España"
    labels = [a[0] for a in actions_of(text)]
    assert labels == ["Guardar contacto", "Llamar", "Escribir email", "Abrir web ↗"]
    call = [a for a in parse_payload(text)[3] if a[0] == "Llamar"][0]
    assert call[2] == "tel:+34600111222"


def test_mecard_name_order_and_vcard_export():
    _, _, items, actions = parse_payload("MECARD:N:Perez,Ana;TEL:123;;")
    assert dict(items)["Nombre"] == "Ana Perez"
    content, ext = actions[0][2]
    assert ext == ".vcf" and "FN:Ana Perez" in content


def test_event_wraps_vevent_in_calendar():
    _, _, items, actions = parse_payload("BEGIN:VEVENT\nSUMMARY:Cena\nLOCATION:Madrid\nEND:VEVENT")
    assert dict(items) == {"Evento": "Cena", "Lugar": "Madrid"}
    ics, ext = actions[0][2]
    assert ext == ".ics" and ics.startswith("BEGIN:VCALENDAR")


def test_otp_has_no_actions_and_keeps_secret():
    assert actions_of("otpauth://totp/ACME:ana?secret=JBSWY3DP&issuer=ACME") == []
    assert items_of("otpauth://totp/ACME:ana?secret=JBSWY3DP&issuer=ACME")["Secreto"] == "JBSWY3DP"


def test_matmsg_builds_mailto():
    _, _, _, actions = parse_payload("MATMSG:TO:hola@example.com;SUB:Hola que tal;BODY:Bien;;")
    assert actions[0][2] == "mailto:hola@example.com?subject=Hola%20que%20tal&body=Bien"


def test_geo_opens_map():
    _, _, _, actions = parse_payload("geo:40.4168,-3.7038?z=12")
    assert actions[0][2] == "https://www.google.com/maps?q=40.4168,-3.7038"


def test_free_text_extracts_urls_and_emails():
    items = parse_payload("Escríbeme a ana@example.com o mira https://example.com/x")[2]
    assert ("Email", "ana@example.com") in items and ("URL", "https://example.com/x") in items


def test_long_text_has_no_search_button():
    assert actions_of("x" * 300) == []


@pytest.mark.parametrize("text, expected", [
    ("WIFI:S:MiCasa;T:WPA;P:clave;;", "MiCasa"),
    ("https://docs.example.com/guia", "example.com"),
    ("tel:+34600111222", "+34600111222"),
    ("Hola\nmundo", "Hola"),
])
def test_headline(text, expected):
    kind, _, items, _ = parse_payload(text)
    assert headline(kind, items, text)[1] == expected


def test_shorten():
    assert shorten("a  b\nc", 10) == "a b c"
    assert shorten("abcdefghij", 5) == "abcd…"
    assert shorten("abcdefghij", 7, middle=True) == "abc…hij"


def test_format_name():
    assert format_name("QRCode") == "Código QR"
    assert format_name("Desconocido") == "Desconocido"
