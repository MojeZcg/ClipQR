"""La interfaz en inglés: atajos, avisos de enlaces y textos de la app."""
import pytest

from clipqr import i18n, settings
from clipqr.i18n import _
from clipqr.linksafety import link_warnings
from clipqr.ui.create_qr import COLORS, FIELDS, TYPES


@pytest.fixture
def english():
    i18n.set_language("en")
    yield
    i18n.set_language("es")


def test_idioma_por_defecto_automatico():
    assert settings.DEFAULT_SETTINGS["language"] == "auto"


def test_atajos_en_ingles(english):
    assert settings.hotkey_label("Ctrl+Shift+Space") == "Ctrl+Shift+Space"
    assert settings.hotkey_label("") == "Off"
    assert [_(label) for _key, label in settings.POSITIONS][0] == "Top right"


def test_atajos_en_espanol():
    assert settings.hotkey_label("Ctrl+Shift+Space") == "Ctrl+Shift+Espacio"
    assert settings.hotkey_label("") == "Desactivado"


def test_avisos_de_enlaces_en_ingles(english):
    assert link_warnings("http://example.com") == ["The connection isn't encrypted (http)."]
    assert link_warnings("https://bit.ly/abc") == ["Shortened link: you can't tell where it goes until you open it."]
    assert any("real destination is evil.com" in w for w in link_warnings("https://banco.com@evil.com/"))


def test_crear_qr_en_ingles(english):
    assert dict((k, _(n)) for k, n in TYPES)["text"] == "Text or link"
    assert [_(t) for _k, t, _m in FIELDS["wifi"]] == ["Network name", "Password"]
    assert _(COLORS[0][0]) == "Black"


def test_textos_con_variables_en_ingles(english, tmp_path, monkeypatch):
    assert _("{n} códigos detectados", n=3) == "3 codes detected"
    assert _("Tienes la última versión ({version}).", version="9.9") == "You have the latest version (9.9)."
    monkeypatch.setattr(settings, "ERROR_LOG", str(tmp_path / "no-existe.log"))
    assert "(no errors logged)" in settings.error_report("1.0.0")


def test_aviso_al_iniciar_activado_por_defecto():
    from clipqr.settings import DEFAULT_SETTINGS
    assert DEFAULT_SETTINGS["startup_notice"] is True
