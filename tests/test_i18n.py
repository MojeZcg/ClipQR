"""Idiomas: cada texto marcado con _() o N_() tiene traducción al inglés con las mismas {llaves}."""
import ast
import pathlib
import string

import pytest

from clipqr import i18n
from clipqr.i18n import CATALOGS, _

ROOT = pathlib.Path(__file__).resolve().parent.parent / "clipqr"


def marked_texts():
    for path in ROOT.rglob("*.py"):
        if path.parent.name == "locale":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) in ("_", "N_") and node.args \
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                yield f"{path.relative_to(ROOT)}:{node.lineno}", node.args[0].value


def fields(text):
    return sorted(f for _, f, _, _ in string.Formatter().parse(text) if f)


TRANSLATED = [code for code in CATALOGS if CATALOGS[code]]  # un catálogo vacío = idioma aún sin traducir


@pytest.mark.parametrize("code", TRANSLATED)
def test_todo_tiene_traduccion(code):
    catalog = CATALOGS[code]
    missing = [f"{where}: {text!r}" for where, text in marked_texts() if text not in catalog]
    assert not missing, f"Sin traducción ({code}):\n" + "\n".join(missing)


@pytest.mark.parametrize("code", TRANSLATED)
def test_mismas_llaves(code):
    wrong = [k for k, v in CATALOGS[code].items() if fields(k) != fields(v)]
    assert not wrong, wrong


@pytest.mark.parametrize("code", TRANSLATED)
def test_sin_traducciones_sobrantes(code):
    used = {text for _, text in marked_texts()}
    unused = [k for k in CATALOGS[code] if k not in used]
    assert not unused, unused


def test_todos_los_idiomas_tienen_catalogo():
    assert set(CATALOGS) | {"es"} == set(i18n.LANGUAGES)


@pytest.mark.parametrize("name, code", [("pt_BR.UTF-8", "pt"), ("fr-FR", "fr"), ("zh_CN", "zh"), ("ja_JP", "ja"),
                                        ("tr_TR.UTF-8", "tr"), ("es_AR.UTF-8", "es"), ("nl_NL", "en"), ("", "en"),
                                        (None, "en")])
def test_idioma_por_configuracion_regional(name, code):
    assert i18n.language_for_locale(name) == code


@pytest.mark.parametrize("langid, code", [(0x2C0A, "es"), (0x0409, "en"), (0x0416, "pt"), (0x040C, "fr"),
                                          (0x0407, "de"), (0x0804, "zh"), (0x0411, "ja"), (0x0419, "ru"),
                                          (0x0412, "ko"), (0x041F, "tr"), (0x0413, "en")])
def test_idioma_por_langid_de_windows(langid, code):
    assert i18n.language_for_langid(langid) == code


def test_cambio_de_idioma():
    i18n.set_language("en")
    assert i18n.language() == "en"
    assert _("texto que no está en el catálogo") == "texto que no está en el catálogo"
    i18n.set_language("es")
    assert _("Vence en {n} días", n=3) == "Vence en 3 días"


@pytest.mark.parametrize("code, expected", [("es", "es"), ("en", "en"), ("ja", "ja"), ("xx", "es")])
def test_set_language(code, expected):
    assert i18n.set_language(code) == expected
    assert i18n.set_language("auto") in i18n.LANGUAGES  # depende del idioma del sistema
