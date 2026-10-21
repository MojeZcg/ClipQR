"""Ajustes e informe de errores."""
from clipqr import settings


def test_error_report_includes_version_and_last_errors(tmp_path, monkeypatch):
    log = tmp_path / "error.log"
    log.write_text("\n".join(f"línea {i}" for i in range(100)), encoding="utf-8")
    monkeypatch.setattr(settings, "ERROR_LOG", str(log))
    report = settings.error_report("9.9.9", limit=5)
    assert report.startswith("ClipQR 9.9.9 · Windows")
    assert "línea 99" in report and "línea 94" not in report


def test_error_report_without_log(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ERROR_LOG", str(tmp_path / "no-existe.log"))
    assert "no hay errores registrados" in settings.error_report("1.0.0")


def test_new_settings_have_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", str(tmp_path / "settings.json"))
    (tmp_path / "settings.json").write_text('{"seconds": 10}', encoding="utf-8")  # ajustes de una versión vieja
    s = settings.load_settings()
    assert s["seconds"] == 10 and s["show_passwords"] is False and s["check_updates"] is True
