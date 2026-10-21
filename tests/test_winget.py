"""Manifiestos de winget: estructura y datos clave."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import winget_manifest  # noqa: E402


def test_three_manifests_with_matching_identity(tmp_path):
    exe = tmp_path / "ClipQR-Setup.exe"
    exe.write_bytes(b"instalador de prueba")
    folder = winget_manifest.write("1.2.3", str(exe), str(tmp_path / "winget"))
    files = sorted(os.listdir(folder))
    assert files == ["MojeZcg.ClipQR.installer.yaml", "MojeZcg.ClipQR.locale.es-ES.yaml", "MojeZcg.ClipQR.yaml"]
    for name in files:
        text = open(os.path.join(folder, name), encoding="utf-8").read()
        assert "PackageIdentifier: MojeZcg.ClipQR" in text and "PackageVersion: 1.2.3" in text


def test_installer_manifest_has_silent_switch_and_hash(tmp_path):
    exe = tmp_path / "ClipQR-Setup.exe"
    exe.write_bytes(b"abc")
    text = winget_manifest.manifests("1.2.3", winget_manifest.sha256(str(exe)))["MojeZcg.ClipQR.installer.yaml"]
    assert "Silent: /silent" in text and "Scope: user" in text
    assert "releases/download/v1.2.3/ClipQR-Setup.exe" in text
    assert "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD" in text  # sha256("abc")
