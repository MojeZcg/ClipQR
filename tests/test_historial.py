"""Ventana del historial: el texto de «sin códigos» cabe en la lista."""
import tkinter as tk
import tkinter.font as tkfont

import pytest

from clipqr.app import ClipQR
from clipqr.ui.system_texts import empty_history_text


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError:
        pytest.skip("sin pantalla")
    r.withdraw()
    yield r
    r.destroy()


@pytest.mark.parametrize("system", ["windows", "macos", "linux"])
def test_texto_sin_codigos_cabe(root, monkeypatch, system):
    monkeypatch.setattr("clipqr.ui.history.empty_history_text", lambda: empty_history_text(system))
    a = ClipQR.__new__(ClipQR)
    a.c = {"bg": "#202020", "muted": "#a3a3a3"}
    a.px = lambda v: v
    a.font = lambda size, *style: tkfont.Font(root, size=size)
    a.history, a.search_var, a.hist_list = [], tk.StringVar(root), tk.Frame(root)
    a._fill_history()
    label = a.hist_list.winfo_children()[0]
    assert label.winfo_reqwidth() <= 380  # ancho mínimo de la ventana
