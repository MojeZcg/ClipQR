"""Actualizaciones: versiones, sumas y verificación de la descarga (sin red)."""
import hashlib

import pytest

from clipqr import updates


@pytest.mark.parametrize("text, expected", [
    ("v1.2.3", (1, 2, 3)), ("1.2.3", (1, 2, 3)), ("v1.10", (1, 10, 0)), ("1.2.0-beta", (1, 2, 0)),
])
def test_parse_version(text, expected):
    assert updates.parse_version(text) == expected


def test_is_newer():
    assert updates.is_newer("1.1.0", "1.0.9")
    assert updates.is_newer("v1.10.0", "1.9.9")
    assert not updates.is_newer("1.0.0", "1.0.0")
    assert not updates.is_newer("0.9.9", "1.0.0")


def test_parse_sums():
    text = "AB" * 32 + "  ClipQR-Setup.exe\n" + "cd" * 32 + " *ClipQR.exe\nbasura\n"
    assert updates.parse_sums(text) == {"ClipQR-Setup.exe": "ab" * 32, "ClipQR.exe": "cd" * 32}


def test_setup_args_keep_user_choices():
    assert updates.setup_args(True, False) == ["/silent", "/launch"]
    assert updates.setup_args(False, True) == ["/silent", "/launch", "/noautostart", "/desktop"]


def _fake_release(monkeypatch, payload, sums_for):
    files = {"https://x/sums": f"{hashlib.sha256(sums_for).hexdigest()}  ClipQR-Setup.exe\n".encode(),
             "https://x/setup": payload}
    monkeypatch.setattr(updates, "_get", lambda url, timeout=10: files[url])
    return {"version": "9.9.9", "page": "https://x", "assets": {"ClipQR-Setup.exe": "https://x/setup",
                                                                "SHA256SUMS.txt": "https://x/sums"}}


def test_download_is_verified(monkeypatch, tmp_path):
    info = _fake_release(monkeypatch, b"instalador", b"instalador")
    path = updates.download_verified(info, str(tmp_path))
    assert open(path, "rb").read() == b"instalador"


def test_tampered_download_is_rejected(monkeypatch, tmp_path):
    info = _fake_release(monkeypatch, b"instalador modificado", b"instalador")
    with pytest.raises(ValueError, match="no coincide"):
        updates.download_verified(info, str(tmp_path))
    assert not (tmp_path / "ClipQR-Setup.exe").exists()


def test_release_without_sums_is_not_installed():
    with pytest.raises(ValueError, match="sumas"):
        updates.download_verified({"assets": {"ClipQR-Setup.exe": "https://x/setup"}})


def test_release_workflow_publishes_every_system_with_its_sum():
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    for name in (updates.SETUP_NAME, updates.MAC_NAME, updates.LINUX_NAME, updates.SUMS_NAME):
        assert name in workflow, name
    assert updates.MAC_NAME in (root / "build_macos.sh").read_text(encoding="utf-8")
    assert updates.LINUX_NAME in (root / "build_linux.sh").read_text(encoding="utf-8")
