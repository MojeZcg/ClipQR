"""Ventana de configuración."""
import time
import tkinter as tk

from clipqr.settings import HOTKEY_FOCUS_CHOICES, HOTKEY_REGION_CHOICES, hotkey_label

from PIL import Image, ImageTk

from clipqr import APP_NAME, VERSION
from clipqr.icons import make_icon
from clipqr.ui.theme import THEMES
from clipqr.winplatform import PACKAGED, style_window


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
        win.title(f"{APP_NAME} · Configuración")
        win.geometry(f"{self.px(500)}x{self.px(680)}")
        win.minsize(self.px(420), self.px(360))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")

        self._window_header(win, "Configuración", f"{APP_NAME} {VERSION} · los cambios se guardan al momento")

        wrap = tk.Frame(win, bg=c["bg"])
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        body = tk.Frame(canvas, bg=c["bg"])
        wid = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(wid, width=e.width))
        win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
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

        card = section("AVISO")
        row(card, "Tiempo visible", "Cuánto tarda en cerrarse solo.",
            lambda p: self._stepper(p, [5, 10, 15, 20, 25, 30, 45, 60, 90, 120, 180, 300], st["seconds"],
                                    fmt_seconds, lambda v: save(seconds=v)))
        row(card, "Cerrar solo", "Si lo desactivas, el aviso queda abierto hasta que lo cierres.",
            lambda p: self._switch(p, st["autoclose"], lambda v: save(autoclose=v)))
        row(card, "Pausar con el ratón encima", "La cuenta atrás se detiene mientras lo señalas.",
            lambda p: self._switch(p, st["pause_on_hover"], lambda v: save(pause_on_hover=v)))
        row(card, "Animación de entrada", None,
            lambda p: self._switch(p, st["animation"], lambda v: save(animation=v)))
        row(card, "Posición", "También puedes arrastrarlo desde su cabecera.",
            lambda p: self._segmented(p, [("top-right", "Arriba dcha.", True), ("bottom-right", "Abajo dcha.", True),
                                          ("center", "Centro", True),
                                          ("custom", "Donde lo dejé", st.get("x") is not None)],
                                      st["position"], lambda v: save(position=v)), stacked=True)
        row(card, "Probar", "Muestra un aviso de ejemplo con estos ajustes.",
            lambda p: self._button(p, "Ver aviso de prueba", cmd=lambda: self.show_popup([{
                "format": "QRCode", "text": "https://github.com/zxing-cpp/zxing-cpp",
                "thumb": Image.alpha_composite(Image.new("RGBA", (96, 96), "white"), make_icon(size=96)).convert("RGB"),
                "time": time.time()}])))

        card = section("APARIENCIA")

        def set_theme(v):
            save(theme=v)
            win.destroy()
            self.root.after(50, self.show_settings)  # se redibuja con el tema nuevo

        row(card, "Tema", None,
            lambda p: self._segmented(p, [("auto", "Como Windows", True), ("light", "Claro", True),
                                          ("dark", "Oscuro", True)], st["theme"], set_theme), stacked=True)

        card = section("DETECCIÓN")
        row(card, "Solo códigos QR", "Desactivado: también lee códigos de barras (EAN, Code 128, DataMatrix…).",
            lambda p: self._switch(p, st["qr_only"], lambda v: save(qr_only=v)))
        row(card, "Leer archivos copiados", "Imágenes copiadas desde el Explorador de archivos.",
            lambda p: self._switch(p, st["explorer_files"], lambda v: save(explorer_files=v)))
        row(card, "Borrar las capturas con QR",
            "Envía a la Papelera la captura que Windows guarda en Imágenes › Capturas de pantalla. "
            "Si está desactivado, el aviso muestra un botón para hacerlo.",
            lambda p: self._switch(p, st["delete_capture"], lambda v: save(delete_capture=v)))
        row(card, "Sonido al detectar", None,
            lambda p: self._switch(p, st["sound"], lambda v: save(sound=v)))
        row(card, "Pausar la detección", "No se escanea el portapapeles hasta que lo reactives.",
            lambda p: self._switch(p, self.paused, lambda v: self.paused != v and self.toggle_pause()))

        card = section("HISTORIAL")

        def set_max(v):
            save(history_max=v)
            del self.history[v:]
            self.tray.update_menu()

        row(card, "Guardar hasta", "Escaneos que se recuerdan mientras ClipQR está abierto.",
            lambda p: self._stepper(p, [10, 25, 50, 100, 200], st["history_max"], str, set_max))

        def clear_button(p):
            b = self._button(p, "Borrar historial")

            def clear():
                self.history.clear()
                self.tray.update_menu()
                if self.history_win is not None and self.history_win.winfo_exists():
                    self._fill_history()
                self._flash(b, "✓ Borrado")

            b.config(command=clear)
            return b

        row(card, "Borrar todo el historial", None, clear_button)

        card = section("ATAJOS DE TECLADO")

        def set_hotkey(**kw):
            save(**kw)
            self.apply_hotkeys(retries=0)  # elegido a mano: avisar al momento si está ocupado

        row(card, "Escanear una zona de la pantalla",
            "Congela la pantalla y lees el código que rodees, sin capturas ni portapapeles.",
            lambda p: self._segmented(p, [(k, hotkey_label(k), True) for k in HOTKEY_REGION_CHOICES],
                                      st["hotkey_region"], lambda v: set_hotkey(hotkey_region=v)), stacked=True)
        row(card, "Usar el aviso con el teclado",
            "Pasa el foco al aviso abierto. Luego: Enter = acción, 1–9 = copiar ese dato, Tab = moverse, Esc = cerrar.",
            lambda p: self._segmented(p, [(k, hotkey_label(k), True) for k in HOTKEY_FOCUS_CHOICES],
                                      st["hotkey_focus"], lambda v: set_hotkey(hotkey_focus=v)), stacked=True)

        card = section("GENERAL")
        row(card, "Iniciar con Windows", None,
            lambda p: self._switch(p, self.autostart_enabled(),
                                   lambda v: self.autostart_enabled() != v and self.toggle_autostart()))
        if not PACKAGED:  # la versión de la Store la actualiza la Store
            row(card, "Buscar actualizaciones",
                "Una vez al día consulta las versiones publicadas en GitHub. Solo se instalan si las aceptas, "
                "y antes se comprueba que el instalador no está alterado.",
                lambda p: self._switch(p, st["check_updates"], lambda v: save(check_updates=v)))
            row(card, "Buscar ahora", f"Versión instalada: {VERSION}",
                lambda p: self._button(p, "Buscar actualizaciones", cmd=lambda: self.check_updates(manual=True)))

        tk.Label(body, text="Los cambios se guardan al momento.", bg=c["bg"], fg=c["muted"],
                 font=self.font(8)).pack(pady=self.px(14))
