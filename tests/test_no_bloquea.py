"""Lo que puede tardar (borrar una captura en OneDrive, leer el portapapeles) no congela la ventana del aviso."""
import threading
import time

import pytest

import clipqr.app as app_module
from clipqr.app import ClipQR


class FakeRoot:
    """Guarda lo que se programa con after() para ejecutarlo como lo haría el hilo de Tk."""
    def __init__(self):
        self.pending = []
        self.lock = threading.Lock()

    def after(self, ms, fn, *args):
        with self.lock:
            self.pending.append(lambda: fn(*args))

    def run_pending(self, timeout=3.0):
        end = time.time() + timeout
        while time.time() < end:
            with self.lock:
                jobs, self.pending = self.pending, []
            for job in jobs:
                job()
            if jobs:
                return True
            time.sleep(0.01)
        return False


def make_app():
    a = ClipQR.__new__(ClipQR)
    a.root = FakeRoot()
    a.settings = {"delete_capture": True, "explorer_files": True}
    a.painted = []
    a._paint_capture_slot = lambda codes: a.painted.append([c.get("capture_deleted") for c in codes])
    return a


def test_borrar_la_captura_no_bloquea(monkeypatch):
    release = threading.Event()

    def slow_trash(path):  # como la Papelera de una carpeta de OneDrive
        release.wait(5)
        return True

    monkeypatch.setattr(app_module, "send_to_trash", slow_trash)
    a = make_app()
    codes = [{"text": "x"}]
    t = time.time()
    a._on_capture(codes, r"C:\capturas\Captura.png")
    assert time.time() - t < 0.2  # vuelve enseguida: el aviso sigue respondiendo
    assert a.painted == []  # todavía borrando
    release.set()
    assert a.root.run_pending()
    assert a.painted == [[True]] and codes[0]["capture_deleted"] is True


def test_borrado_fallido_avisa(monkeypatch):
    monkeypatch.setattr(app_module, "send_to_trash", lambda path: False)
    a = make_app()
    results = []
    a.trash_in_background("x.png", [{"text": "x"}], results.append)
    assert a.root.run_pending()
    assert results == [False] and a.painted == [[False]]


@pytest.mark.skipif(app_module.SYSTEM == "macos", reason="en macOS el portapapeles se lee directamente")
def test_leer_el_portapapeles_no_bloquea(monkeypatch):
    release = threading.Event()
    a = make_app()
    got = []
    t = time.time()
    a._off_tk(lambda: (release.wait(5), "imagen")[1], got.append)
    assert time.time() - t < 0.2 and got == []
    release.set()
    assert a.root.run_pending()
    assert got == ["imagen"]
