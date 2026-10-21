"""Piezas comunes: botones, interruptores, filas, imágenes."""
import tkinter as tk

from PIL import Image, ImageTk

from clipqr.i18n import _
from clipqr.icons import make_icon
from clipqr.ui.theme import KINDS, _shade


class WidgetsMixin:
    def px(self, n):
        return int(n * self.dpi)

    def font(self, size, weight="normal"):
        return (self.ui_font, size, weight)

    def glyph(self, kind_or_char):
        """(texto, fuente) para un icono: glifo de Segoe Fluent Icons o emoji de reserva."""
        if kind_or_char in KINDS:
            g, emoji, __ = KINDS[kind_or_char]
            return (g, (self.icon_font, 12)) if self.icon_font else (emoji, self.font(11))
        return kind_or_char, (self.icon_font or self.ui_font, 10)

    def _flash(self, btn, text, ok=True):
        if not btn.winfo_exists():
            return
        old_text, old_bg = btn.cget("text"), btn._base_bg
        btn._base_bg = self.c["ok"] if ok else "#c62828"
        btn.config(text=text, bg=btn._base_bg, fg="white")
        def restore():
            if btn.winfo_exists():
                btn._base_bg = old_bg
                btn.config(text=old_text, bg=old_bg, fg=btn._base_fg)
        btn.after(1300, restore)

    def _button(self, parent, text, cmd=None, color=None, bg=None):
        """Botón plano con efecto hover. `color` = botón principal con ese acento."""
        c = self.c
        base = color or c["btn"]
        fg = "white" if color else c["fg"]
        hover = _shade(color, 0.85) if color else c["btn_hover"]
        b = tk.Button(parent, text=text, command=cmd, bg=base, fg=fg, activebackground=hover,
                      activeforeground=fg, relief="flat", bd=0, padx=self.px(10), pady=self.px(4),
                      font=self.font(9, "bold" if color else "normal"), cursor="hand2", highlightthickness=0)
        b._base_bg, b._base_fg = base, fg
        b.bind("<Enter>", lambda e: b.cget("state") != "disabled" and b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.focus_get() is not b and b.config(bg=b._base_bg))
        # con el teclado (Tab) el botón enfocado se resalta igual que con el ratón; Espacio lo pulsa
        b.bind("<FocusIn>", lambda e: b.config(bg=hover))
        b.bind("<FocusOut>", lambda e: b.config(bg=b._base_bg))
        b.bind("<Return>", lambda e: b.invoke())
        return b

    def _row(self, parent, label, value):
        c = self.c
        row = tk.Frame(parent, bg=c["card"])
        row.pack(fill="x", pady=1)
        tk.Label(row, text=label, bg=c["card"], fg=c["muted"], font=self.font(8), width=11,
                 anchor="w").pack(side="left")
        shown = value if len(value) <= 60 else value[:60] + "…"
        if label.lower().startswith(_("Contraseña").lower()) or label == _("Secreto"):
            hidden = "•" * min(len(value), 14)
            var = tk.StringVar(value=shown if self.settings.get("show_passwords") else hidden)
            lbl = tk.Label(row, textvariable=var, bg=c["card"], fg=c["fg"], font=("Consolas", 10),
                           anchor="w", cursor="hand2")
            toggle = self._button(row, self.glyph("")[0] if self.icon_font else "👁")
            toggle.config(font=self.glyph("")[1], padx=self.px(6),
                          command=lambda: var.set(shown if var.get() == hidden else hidden))
        else:
            lbl = tk.Label(row, text=shown, bg=c["card"], fg=c["fg"], font=self.font(10), anchor="w",
                           justify="left", wraplength=self.px(230))
            toggle = None
        lbl.pack(side="left", fill="x", expand=True)
        b = self._button(row, _("Copiar"))
        b.config(command=lambda: self.copy(value, b))
        b.pack(side="right")
        if toggle:
            toggle.pack(side="right", padx=(0, self.px(4)))
        return b

    def _photo(self, pil_img, size):
        img = pil_img.copy()
        img.thumbnail((size, size), Image.LANCZOS)
        p = ImageTk.PhotoImage(img)
        self._photos.append(p)
        del self._photos[:-200]
        return p

    def _logo(self, size):
        return self._photo(make_icon(size=self.px(size), dark_bg=self.theme_name() == "dark"), self.px(size))

    def _window_header(self, win, title, subtitle):
        c = self.c
        top = tk.Frame(win, bg=c["bg"])
        top.pack(fill="x", padx=self.px(16), pady=(self.px(14), self.px(6)))
        tk.Label(top, image=self._logo(36), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(12)))
        txt = tk.Frame(top, bg=c["bg"])
        txt.pack(side="left")
        tk.Label(txt, text=title, bg=c["bg"], fg=c["fg"], font=self.font(14, "bold")).pack(anchor="w")
        tk.Label(txt, text=subtitle, bg=c["bg"], fg=c["muted"], font=self.font(8)).pack(anchor="w")
        return top

    def _switch(self, parent, value, on_change):
        """Interruptor tipo Windows 11 dibujado en un Canvas."""
        c, w, h = self.c, self.px(40), self.px(20)
        cv = tk.Canvas(parent, width=w, height=h, bg=parent.cget("bg"), highlightthickness=0, bd=0, cursor="hand2")
        state = {"on": bool(value)}

        def draw():
            cv.delete("all")
            on = state["on"]
            fill = KINDS["link"][2] if on else c["btn"]
            r = h // 2
            cv.create_oval(0, 0, h, h, fill=fill, width=0)
            cv.create_oval(w - h, 0, w, h, fill=fill, width=0)
            cv.create_rectangle(r, 0, w - r, h, fill=fill, width=0)
            k = self.px(4)
            cx = w - r if on else r
            cv.create_oval(cx - r + k, k, cx + r - k, h - k, fill="white" if on else c["muted"], width=0)

        def click(e):
            state["on"] = not state["on"]
            draw()
            on_change(state["on"])

        cv.bind("<Button-1>", click)
        draw()
        return cv

    def _segmented(self, parent, options, value, on_change):
        """Fila de botones donde solo uno está activo."""
        box = tk.Frame(parent, bg=parent.cget("bg"))
        buttons = {}
        state = {"v": value}

        def paint():
            for key, b in buttons.items():
                sel = key == state["v"]
                b._base_bg = KINDS["link"][2] if sel else self.c["btn"]
                b._base_fg = "white" if sel else self.c["fg"]
                b.config(bg=b._base_bg, fg=b._base_fg)

        def pick(key):
            state["v"] = key
            paint()
            on_change(key)

        for key, label, enabled in options:
            b = self._button(box, label, cmd=lambda k=key: pick(k))
            if not enabled:
                b.config(state="disabled", cursor="arrow")
            b.pack(side="left", padx=(0, self.px(4)), pady=self.px(2))
            buttons[key] = b
        paint()
        return box

    def _stepper(self, parent, choices, value, fmt, on_change):
        """[−] valor [+] sobre una lista de valores permitidos."""
        box = tk.Frame(parent, bg=parent.cget("bg"))
        idx = {"i": min(range(len(choices)), key=lambda i: abs(choices[i] - value))}
        lbl = tk.Label(box, text=fmt(choices[idx["i"]]), width=7, bg=parent.cget("bg"), fg=self.c["fg"],
                       font=self.font(10, "bold"))

        def move(d):
            idx["i"] = min(max(idx["i"] + d, 0), len(choices) - 1)
            lbl.config(text=fmt(choices[idx["i"]]))
            on_change(choices[idx["i"]])

        self._button(box, "−", cmd=lambda: move(-1)).pack(side="left")
        lbl.pack(side="left")
        self._button(box, "+", cmd=lambda: move(1)).pack(side="left")
        return box
