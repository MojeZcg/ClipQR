"""Línea de órdenes de ClipQR.exe y estado guardado."""
import pytest

from clipqr import settings
from clipqr.app import parse_cli


@pytest.mark.parametrize("argv, expected", [
    ([], ("run", False)),
    (["--autostart"], ("run", True)),
    (["--uninstall"], ("uninstall", False)),
    (["--uninstall", "/silent"], ("uninstall", True)),
    (["--uninstall", "/SILENT"], ("uninstall", True)),
    (["foto.png"], ("decode", ["foto.png"])),
    (["a.png", "b.jpg"], ("decode", ["a.png", "b.jpg"])),
])
def test_parse_cli(argv, expected):
    assert parse_cli(argv) == expected


def test_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "STATE_FILE", str(tmp_path / "state.json"))
    assert settings.load_state() == {}
    settings.save_state(clip_seq=7)
    settings.save_state(otra=1)
    assert settings.load_state() == {"clip_seq": 7, "otra": 1}
