"""El aviso que aparece al detectar un código."""
import os
import tkinter as tk


from clipqr.i18n import N_, _
from clipqr.icons import make_icon
from clipqr.payloads import analyze, format_name, headline, parse_payload, shorten
from clipqr.ui.theme import KINDS, THEMES
from clipqr.platform import (SYSTEM, area_containing, bring_to_front, clamp_to_area, send_to_trash,
                             style_window, work_area, work_areas)

MAX_CARDS = 4


class PopupMixin:
    def _card(self, parent, code):
        """Tarjeta de un código, pensada para leerse de un vistazo: el dato principal en grande,
        la acción principal justo debajo, el resto de datos compactos y el texto crudo plegado."""
        c = self.c
        r = analyze(code["text"])
        kind, title, items, actions = r.kind, r.title, r.items, r.actions
        accent = KINDS[kind][2]
        text = code["text"]
        head_label, head_value = r.headline or headline(kind, items, text)
        if kind == "link" and not r.headline:  # el enlace entero, no solo el dominio (que va en los datos)
            head_label, head_value = _("Enlace"), text
        rows = [(l, v) for l, v in items if (l, v) != (head_label, head_value)]
        if head_value != text and head_value not in (v for _l, v in rows):
            rows.insert(0, (head_label, head_value))  # el dato principal también se puede copiar solo

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
        b_head = self._button(top, _("Copiar todo"), color=accent)
        b_head.config(command=lambda: self.copy(text, b_head))
        b_head.pack(side="right", anchor="n")
        copy_buttons = [b_head]  # para los atajos 1–9: el QR entero y luego cada dato, en orden
        head = tk.Frame(top, bg=c["card"])
        head.pack(side="left", fill="x", expand=True)
        meta = tk.Frame(head, bg=c["card"])
        meta.pack(anchor="w")
        g, gf = self.glyph(kind)
        tk.Label(meta, text=g, font=(gf[0], 10), bg=c["card"], fg=accent).pack(side="left", padx=(0, self.px(5)))
        tk.Label(meta, text=title.upper(), bg=c["card"], fg=accent, font=self.font(8, "bold")).pack(side="left")
        if " · " not in title:  # «Factura · ARCA» ya ocupa la línea: el tipo de código sobra
            tk.Label(meta, text=f"  ·  {format_name(code['format'])}", bg=c["card"], fg=c["muted"],
                     font=self.font(8)).pack(side="left")
        if head_value != text:  # si el dato principal es el QR entero, ya se ve abajo en grande
            tk.Label(head, text=shorten(head_value, 70), bg=c["card"], fg=c["fg"], font=self.font(15, "bold"),
                     anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")
        subtitle = r.subtitle
        if subtitle:  # p. ej. «Factura B · 0003-00001234 · fecha»
            tk.Label(head, text=subtitle, bg=c["card"], fg=c["muted"], font=self.font(9),
                     anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")

        # el contenido entero del QR, a la vista y seleccionable para copiar solo una parte
        self._full_text(inner, text, accent, large=head_value == text)

        # avisos (enlaces sospechosos, datos que no cuadran…) justo antes de los botones
        warnings = r.warnings + code.get("warnings", [])
        if warnings:
            self._warning_strip(inner, warnings, r.warning_level)

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


    def _full_text(self, parent, text, accent, large=False):
        """Todo el contenido del QR, visible y seleccionable: arrastrar, doble clic (palabra), triple clic
        (línea) o Ctrl+A. Ctrl+C o «Copiar selección» copian lo seleccionado; Ctrl+C sin selección, todo."""
        c = self.c
        if not getattr(self, "_word_chars_set", False):
            # doble clic = una palabra entre símbolos (el número de «wa.me/549…?text=», un parámetro de una URL),
            # no todo lo que haya entre espacios, que en un enlace es el enlace entero
            self.root.tk.eval("catch {tcl_endOfWord}; set tcl_wordchars {\\w}; set tcl_nonwordchars {\\W}")
            self._word_chars_set = True
        frame = tk.Frame(parent, bg=c["card"])
        frame.pack(fill="x", pady=(self.px(8), 0))
        per_line = 38 if large else 46  # el QR entero como dato principal va más grande
        lines = min(max(text.count("\n") + 1, len(text) // per_line + 1), 4)
        txt = tk.Text(frame, height=lines, width=per_line, wrap="word" if " " in text else "char", bg=c["textbg"],
                      fg=c["fg"], relief="flat", font=self.mono(12 if large else 10), padx=self.px(6),
                      pady=self.px(4),
                      selectbackground=accent, selectforeground="white", inactiveselectbackground=accent,
                      highlightthickness=0, bd=0, cursor="xterm")
        txt.insert("1.0", text)
        txt.config(state="disabled")  # solo lectura; seleccionar y copiar siguen funcionando
        txt.pack(fill="x")
        bar = tk.Frame(frame, bg=c["card"])
        bar.pack(fill="x", pady=(self.px(3), 0))
        tk.Label(bar, text=_("Selecciona una parte con el ratón y pulsa Ctrl+C"), bg=c["card"], fg=c["muted"],
                 font=self.font(8)).pack(side="left")
        b_sel = self._button(bar, _("Copiar selección"))
        b_sel.pack(side="right")

        def copy_sel(e=None):
            try:
                part = txt.get("sel.first", "sel.last")
            except tk.TclError:
                part = ""
            if part:
                self.copy(part, b_sel)
            elif e is not None:
                self.copy(text, b_sel)
            else:
                self._flash(b_sel, _("Selecciona texto arriba"), ok=False)
            return "break"

        def activate(e):
            win = txt.winfo_toplevel()
            win._pinned = True  # no se cierra solo mientras eliges qué copiar
            self._take_focus(win)
            txt.focus_set()

        def select_all(e):
            txt.tag_add("sel", "1.0", "end-1c")
            return "break"

        b_sel.config(command=copy_sel)
        txt._copy_selection = copy_sel  # Ctrl+C en cualquier parte del aviso copia primero lo seleccionado
        top = parent.winfo_toplevel()
        top._full_texts = getattr(top, "_full_texts", []) + [txt]
        txt.bind("<ButtonPress-1>", activate, add="+")
        copy_keys = ("<Control-c>", "<Control-C>", "<Control-Insert>")
        if SYSTEM == "macos":
            copy_keys += ("<Command-c>", "<Command-C>")
        for seq in copy_keys:
            txt.bind(seq, copy_sel)
        txt.bind("<Control-a>", select_all)
        txt.bind("<Control-A>", select_all)
        return txt

    def _take_focus(self, win):
        """Da el foco de teclado al aviso. Windows no deja que una ventana sin barra de título lo tome solo
        con un clic: hace falta traerla al frente como con el atajo."""
        if win is not None and win.winfo_exists():
            bring_to_front(win)
            if not self._popup_has_focus(win):  # sin quitarle el foco al cuadro de texto donde se hizo clic
                win.focus_force()

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
        win._h = h
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
            # alto actual (puede crecer mientras entra, p. ej. al aparecer «Borrar captura»)
            win.geometry(f"{w}x{getattr(win, '_h', h)}+{x}+{int(y + dy * (1 - t))}")
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
        tk.Label(head, text=_("1 código detectado") if n == 1 else _("{n} códigos detectados", n=n),
                 bg=c["bg"], fg=c["fg"], font=self.font(11, "bold")).pack(side="left")
        x = tk.Label(head, text="" if self.icon_font else "✕", bg=c["bg"], fg=c["muted"],
                     font=(self.icon_font, 9) if self.icon_font else self.font(11), cursor="hand2",
                     padx=self.px(6), pady=self.px(4))
        x.pack(side="right")
        x.bind("<Button-1>", lambda e: self.root.after(0, self._close_popup))
        x.bind("<Enter>", lambda e: x.config(fg=c["fg"]))
        x.bind("<Leave>", lambda e: x.config(fg=c["muted"]))
        hist = tk.Label(head, text="" if self.icon_font else _("Historial"), bg=c["bg"], fg=c["muted"],
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
                win._pinned = True  # si lo has movido es que lo estás usando: este aviso queda fijado
                paint_pin()
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
            tk.Label(win, text=_("+{n} más en el historial", n=n - MAX_CARDS), bg=c["bg"], fg=c["muted"],
                     font=self.font(8)).pack()

        win._hint = tk.Label(win, text=_(self.HINT_MOUSE), bg=c["bg"], fg=c["muted"], font=self.font(8))
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
    HINT_MOUSE = N_("Arrástralo desde arriba · 📌 para fijarlo · Esc para cerrar")
    HINT_KEYS = N_("Enter: acción · 1–9: copiar · Supr: borrar captura · Esc: cerrar")

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
            for txt in getattr(win, "_full_texts", []):
                if txt.winfo_exists() and txt.tag_ranges("sel"):
                    return txt._copy_selection(e)
            if not in_button_or_text() and win._kbd_copy:
                win._kbd_copy[0].invoke()

        def copy_n(n):
            if n <= len(win._kbd_copy):
                win._kbd_copy[n - 1].invoke()

        for n in range(1, 10):
            win.bind(f"<Key-{n}>", lambda e, n=n: copy_n(n))
        win.bind("<Delete>", lambda e: getattr(win, "_delete_capture", None) and win._delete_capture())
        win.bind("<Return>", primary)
        win.bind("<Control-c>", copy_main)
        win.bind("<FocusIn>", lambda e: self._kbd_mode(win, True))
        win.bind("<FocusOut>", lambda e: win.after(30, lambda: win.winfo_exists() and self._kbd_mode(
            win, self._popup_has_focus(win))))
        win.bind("<ButtonPress-1>", lambda e: self._take_focus(win), add="+")

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
                b.config(text=_("Copiar  {n}", n=n) if on else _("Copiar"))
        win._hint.config(text=_(self.HINT_KEYS if on else self.HINT_MOUSE))

    def focus_popup(self):
        """Atajo global: pasa el foco al aviso abierto para usarlo con el teclado."""
        win = self.popup
        if win is None or not win.winfo_exists() or not hasattr(win, "_kbd_copy"):
            return
        win._pinned = True  # mientras se usa con el teclado no se cierra solo
        bring_to_front(win)
        win.focus_force()

    def notice(self, title, text, buttons, seconds=60):
        """Aviso con título, texto y botones [(texto, función, principal)]. Para avisos de la propia app
        (actualizaciones…), no de códigos."""
        win = self._new_popup()
        c = self.c
        head = tk.Frame(win, bg=c["bg"])
        head.pack(fill="x", padx=self.px(14), pady=(self.px(12), self.px(4)))
        tk.Label(head, image=self._logo(22), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(10)))
        tk.Label(head, text=title, bg=c["bg"], fg=c["fg"], font=self.font(12, "bold")).pack(side="left")
        tk.Label(win, text=text, bg=c["bg"], fg=c["muted"], font=self.font(9), justify="left", anchor="w",
                 wraplength=self.px(360)).pack(fill="x", padx=self.px(14))
        bar = tk.Frame(win, bg=c["bg"])
        bar.pack(fill="x", padx=self.px(14), pady=(self.px(10), self.px(12)))
        for label, fn, primary in buttons:
            b = self._button(bar, label, color=KINDS["link"][2] if primary else None)
            b.config(command=lambda fn=fn, b=b: fn(b))
            b.pack(side="left", padx=(0, self.px(6)))
        cd = tk.Canvas(win, height=self.px(3), bg=c["bg"], highlightthickness=0, bd=0)
        cd.pack(fill="x", side="bottom")
        cd.create_rectangle(0, 0, 9999, self.px(3), fill=KINDS["link"][2], width=0, tags="fill")
        win._countdown = cd
        win.bind("<Escape>", lambda e: self._close_popup())
        self._show_animated(win, seconds)
        return win

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
        pending = codes[0].get("capture_pending")
        slot = win._capture_slot
        for w in slot.winfo_children():
            w.destroy()
        win._delete_capture = None
        if not path and not pending:
            if slot.winfo_ismapped():
                slot.pack_forget()
                self._refit_popup()
            return
        c = self.c
        g = "" if self.icon_font else "🗑"
        gf = (self.icon_font, 10) if self.icon_font else self.font(10)
        icon = tk.Label(slot, text=g, font=gf, bg=c["bg"], fg=c["muted"])
        icon.pack(side="left", padx=(0, self.px(6)))
        msg = tk.Label(slot, bg=c["bg"], fg=c["muted"], font=self.font(9), anchor="w", justify="left")
        msg.pack(side="left", fill="x", expand=True)
        if pending:
            msg.config(text=_("Buscando la captura guardada…"))
        elif codes[0].get("capture_deleted"):
            msg.config(text=_("Captura enviada a la Papelera"), fg=c["fg"])
            icon.config(fg=c["ok"])
        elif os.path.exists(path):
            msg.config(text=_("Captura: {archivo}", archivo=shorten(os.path.basename(path), 22, middle=True)))

            def delete(always=False):
                if always:  # a partir de ahora, solas
                    self.set_setting(delete_capture=True)
                ok = send_to_trash(path)
                for code in codes:
                    code["capture_deleted"] = ok
                if ok:
                    self._paint_capture_slot(codes)
                else:
                    self._flash(b, _("No se pudo borrar"), ok=False)

            always = self._button(slot, _("Borrar siempre"), cmd=lambda: delete(always=True))
            always.pack(side="right", padx=(self.px(6), 0))
            b = self._button(slot, _("🗑 Borrar captura"), color="#d64545", cmd=delete)
            b.pack(side="right")
            win._delete_capture = delete  # tecla Supr
        else:
            msg.config(text=_("La captura ya no está en la carpeta"))
        slot.pack(fill="x", padx=self.px(14), pady=(0, self.px(8)), before=win._hint)
        self._refit_popup()
