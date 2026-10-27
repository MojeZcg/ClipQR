"""Atajos de teclado globales."""
import sys

import pytest

from clipqr.hotkeys import MOD_NOREPEAT, parse_hotkey
from clipqr.platform import HotkeyManager

windows_only = pytest.mark.skipif(sys.platform != "win32", reason="RegisterHotKey es de Windows")


@pytest.mark.parametrize("text, expected", [
    ("Ctrl+Alt+Q", (0x2 | 0x1 | MOD_NOREPEAT, ord("Q"))),
    ("ctrl + shift + espacio", (0x2 | 0x4 | MOD_NOREPEAT, 0x20)),
    ("Alt+Shift+F9", (0x1 | 0x4 | MOD_NOREPEAT, 0x78)),
    ("Win+Shift+7", (0x8 | 0x4 | MOD_NOREPEAT, ord("7"))),
])
def test_parse_hotkey(text, expected):
    assert parse_hotkey(text) == expected


@pytest.mark.parametrize("text", ["Q", "Ctrl+", "Hyper+Q", "Ctrl+Flecha"])
def test_invalid_hotkeys(text):
    with pytest.raises(ValueError):
        parse_hotkey(text)


@windows_only
def test_register_and_release_a_real_hotkey():
    m = HotkeyManager()
    try:
        # combinación poco habitual para no chocar con nada del equipo
        assert m.set({"Ctrl+Alt+Shift+F11": lambda: None}) == []
        assert m.set({"Ctrl+Alt+Shift+F11": lambda: None, "Ctrl+Nada": lambda: None}) == ["Ctrl+Nada"]
        assert m.set({}) == []
    finally:
        m.stop()


@windows_only
def test_hotkey_taken_by_another_registration_is_reported():
    a, b = HotkeyManager(), HotkeyManager()
    try:
        assert a.set({"Ctrl+Alt+Shift+F12": lambda: None}) == []
        assert b.set({"Ctrl+Alt+Shift+F12": lambda: None}) == ["Ctrl+Alt+Shift+F12"]
    finally:
        a.stop()
        b.stop()
