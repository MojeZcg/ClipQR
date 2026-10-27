"""Opciones de línea de órdenes del instalador."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "installer"))
import setup  # noqa: E402


def test_defaults_open_the_wizard_with_autostart():
    assert setup.parse_args([]) == {"silent": False, "autostart": True, "desktop": False, "launch": False}


def test_silent_options_any_prefix_or_case():
    assert setup.parse_args(["/SILENT", "-noautostart", "--desktop", "/launch"]) == {
        "silent": True, "autostart": False, "desktop": True, "launch": True}


def test_unknown_option_is_an_error():
    with pytest.raises(ValueError):
        setup.parse_args(["/quiet"])


def test_language_from_windows_langid():
    assert setup.language_for(0x0C0A) == "es"  # es-ES
    assert setup.language_for(0x2C0A) == "es"  # es-AR
    assert setup.language_for(0x080A) == "es"  # es-MX
    assert setup.language_for(0x0409) == "en"  # en-US
    assert setup.language_for(0x0416) == "pt"  # pt-BR
    assert setup.language_for(0x0413) == "en"  # nl-NL: sin traducción, en inglés


def test_texts_follow_the_language(monkeypatch):
    monkeypatch.setattr(setup, "LANG", "es")
    assert setup.T("Instalar", "Install") == "Instalar"
    assert "/silent" in setup.usage() and "instala" in setup.usage()
    monkeypatch.setattr(setup, "LANG", "en")
    assert setup.T("Instalar", "Install") == "Install"
    assert "/silent" in setup.usage() and "install" in setup.usage()


def test_unknown_option_message_is_translated(monkeypatch):
    monkeypatch.setattr(setup, "LANG", "en")
    with pytest.raises(ValueError, match="Unknown option: quiet"):
        setup.parse_args(["/quiet"])


def test_traducciones_del_instalador_completas():
    """Cada idioma con traducciones tiene todos los textos ingleses de T(es, en)."""
    import ast
    src = open(setup.__file__, encoding="utf-8").read()
    english = {n.args[1].value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)
               and getattr(n.func, "id", None) == "T" and len(n.args) == 2 and isinstance(n.args[1], ast.Constant)}
    for code, texts in setup.TRANSLATIONS.items():
        if texts:
            assert english <= set(texts), (code, sorted(english - set(texts)))
