"""Ventana de historial."""
import time
import tkinter as tk

from PIL import ImageTk

from clipqr import APP_NAME
from clipqr.i18n import _
from clipqr.icons import make_icon
from clipqr.payloads import analyze
from clipqr.platform import style_window
from clipqr.ui.system_texts import empty_history_text
from clipqr.ui.theme import KINDS, THEMES


class HistoryMixin:
    def show_history(self):
        if self.history_win is not None and self.history_win.winfo_exists():
            self.history_win.deiconify()
            self.history_win.lift()
            self.history_win.focus_force()
            return
        self.c = THEMES[self.theme_name()]
        c = self.c
        win = tk.Toplevel(self.root, bg=c["bg"])
        self.history_win = win
        win.title(f"{APP_NAME} · {_('Historial')}")
        win.geometry(f"{self.px(520)}x{self.px(600)}")
        win.minsize(self.px(380), self.px(300))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")

        top = tk.Frame(win, bg=c["bg"])
        top.pack(fill="x", padx=self.px(14), pady=(self.px(14), self.px(8)))
        tk.Label(top, image=self._logo(28), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(10)))
        tk.Label(top, text=_("Historial"), bg=c["bg"], fg=c["fg"], font=self.font(14, "bold")).pack(side="left")
        self._button(top, _("Escanear ahora"), cmd=lambda: self.scan(force=True)).pack(side="right")
        if not self.tray_has_menu:
            # sin menú en la bandeja (o sin bandeja), esta ventana hace de ventana principal
            self._button(top, _("Salir"), cmd=self.quit).pack(side="right", padx=(0, self.px(6)))
            self._button(top, _("Configuración…"), cmd=self.show_settings).pack(side="right", padx=(0, self.px(6)))
            win.protocol("WM_DELETE_WINDOW", win.iconify)  # cerrarla no debe dejar ClipQR inalcanzable

        sbox = tk.Frame(win, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
        sbox.pack(fill="x", padx=self.px(14), pady=(0, self.px(8)))
        if self.icon_font:
            tk.Label(sbox, text="", font=(self.icon_font, 10), bg=c["card"], fg=c["muted"]).pack(side="left", padx=(self.px(8), 0))
        self.search_var = tk.StringVar()
        entry = tk.Entry(sbox, textvariable=self.search_var, bg=c["card"], fg=c["fg"], insertbackground=c["fg"],
                         relief="flat", font=self.font(10), highlightthickness=0)
        entry.pack(fill="x", padx=self.px(8), pady=self.px(6))
        self.search_var.trace_add("write", lambda *a: self._fill_history())

        wrap = tk.Frame(win, bg=c["bg"])
        wrap.pack(fill="both", expand=True, padx=(self.px(14), 0), pady=(0, self.px(14)))
        canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)
        self.hist_list = tk.Frame(canvas, bg=c["bg"])
        wid = canvas.create_window((0, 0), window=self.hist_list, anchor="nw")
        self.hist_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(wid, width=e.width - self.px(10)))
        self._bind_wheel(win, canvas)
        win.bind("<Escape>", lambda e: win.destroy() if self.tray_has_menu else win.iconify())
        self._fill_history()
        entry.focus_set()

    def _fill_history(self):
        c = self.c
        for w in self.hist_list.winfo_children():
            w.destroy()
        q = self.search_var.get().strip().lower()
        entries = [code for scan in self.history for code in scan if not q or q in code["text"].lower()]
        if not entries:
            # wraplength: el texto de macOS es más largo que la lista y se cortaba por los dos lados
            tk.Label(self.hist_list, text=_("Sin resultados.") if q else empty_history_text(), bg=c["bg"], fg=c["muted"],
                     font=self.font(10), justify="center", wraplength=self.px(340)).pack(pady=self.px(40))
            return
        for code in entries:
            r = analyze(code["text"])
            kind, title, items = r.kind, r.title, r.items
            row = tk.Frame(self.hist_list, bg=c["card"], highlightthickness=1, highlightbackground=c["border"],
                           cursor="hand2")
            row.pack(fill="x", pady=(0, self.px(6)))
            # el botón se coloca primero para que un texto largo no lo saque de la fila
            b = self._button(row, _("Copiar"))
            b.config(command=lambda t=code["text"], b=b: self.copy(t, b))
            b.pack(side="right", padx=self.px(8))
            if code.get("thumb") is not None:
                tk.Label(row, image=self._photo(code["thumb"], self.px(44)), bg=c["card"], bd=0).pack(side="left", padx=self.px(8), pady=self.px(8))
            mid = tk.Frame(row, bg=c["card"])
            mid.pack(side="left", fill="x", expand=True, pady=self.px(6))
            line = tk.Frame(mid, bg=c["card"])
            line.pack(anchor="w")
            g, gf = self.glyph(kind)
            tk.Label(line, text=g, font=gf, bg=c["card"], fg=KINDS[kind][2]).pack(side="left", padx=(0, self.px(6)))
            tk.Label(line, text=title, bg=c["card"], fg=c["fg"], font=self.font(10, "bold")).pack(side="left")
            tk.Label(line, text="  " + time.strftime("%H:%M", time.localtime(code["time"])), bg=c["card"],
                     fg=c["muted"], font=self.font(8)).pack(side="left")
            # resumen legible (Ana Pérez · +34 600…) en vez del texto crudo de vCard / Wi-Fi
            summary = [v for l, v in items if l not in (_("Contraseña"), _("Secreto"), _("Dominio"))][:3]
            if r.headline:  # facturas, pagos…: «$ 12.345,67 · Factura B · 0003-00001234»
                preview = " · ".join(x for x in (r.headline[1], r.subtitle) if x)
            elif kind not in ("link", "text", "product") and summary:
                preview = " · ".join(summary)
            else:
                preview = code["text"].replace("\r", "").replace("\n", " · ")
            tk.Label(mid, text=(preview[:52] + "…") if len(preview) > 52 else preview, bg=c["card"],
                     fg=c["muted"], font=self.font(9), anchor="w").pack(anchor="w", fill="x")
            open_it = lambda e, cd=code: self.show_popup([cd])
            for w in (row, mid, line, *mid.winfo_children(), *line.winfo_children(), *row.winfo_children()):
                if w is not b:
                    w.bind("<Button-1>", open_it)
