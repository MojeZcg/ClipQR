"""Idiomas de la interfaz: español (el del código) e inglés.

Los textos se escriben en español dentro de _("…") y ese mismo texto es la clave del catálogo inglés
(clipqr/locale/en_*.py). Con variables: _("Vence en {n} días", n=3) — las llaves se rellenan después de
traducir, así el traductor ve la frase entera. Los textos que se definen al importar un módulo (tablas,
constantes) se marcan con N_("…"), que no traduce, y se traducen con _() al mostrarlos.
"""
import ctypes

from clipqr.locale import en_app, en_fiscal, en_formats

LANGUAGES = {"es": "Español", "en": "English"}
CATALOGS = {"en": {**en_app.EN, **en_formats.EN, **en_fiscal.EN}}

_lang = "es"


def windows_language():
    """«es» si Windows está en español; si no, «en» (el inglés se entiende en más sitios)."""
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except (AttributeError, OSError):
        return "en"
    return "es" if lang_id & 0x3FF == 0x0A else "en"


def set_language(code):
    """«auto», «es» o «en»."""
    global _lang
    _lang = windows_language() if code in (None, "", "auto") else code if code in LANGUAGES else "es"
    return _lang


def language():
    return _lang


def _(text, **values):
    """Texto en el idioma activo; las {llaves} se rellenan con `values`."""
    if _lang != "es" and text:
        text = CATALOGS.get(_lang, {}).get(text, text)
    return text.format(**values) if values else text


def N_(text):
    """Marca un texto para traducir más tarde (tablas y constantes de módulo)."""
    return text
