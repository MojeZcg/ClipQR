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


def test_todo_tiene_traduccion():
    en = CATALOGS["en"]
    missing = [f"{where}: {text!r}" for where, text in marked_texts() if text not in en]
    assert not missing, "Sin traducción al inglés:\n" + "\n".join(missing)


def test_mismas_llaves_en_ingles():
    wrong = [k for k, v in CATALOGS["en"].items() if fields(k) != fields(v)]
    assert not wrong, wrong


def test_sin_traducciones_sobrantes():
    used = {text for _, text in marked_texts()}
    unused = [k for k in CATALOGS["en"] if k not in used]
    assert not unused, unused


def test_cambio_de_idioma():
    i18n.set_language("en")
    assert i18n.language() == "en"
    assert _("texto que no está en el catálogo") == "texto que no está en el catálogo"
    i18n.set_language("es")
    assert _("Vence en {n} días", n=3) == "Vence en 3 días"


@pytest.mark.parametrize("code, expected", [("es", "es"), ("en", "en"), ("xx", "es")])
def test_set_language(code, expected):
    assert i18n.set_language(code) == expected
    assert i18n.set_language("auto") in ("es", "en")
