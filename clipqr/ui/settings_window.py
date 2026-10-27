"""Ventana de configuración."""
import time
import tkinter as tk

from clipqr.settings import (HOTKEY_CREATE_CHOICES, HOTKEY_FOCUS_CHOICES, HOTKEY_REGION_CHOICES, error_report,
                             hotkey_label)

from PIL import Image, ImageTk

from clipqr import APP_NAME, DONATE_URL, VERSION
from clipqr.i18n import LANGUAGES, _
from clipqr.icons import make_icon
from clipqr.platform import PACKAGED, open_path, style_window
from clipqr.ui.system_texts import (autostart_label, copied_files_hint, delete_capture_hint, hotkeys_problem,
                                    theme_auto_label)
from clipqr.ui.theme import KINDS, THEMES


class SettingsWindowMixin:
    def show_settings(self):
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.deiconify()
            self.settings_win.lift()
            self.settings_win.focus_force()
            return
        self.c = THEMES[self.theme_name()]
        c, st = self.c, self.settings
        win = tk.Toplevel(self.root, bg=c["bg"])
        self.settings_win = win
        win.title(f"{APP_NAME} · {_('Configuración')}")
        win.geometry(f"{self.px(500)}x{self.px(680)}")
        win.minsize(self.px(420), self.px(360))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")

        self._window_header(win, _("Configuración"), _("{app} {version} · los cambios se guardan al momento",
                                                              app=APP_NAME, version=VERSION))

        wrap = tk.Frame(win, bg=c["bg"])
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        body = tk.Frame(canvas, bg=c["bg"])
        wid = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(wid, width=e.width))
        self._bind_wheel(win, canvas)
        win.bind("<Escape>", lambda e: win.destroy())

        def section(title):
            tk.Label(body, text=title, bg=c["bg"], fg=c["muted"], font=self.font(9, "bold")).pack(
                anchor="w", padx=self.px(18), pady=(self.px(10), self.px(4)))
            card = tk.Frame(body, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
            card.pack(fill="x", padx=self.px(16))
            return card

        def row(card, title, hint=None, control=None, stacked=False):
            """Fila: texto a la izquierda y control a la derecha (o debajo si stacked)."""
            if card.winfo_children():
                tk.Frame(card, bg=c["border"], height=1).pack(fill="x")
            r = tk.Frame(card, bg=c["card"])
            r.pack(fill="x", padx=self.px(12), pady=self.px(8))
            if control and not stacked:  # el control se coloca antes para que el texto no lo empuje fuera
                control(r).pack(side="right", anchor="e", padx=(self.px(8), 0))
            txt = tk.Frame(r, bg=c["card"])
            txt.pack(side="top" if stacked else "left", fill="x", expand=True, anchor="w")
            tk.Label(txt, text=title, bg=c["card"], fg=c["fg"], font=self.font(10), anchor="w").pack(anchor="w")
            if hint:
                tk.Label(txt, text=hint, bg=c["card"], fg=c["muted"], font=self.font(8), anchor="w",
                         justify="left", wraplength=self.px(260)).pack(anchor="w")
            if control and stacked:
                control(r).pack(side="top", anchor="w", pady=(self.px(6), 0))

        save = lambda **kw: self.set_setting(**kw)

        def fmt_seconds(v):
            if v < 60:
                return f"{v} s"
            return f"{v // 60} min" if v % 60 == 0 else f"{v / 60:.1f} min"

        card = section(_("AVISO"))
        row(card, _("Tiempo visible"), _("Cuánto tarda en cerrarse solo."),
            lambda p: self._stepper(p, [5, 10, 15, 20, 25, 30, 45, 60, 90, 120, 180, 300], st["seconds"],
                                    fmt_seconds, lambda v: save(seconds=v)))
        row(card, _("Cerrar solo"), _("Si lo desactivas, el aviso queda abierto hasta que lo cierres."),
            lambda p: self._switch(p, st["autoclose"], lambda v: save(autoclose=v)))
        row(card, _("Pausar con el ratón encima"), _("La cuenta atrás se detiene mientras lo señalas."),
            lambda p: self._switch(p, st["pause_on_hover"], lambda v: save(pause_on_hover=v)))
        row(card, _("Animación de entrada"), None,
            lambda p: self._switch(p, st["animation"], lambda v: save(animation=v)))
        row(card, _("Posición"), _("También puedes arrastrarlo desde su cabecera."),
            lambda p: self._segmented(p, [("top-right", _("Arriba dcha."), True),
                                          ("bottom-right", _("Abajo dcha."), True),
                                          ("center", _("Centro"), True),
                                          ("custom", _("Donde lo dejé"), st.get("x") is not None)],
                                      st["position"], lambda v: save(position=v)), stacked=True)
        row(card, _("Probar"), _("Muestra un aviso de ejemplo con estos ajustes."),
            lambda p: self._button(p, _("Ver aviso de prueba"), cmd=lambda: self.show_popup([{
                "format": "QRCode", "text": "https://github.com/zxing-cpp/zxing-cpp",
                "thumb": Image.alpha_composite(Image.new("RGBA", (96, 96), "white"), make_icon(size=96)).convert("RGB"),
                "time": time.time()}])))

        card = section(_("APARIENCIA"))

        def set_theme(v):
            save(theme=v)
            win.destroy()
            self.root.after(50, self.show_settings)  # se redibuja con el tema nuevo

        row(card, _("Tema"), None,
            lambda p: self._segmented(p, [("auto", theme_auto_label(), True), ("light", _("Claro"), True),
                                          ("dark", _("Oscuro"), True)], st["theme"], set_theme), stacked=True)

        card = section(_("DETECCIÓN"))
        row(card, _("Solo códigos QR"), _("Desactivado: también lee códigos de barras (EAN, Code 128, DataMatrix…)."),
            lambda p: self._switch(p, st["qr_only"], lambda v: save(qr_only=v)))
        row(card, _("Leer archivos copiados"), copied_files_hint(),
            lambda p: self._switch(p, st["explorer_files"], lambda v: save(explorer_files=v)))
        row(card, _("Borrar las capturas con QR"), delete_capture_hint(),
            lambda p: self._switch(p, st["delete_capture"], lambda v: save(delete_capture=v)))
        row(card, _("Mostrar contraseñas al momento"), _("Contraseñas Wi‑Fi y secretos 2FA visibles sin pulsar el ojo. "
            "Desactivado es más seguro si alguien mira tu pantalla."),
            lambda p: self._switch(p, st["show_passwords"], lambda v: save(show_passwords=v)))
        row(card, _("Sonido al detectar"), None,
            lambda p: self._switch(p, st["sound"], lambda v: save(sound=v)))
        row(card, _("Pausar la detección"), _("No se escanea el portapapeles hasta que lo reactives."),
            lambda p: self._switch(p, self.paused, lambda v: self.paused != v and self.toggle_pause()))

        card = section(_("HISTORIAL"))

        def set_max(v):
            save(history_max=v)
            del self.history[v:]
            self.tray.update_menu()

        row(card, _("Guardar hasta"), _("Escaneos que se recuerdan mientras ClipQR está abierto."),
            lambda p: self._stepper(p, [10, 25, 50, 100, 200], st["history_max"], str, set_max))

        def clear_button(p):
            b = self._button(p, _("Borrar historial"))

            def clear():
                self.history.clear()
                self.tray.update_menu()
                if self.history_win is not None and self.history_win.winfo_exists():
                    self._fill_history()
                self._flash(b, _("✓ Borrado"))

            b.config(command=clear)
            return b

        row(card, _("Borrar todo el historial"), None, clear_button)

        card = section(_("ATAJOS DE TECLADO"))
        problem = hotkeys_problem(getattr(self.hotkeys, "reason", None))
        if problem:  # macOS sin permiso de Accesibilidad, Wayland, sin pynput
            tk.Label(card, text=problem, bg=c["warn_bg"], fg=c["warn_fg"], font=self.font(9), anchor="w",
                     justify="left", wraplength=self.px(420)).pack(fill="x", ipadx=self.px(10), ipady=self.px(6))

        def set_hotkey(**kw):
            save(**kw)
            self.apply_hotkeys(retries=0)  # elegido a mano: avisar al momento si está ocupado

        row(card, _("Escanear una zona de la pantalla"),
            _("Congela la pantalla y lees el código que rodees, sin capturas ni portapapeles."),
            lambda p: self._segmented(p, [(k, hotkey_label(k), True) for k in HOTKEY_REGION_CHOICES],
                                      st["hotkey_region"], lambda v: set_hotkey(hotkey_region=v)), stacked=True)
        row(card, _("Crear un QR"), _("Abre «Crear QR» con lo que tengas copiado."),
            lambda p: self._segmented(p, [(k, hotkey_label(k), True) for k in HOTKEY_CREATE_CHOICES],
                                      st["hotkey_create"], lambda v: set_hotkey(hotkey_create=v)), stacked=True)
        row(card, _("Usar el aviso con el teclado"),
            _("Pasa el foco al aviso abierto. Luego: Enter = acción, 1–9 = copiar ese dato, Tab = moverse, Esc = cerrar."),
            lambda p: self._segmented(p, [(k, hotkey_label(k), True) for k in HOTKEY_FOCUS_CHOICES],
                                      st["hotkey_focus"], lambda v: set_hotkey(hotkey_focus=v)), stacked=True)

        card = section(_("GENERAL"))

        def language_control(p):
            box = tk.Frame(p, bg=p.cget("bg"))
            restart = self._button(box, _("Reiniciar ahora"), color=KINDS["link"][2], cmd=self.restart)

            def set_language(v):
                save(language=v)
                if v != self.started_language:
                    restart.pack(side="top", anchor="w", pady=(self.px(6), 0))
                else:
                    restart.pack_forget()

            options = [("auto", _("Automático (idioma del sistema)"))] + list(LANGUAGES.items())
            self._dropdown(box, options, st["language"], set_language).pack(side="top", anchor="w")
            if st["language"] != self.started_language:
                restart.pack(side="top", anchor="w", pady=(self.px(6), 0))
            return box

        # en los dos idiomas, para quien lo haya puesto por error en uno que no entiende
        row(card, "Idioma · Language", _("El idioma nuevo se aplica al reiniciar ClipQR."), language_control,
            stacked=True)
        row(card, autostart_label(), None,
            lambda p: self._switch(p, self.autostart_enabled(),
                                   lambda v: self.autostart_enabled() != v and self.toggle_autostart()))
        row(card, _("Avisar al iniciar"), _("Un aviso breve confirma que ClipQR está activo cuando se abre."),
            lambda p: self._switch(p, st["startup_notice"], lambda v: save(startup_notice=v)))
        def report_button(p):
            b = self._button(p, _("Copiar informe"))
            b.config(command=lambda: self.copy(error_report(VERSION), b))
            return b

        row(card, _("Informe de errores"), _("Copia la versión y los últimos errores para pegarlos en una incidencia "
            "de GitHub. No incluye imágenes ni el contenido de tus códigos; no se envía nada."), report_button)
        if not PACKAGED:  # la versión de la Store la actualiza la Store
            row(card, _("Buscar actualizaciones"),
                _("Una vez al día consulta las versiones publicadas en GitHub. Solo se instalan si las aceptas, "
                  "y antes se comprueba que el instalador no está alterado."),
                lambda p: self._switch(p, st["check_updates"], lambda v: save(check_updates=v)))
            row(card, _("Buscar ahora"), _("Versión instalada: {version}", version=VERSION),
                lambda p: self._button(p, _("Buscar actualizaciones"), cmd=lambda: self.check_updates(manual=True)))

        card = section(_("APOYAR CLIPQR"))
        row(card, _("Invitar un cafecito ☕"), _("ClipQR es gratis y de código abierto. Si te sirve, puedes apoyarlo "
            "con un cafecito en cafecito.app."),
            lambda p: self._button(p, _("Invitar un cafecito ↗"), cmd=lambda: open_path(DONATE_URL)))

        tk.Label(body, text=_("Los cambios se guardan al momento."), bg=c["bg"], fg=c["muted"],
                 font=self.font(8)).pack(pady=self.px(14))
