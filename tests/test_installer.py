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
