"""Idiomas de la interfaz: español (el del código), inglés, portugués, francés, alemán, italiano, chino
simplificado, japonés, ruso y coreano.

Los textos se escriben en español dentro de _("…") y ese mismo texto es la clave de cada catálogo
(clipqr/locale/<idioma>_*.py). Con variables: _("Vence en {n} días", n=3) — las llaves se rellenan después de
traducir, así el traductor ve la frase entera. Los textos que se definen al importar un módulo (tablas,
constantes) se marcan con N_("…"), que no traduce, y se traducen con _() al mostrarlos. Los catálogos se
importan uno a uno (nada de imports por nombre: PyInstaller no los vería).
"""
import locale
import os

from clipqr.locale import (
    en_app, en_fiscal, en_formats,
    pt_app, pt_fiscal, pt_formats,
    fr_app, fr_fiscal, fr_formats,
    de_app, de_fiscal, de_formats,
    it_app, it_fiscal, it_formats,
    zh_app, zh_fiscal, zh_formats,
    ja_app, ja_fiscal, ja_formats,
    ru_app, ru_fiscal, ru_formats,
    ko_app, ko_fiscal, ko_formats,
)

# código -> nombre en su propio idioma (así lo reconoce quien lo habla)
LANGUAGES = {"es": "Español", "en": "English", "pt": "Português", "fr": "Français", "de": "Deutsch",
             "it": "Italiano", "zh": "中文（简体）", "ja": "日本語", "ru": "Русский", "ko": "한국어"}
CATALOGS = {
    "en": {**en_app.TEXTS, **en_formats.TEXTS, **en_fiscal.TEXTS},
    "pt": {**pt_app.TEXTS, **pt_formats.TEXTS, **pt_fiscal.TEXTS},
    "fr": {**fr_app.TEXTS, **fr_formats.TEXTS, **fr_fiscal.TEXTS},
    "de": {**de_app.TEXTS, **de_formats.TEXTS, **de_fiscal.TEXTS},
    "it": {**it_app.TEXTS, **it_formats.TEXTS, **it_fiscal.TEXTS},
    "zh": {**zh_app.TEXTS, **zh_formats.TEXTS, **zh_fiscal.TEXTS},
    "ja": {**ja_app.TEXTS, **ja_formats.TEXTS, **ja_fiscal.TEXTS},
    "ru": {**ru_app.TEXTS, **ru_formats.TEXTS, **ru_fiscal.TEXTS},
    "ko": {**ko_app.TEXTS, **ko_formats.TEXTS, **ko_fiscal.TEXTS},
}
# LANGID primario de Windows -> código
WINDOWS_LANGIDS = {0x0A: "es", 0x09: "en", 0x16: "pt", 0x0C: "fr", 0x07: "de", 0x10: "it", 0x04: "zh",
                   0x11: "ja", 0x19: "ru", 0x12: "ko"}

_lang = "es"


def language_for_langid(lang_id):
    return WINDOWS_LANGIDS.get(lang_id & 0x3FF, "en")


def language_for_locale(name):
    """«pt_BR.UTF-8», «fr-FR», «zh_Hans_CN» -> código; si no lo hay, «en»."""
    code = (name or "").replace("-", "_").split("_")[0].split(".")[0].lower()
    return code if code in LANGUAGES else "en"


def system_language():
    """Idioma del sistema: el de la interfaz de Windows; en macOS, el idioma preferido del usuario; en Linux
    (o si no se pudo saber), el de la configuración regional. Si no está entre los disponibles, inglés (se
    entiende en más sitios)."""
    from clipqr.platform import ui_langid, ui_locale_name  # aquí: clipqr.platform importa este módulo
    try:
        lang_id = ui_langid()
        if lang_id is not None:
            return language_for_langid(lang_id)
        name = ui_locale_name()
        if name:
            return language_for_locale(name)
    except OSError:
        pass
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(var):
            return language_for_locale(os.environ[var])
    try:
        return language_for_locale(locale.getlocale()[0])
    except ValueError:
        return "en"


windows_language = system_language  # nombre anterior


def set_language(code):
    """«auto» (el del sistema) o un código de LANGUAGES."""
    global _lang
    _lang = system_language() if code in (None, "", "auto") else code if code in LANGUAGES else "es"
    return _lang


def language():
    return _lang


def _(text, **values):
    """Texto en el idioma activo (si falta la traducción, en inglés; si tampoco, en español); las {llaves}
    se rellenan con `values`."""
    if _lang != "es" and text:
        text = CATALOGS.get(_lang, {}).get(text) or CATALOGS["en"].get(text, text)
    return text.format(**values) if values else text


def N_(text):
    """Marca un texto para traducir más tarde (tablas y constantes de módulo)."""
    return text
