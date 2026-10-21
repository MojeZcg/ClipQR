"""El aviso que aparece al detectar un código."""
import os
import tkinter as tk


from clipqr.icons import make_icon
from clipqr.linksafety import link_warnings
from clipqr.payloads import format_name, headline, parse_payload, shorten
from clipqr.ui.theme import KINDS, THEMES
from clipqr.winplatform import (area_containing, clamp_to_area, force_foreground, send_to_recycle_bin,
                                style_window, user32, work_area, work_areas)

MAX_CARDS = 4


class PopupMixin:
    def _card(self, parent, code):
        """Tarjeta de un código, pensada para leerse de un vistazo: el dato principal en grande,
        la acción principal justo debajo, el resto de datos compactos y el texto crudo plegado."""
        c = self.c
        kind, title, items, actions = parse_payload(code["text"])
        accent = KINDS[kind][2]
        text = code["text"]
        head_label, head_value = headline(kind, items, text)
        rows = [(l, v) for l, v in items if (l, v) != (head_label, head_value)]

        card = tk.Frame(parent, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
        card.pack(fill="x", padx=self.px(12), pady=(0, self.px(8)))
        inner = tk.Frame(card, bg=c["card"])
        inner.pack(fill="both", padx=self.px(12), pady=self.px(10))

        # tipo (pequeño, en color) + dato principal (grande)
        top = tk.Frame(inner, bg=c["card"])
        top.pack(fill="x")
        if code.get("thumb") is not None:
            tk.Label(top, image=self._photo(code["thumb"], self.px(46)), bg=c["card"], bd=0).pack(
                side="left", anchor="n", padx=(0, self.px(12)))
        b_head = self._button(top, "Copiar")
        b_head.config(command=lambda: self.copy(head_value, b_head))
        b_head.pack(side="right", anchor="n")
        copy_buttons = [b_head]  # para los atajos 1–9: el dato principal y luego el resto, en orden
        head = tk.Frame(top, bg=c["card"])
        head.pack(side="left", fill="x", expand=True)
        meta = tk.Frame(head, bg=c["card"])
        meta.pack(anchor="w")
        g, gf = self.glyph(kind)
        tk.Label(meta, text=g, font=(gf[0], 10), bg=c["card"], fg=accent).pack(side="left", padx=(0, self.px(5)))
        tk.Label(meta, text=title.upper(), bg=c["card"], fg=accent, font=self.font(8, "bold")).pack(side="left")
        tk.Label(meta, text=f"  ·  {format_name(code['format'])}", bg=c["card"], fg=c["muted"],
                 font=self.font(8)).pack(side="left")
        tk.Label(head, text=shorten(head_value, 70), bg=c["card"], fg=c["fg"], font=self.font(15, "bold"),
                 anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")
        if kind == "link":  # el dominio no basta: la URL completa, en pequeño
            tk.Label(head, text=shorten(text, 90, middle=True), bg=c["card"], fg=c["muted"], font=self.font(9),
                     anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")

        # avisos (enlaces sospechosos, datos que no cuadran…) justo antes de los botones
        warnings = link_warnings(actions[0][2]) if kind == "link" and actions else []
        warnings += code.get("warnings", [])
        if warnings:
            self._warning_strip(inner, warnings)

        # acción principal en grande, las demás al lado
        if actions:
            bar = tk.Frame(inner, bg=c["card"])
            bar.pack(fill="x", pady=(self.px(10), 0))
            for i, (label, kind_a, arg) in enumerate(actions):
                b = self._button(bar, label, color=accent)
                if i == 0:
                    b.config(font=self.font(10, "bold"), padx=self.px(16), pady=self.px(6))
                b.config(command=lambda k=kind_a, a=arg, b=b: self.run_action(k, a, b))
                b.pack(side="left", padx=(0, self.px(6)), pady=(0, self.px(2)))
                if i == 0 and getattr(self, "_kbd_primary", None) is not None:
                    self._kbd_primary.append(b)

        # resto de datos, compactos
        if rows:
            box = tk.Frame(inner, bg=c["card"])
            box.pack(fill="x", pady=(self.px(10), 0))
            for label, value in rows:
                copy_buttons.append(self._row(box, label, value))
        if getattr(self, "_kbd_copy", None) is not None:
            self._kbd_copy.extend(copy_buttons)

        # texto completo plegado (en «Texto» se ve desde el principio si es largo)
        foot = tk.Frame(inner, bg=c["card"])
        foot.pack(fill="x", pady=(self.px(8), 0))
        raw = tk.Frame(inner, bg=c["card"])
        toggle = tk.Label(foot, bg=c["card"], fg=c["muted"], font=self.font(9), cursor="hand2")
        toggle.pack(side="left")
        b_all = self._button(foot, "Copiar todo")
        b_all.config(command=lambda: self.copy(text, b_all))
        b_all.pack(side="right")
        state = {"open": False, "built": False}

        def build_raw():
            lines = min(max(text.count("\n") + 1, len(text) // 50 + 1), 6)
            txt = tk.Text(raw, height=lines, width=50, wrap="word", bg=c["textbg"], fg=c["fg"], relief="flat",
                          font=("Consolas", 9), padx=self.px(6), pady=self.px(4), selectbackground=accent,
                          selectforeground="white", highlightthickness=0, bd=0, cursor="xterm")
            txt.insert("1.0", text)
            txt.config(state="disabled")
            txt.pack(fill="x", pady=(self.px(6), self.px(4)))
            b_sel = self._button(raw, "Copiar selección")

            def copy_sel():
                try:
                    self.copy(txt.get("sel.first", "sel.last"), b_sel)
                except tk.TclError:
                    self._flash(b_sel, "Selecciona texto arriba", ok=False)

            b_sel.config(command=copy_sel)
            b_sel.pack(anchor="e")

        def flip(e=None):
            state["open"] = not state["open"]
            if state["open"]:
                if not state["built"]:
                    build_raw()
                    state["built"] = True
                raw.pack(fill="x", after=foot)
            else:
                raw.pack_forget()
            toggle.config(text=("▾ Ocultar texto completo" if state["open"] else "▸ Ver texto completo"))
            if e is not None and self.popup is not None:
                self._refit_popup()

        toggle.config(text="▸ Ver texto completo")
        toggle.bind("<Button-1>", flip)
        toggle.bind("<Enter>", lambda e: toggle.config(fg=c["fg"]))
        toggle.bind("<Leave>", lambda e: toggle.config(fg=c["muted"]))
        if kind == "text" and (len(text) > 70 or "\n" in text):
            flip()

    def _warning_strip(self, parent, warnings, level="warn"):
        """Franja de avisos: ámbar (warn) o roja (bad). Informa; no bloquea nada."""
        c = self.c
        bg, fg = c[f"{level}_bg"], c[f"{level}_fg"]
        strip = tk.Frame(parent, bg=bg)
        strip.pack(fill="x", pady=(self.px(10), 0))
        for w in warnings:
            line = tk.Frame(strip, bg=bg)
            line.pack(fill="x", padx=self.px(8), pady=(self.px(3), 0))
            tk.Label(line, text="⚠", bg=bg, fg=fg, font=self.font(9, "bold")).pack(side="left", anchor="n")
            tk.Label(line, text=w, bg=bg, fg=fg, font=self.font(9), anchor="w", justify="left",
                     wraplength=self.px(330)).pack(side="left", fill="x", padx=(self.px(4), 0))
        tk.Frame(strip, bg=bg, height=self.px(3)).pack()

    def _warm_up(self):
        """Muestra un aviso de ejemplo fuera de la pantalla y transparente para que Tk cargue fuentes y
        recursos al arrancar; si no, el primer aviso real tarda casi un segundo en aparecer."""
        win = tk.Toplevel(self.root, bg=self.c["bg"])
        win.overrideredirect(True)
        win.attributes("-alpha", 0.0)
        win.attributes("-topmost", True)
        win.geometry("+-4000+-4000")
        sample = {"format": "QRCode", "text": "WIFI:T:WPA;S:ClipQR;P:clipqr;;\nhttps://example.com",
                  "thumb": make_icon(size=64).convert("RGB")}
        self._card(win, sample)
        tk.Label(win, image=self._logo(18)).pack()
        tk.Canvas(win, height=3).pack()
        tk.Entry(win, font=self.font(10)).pack()
        style_window(win, border=self.c["border"])
        win.update()
        win.destroy()

    def _refit_popup(self):
        """Reajusta el alto del aviso al desplegar/plegar contenido, sin moverlo de sitio."""
        win = self.popup
        if win is None or not win.winfo_exists():
            return
        win.update_idletasks()
        rect = work_area((win.winfo_x() + 10, win.winfo_y() + 10))  # el monitor donde está el aviso
        h = min(win.winfo_reqheight(), rect.bottom - rect.top - self.px(24))
        x, y = win.winfo_x(), win.winfo_y()
        if y + h > rect.bottom:
            y = max(rect.top, rect.bottom - h - self.px(16))
        win.geometry(f"{win.winfo_width()}x{h}+{x}+{y}")
        if getattr(win, "_countdown", None) is not None:
            win._countdown.coords("fill", 0, 0, win.winfo_width(), self.px(3))

    def _close_popup(self):
        win, job = self.popup, self.popup_job
        self.popup, self.popup_job = None, None
        if win is not None and win.winfo_exists():
            if job:
                win.after_cancel(job)  # cancelar con el mismo widget que lo programó
            win.destroy()

    def _placement_area(self):
        """Monitor donde va el aviso: el de la posición guardada («Donde lo dejé») si ese monitor sigue
        conectado; si no, el monitor donde está el ratón."""
        st = self.settings
        if st["position"] == "custom" and st.get("x") is not None:
            area = area_containing(st["x"], st["y"], work_areas())
            if area is not None:
                return area
        return work_area()

    def _new_popup(self):
        self._close_popup()
        self.c = THEMES[self.theme_name()]  # sigue el tema elegido / de Windows
        win = tk.Toplevel(self.root, bg=self.c["bg"])
        self.popup = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.0)
        return win

    def _popup_xy(self, w, h, rect):
        """Posición según ajustes, dentro del área `rect`. Por defecto arriba a la derecha: abajo es
        donde salen las notificaciones de Windows (p. ej. la de Recortes) y lo taparían."""
        m = self.px(16)
        pos = self.settings["position"]
        x0, y0 = self.settings.get("x"), self.settings.get("y")
        if pos == "custom" and x0 is not None and area_containing(x0, y0, [rect]):
            return (*clamp_to_area(x0, y0, w, h, rect), 0)
        if pos == "bottom-right":
            return rect.right - w - m, rect.bottom - h - m, self.px(36)
        if pos == "center":
            return (rect.left + rect.right - w) // 2, (rect.top + rect.bottom - h) // 2, self.px(24)
        return rect.right - w - m, rect.top + m, -self.px(36)  # top-right

    def _show_animated(self, win, seconds, can_stay_open=False):
        """Coloca el popup, entra deslizando + fundido, y cuenta atrás con barra."""
        win.update_idletasks()
        rect = self._placement_area()
        w = win.winfo_reqwidth()
        h = min(win.winfo_reqheight(), rect.bottom - rect.top - self.px(24))
        x, y, dy = self._popup_xy(w, h, rect)
        style_window(win, border=self.c["border"])
        steps = 8 if self.settings["animation"] else 0
        win._pinned = can_stay_open and not self.settings["autoclose"]

        def frame(i=0):
            if not win.winfo_exists():
                return
            t = 1 - (1 - i / steps) ** 3 if steps else 1  # ease-out
            win.geometry(f"{w}x{h}+{x}+{int(y + dy * (1 - t))}")
            win.attributes("-alpha", 0.98 * t)
            if i < steps:
                win.after(15, frame, i + 1)

        frame()

        bar = getattr(win, "_countdown", None)
        total = seconds * 1000
        state = {"left": total}

        def tick():
            if not win.winfo_exists():
                return
            px_, py_ = win.winfo_pointerxy()
            inside = win.winfo_rootx() <= px_ < win.winfo_rootx() + w and win.winfo_rooty() <= py_ < win.winfo_rooty() + h
            if win._pinned:  # fijado: no se cierra solo
                state["left"] = total
            elif self._popup_has_focus(win):  # usándolo con el teclado
                pass
            elif not (inside and self.settings["pause_on_hover"]):  # se pausa con el ratón encima
                state["left"] -= 50
            if state["left"] <= 0:
                self._close_popup()
                return
            if bar is not None:
                bar.coords("fill", 0, 0, 0 if win._pinned else w * state["left"] / total, self.px(3))
            self.popup_job = win.after(50, tick)

        self.popup_job = win.after(50, tick)

    def show_popup(self, codes):
        win = self._new_popup()
        c = self.c

        head = tk.Frame(win, bg=c["bg"])
        head.pack(fill="x", padx=self.px(12), pady=(self.px(10), self.px(8)))
        tk.Label(head, image=self._logo(18), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(8)))
        n = len(codes)
        tk.Label(head, text=f"{n} código{'s' if n > 1 else ''} detectado{'s' if n > 1 else ''}",
                 bg=c["bg"], fg=c["fg"], font=self.font(11, "bold")).pack(side="left")
        x = tk.Label(head, text="" if self.icon_font else "✕", bg=c["bg"], fg=c["muted"],
                     font=(self.icon_font, 9) if self.icon_font else self.font(11), cursor="hand2",
                     padx=self.px(6), pady=self.px(4))
        x.pack(side="right")
        x.bind("<Button-1>", lambda e: self.root.after(0, self._close_popup))
        x.bind("<Enter>", lambda e: x.config(fg=c["fg"]))
        x.bind("<Leave>", lambda e: x.config(fg=c["muted"]))
        hist = tk.Label(head, text="" if self.icon_font else "Historial", bg=c["bg"], fg=c["muted"],
                        font=(self.icon_font, 10) if self.icon_font else self.font(8), cursor="hand2",
                        padx=self.px(6), pady=self.px(4))
        hist.pack(side="right", padx=(0, self.px(4)))
        hist.bind("<Button-1>", lambda e: self.root.after(0, lambda: (self._close_popup(), self.show_history())))
        hist.bind("<Enter>", lambda e: hist.config(fg=c["fg"]))
        hist.bind("<Leave>", lambda e: hist.config(fg=c["muted"]))
        gear = tk.Label(head, text="\ue713" if self.icon_font else "⚙", bg=c["bg"], fg=c["muted"],
                        font=(self.icon_font, 10) if self.icon_font else self.font(9), cursor="hand2",
                        padx=self.px(6), pady=self.px(4))
        gear.pack(side="right", padx=(0, self.px(2)))
        gear.bind("<Button-1>", lambda e: self.root.after(0, self.show_settings))
        gear.bind("<Enter>", lambda e: gear.config(fg=c["fg"]))
        gear.bind("<Leave>", lambda e: gear.config(fg=c["muted"]))
        accent = KINDS[parse_payload(codes[0]["text"])[0]][2]
        pin = tk.Label(head, text="" if self.icon_font else "📌", bg=c["bg"], fg=c["muted"],
                       font=(self.icon_font, 10) if self.icon_font else self.font(9), cursor="hand2",
                       padx=self.px(6), pady=self.px(4))
        pin.pack(side="right", padx=(0, self.px(2)))

        def paint_pin():
            pinned = getattr(win, "_pinned", False)
            pin.config(text=("" if pinned else "") if self.icon_font else "📌",
                       fg=accent if pinned else c["muted"])

        def toggle_pin(e):
            win._pinned = not getattr(win, "_pinned", False)
            paint_pin()

        pin.bind("<Button-1>", toggle_pin)
        win.after(10, paint_pin)

        # arrastrar desde la cabecera; la posición se recuerda
        drag = {}

        def press(e):
            drag.update(x=e.x_root - win.winfo_x(), y=e.y_root - win.winfo_y(), moved=False)

        def motion(e):
            if drag:
                drag["moved"] = True
                win.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")

        def release(e):
            if drag.get("moved"):
                self.settings.update(position="custom", x=win.winfo_x(), y=win.winfo_y())
                self.save_settings()
                self.tray.update_menu()
            drag.clear()

        for wdg in (head, *[w for w in head.winfo_children() if w not in (x, hist, pin, gear)]):
            wdg.config(cursor="fleur")
            wdg.bind("<ButtonPress-1>", press)
            wdg.bind("<B1-Motion>", motion)
            wdg.bind("<ButtonRelease-1>", release)

        win._codes = codes
        self._kbd_copy, self._kbd_primary = [], []  # _card los rellena (atajos 1–9 y Enter)
        for code in codes[:MAX_CARDS]:
            self._card(win, code)
        win._kbd_copy, win._kbd_primary = self._kbd_copy, self._kbd_primary
        self._kbd_copy = self._kbd_primary = None
        win._capture_slot = tk.Frame(win, bg=c["bg"])
        if n > MAX_CARDS:
            tk.Label(win, text=f"+{n - MAX_CARDS} más en el historial", bg=c["bg"], fg=c["muted"],
                     font=self.font(8)).pack()

        win._hint = tk.Label(win, text=self.HINT_MOUSE, bg=c["bg"], fg=c["muted"], font=self.font(8))
        win._hint.pack(pady=(0, self.px(6)))
        cd = tk.Canvas(win, height=self.px(3), bg=c["bg"], highlightthickness=0, bd=0)
        cd.pack(fill="x", side="bottom")
        cd.create_rectangle(0, 0, 9999, self.px(3), fill=accent, width=0, tags="fill")
        win._countdown = cd

        win.bind("<Escape>", lambda e: self._close_popup())
        self._bind_keyboard(win)
        self._show_animated(win, self.settings["seconds"], can_stay_open=True)
        self._paint_capture_slot(codes)  # al reabrir desde el historial

    # ---- teclado
    HINT_MOUSE = "Arrástralo desde arriba · 📌 para fijarlo · Esc para cerrar"
    HINT_KEYS = "Enter: acción · 1–9: copiar · Tab: moverse · Esc: cerrar"

    def _bind_keyboard(self, win):
        """El aviso no roba el foco al aparecer. Al tomarlo (atajo global o clic) se maneja con el teclado:
        Enter = acción principal del primer código, 1–9 = copiar ese dato, Ctrl+C = copiar el dato
        principal, Tab = recorrer los botones (Espacio o Enter los pulsa), Esc = cerrar."""
        def in_button_or_text():
            f = win.focus_get()
            return isinstance(f, (tk.Button, tk.Text))

        def primary(e):
            if not in_button_or_text() and win._kbd_primary:
                win._kbd_primary[0].invoke()

        def copy_main(e):
            if not in_button_or_text() and win._kbd_copy:
                win._kbd_copy[0].invoke()

        def copy_n(n):
            if n <= len(win._kbd_copy):
                win._kbd_copy[n - 1].invoke()

        for n in range(1, 10):
            win.bind(f"<Key-{n}>", lambda e, n=n: copy_n(n))
        win.bind("<Return>", primary)
        win.bind("<Control-c>", copy_main)
        win.bind("<FocusIn>", lambda e: self._kbd_mode(win, True))
        win.bind("<FocusOut>", lambda e: win.after(30, lambda: win.winfo_exists() and self._kbd_mode(
            win, self._popup_has_focus(win))))
        win.bind("<ButtonPress-1>", lambda e: win.focus_force(), add="+")

    def _popup_has_focus(self, win):
        f = win.focus_get()
        return f is not None and str(f).startswith(str(win))

    def _kbd_mode(self, win, on):
        """Con el foco en el aviso, los botones «Copiar» muestran su número y la pista cambia."""
        if getattr(win, "_kbd_on", False) == on:
            return
        win._kbd_on = on
        for n, b in enumerate(win._kbd_copy[:9], start=1):
            if b.winfo_exists():
                b.config(text=f"Copiar  {n}" if on else "Copiar")
        win._hint.config(text=self.HINT_KEYS if on else self.HINT_MOUSE)

    def focus_popup(self):
        """Atajo global: pasa el foco al aviso abierto para usarlo con el teclado."""
        win = self.popup
        if win is None or not win.winfo_exists() or not hasattr(win, "_kbd_copy"):
            return
        win._pinned = True  # mientras se usa con el teclado no se cierra solo
        force_foreground(user32.GetParent(win.winfo_id()))
        win.focus_force()

    def toast(self, msg, seconds=3):
        win = self._new_popup()
        c = self.c
        tk.Label(win, text=msg, bg=c["bg"], fg=c["fg"], font=self.font(10), padx=self.px(16),
                 pady=self.px(12), justify="left").pack()
        cd = tk.Canvas(win, height=self.px(3), bg=c["bg"], highlightthickness=0, bd=0)
        cd.pack(fill="x", side="bottom")
        cd.create_rectangle(0, 0, 9999, self.px(3), fill=KINDS["link"][2], width=0, tags="fill")
        win._countdown = cd
        win.bind("<Button-1>", lambda e: self._close_popup())
        self._show_animated(win, seconds)

    def _paint_capture_slot(self, codes):
        """Línea del aviso sobre el archivo de la captura: ya borrado, o botón para borrarlo."""
        win = self.popup
        if win is None or not win.winfo_exists() or getattr(win, "_codes", None) is not codes:
            return
        path = codes[0].get("capture")
        slot = win._capture_slot
        for w in slot.winfo_children():
            w.destroy()
        if not path:
            return
        c = self.c
        g = "\ue74d" if self.icon_font else "🗑"
        gf = (self.icon_font, 9) if self.icon_font else self.font(9)
        tk.Label(slot, text=g, font=gf, bg=c["bg"], fg=c["muted"]).pack(side="left", padx=(0, self.px(6)))
        msg = tk.Label(slot, bg=c["bg"], fg=c["muted"], font=self.font(9), anchor="w")
        msg.pack(side="left", fill="x", expand=True)
        if codes[0].get("capture_deleted"):
            msg.config(text="Captura enviada a la Papelera")
        elif os.path.exists(path):
            msg.config(text=f"Captura guardada: {shorten(os.path.basename(path), 34, middle=True)}")
            b = self._button(slot, "Borrar captura")

            def delete():
                ok = send_to_recycle_bin(path)
                for code in codes:
                    code["capture_deleted"] = ok
                if ok:
                    self._paint_capture_slot(codes)
                else:
                    self._flash(b, "No se pudo borrar", ok=False)

            b.config(command=delete)
            b.pack(side="right")
        else:
            msg.config(text="La captura ya no está en la carpeta")
        slot.pack(fill="x", padx=self.px(14), pady=(0, self.px(8)), before=win._hint)
        self._refit_popup()
