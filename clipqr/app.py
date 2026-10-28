"""Aplicación: bandeja del sistema, vigilancia del portapapeles y acciones."""
import hashlib
import os
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont

from PIL import Image

from clipqr import APP_NAME, DONATE_URL
from clipqr.actions import connect_wifi, find_saved_capture, open_with_default_app
from clipqr.decode import decode_image, grab_clipboard_images, make_thumb
from clipqr.icons import make_icon
from clipqr.payloads import analyze, parse_payload
from clipqr.i18n import _, set_language
from clipqr.settings import (CONFIG_DIR, FIRST_RUN_MARK, SETTINGS_FILE, hotkey_label, load_settings, load_state,
                             log_exception, save_state)
from clipqr.ui.create_qr import CreateQRMixin
from clipqr.ui.history import HistoryMixin
from clipqr.ui.popup import PopupMixin
from clipqr.ui.region import RegionMixin
from clipqr.ui.update_flow import UpdateMixin
from clipqr.ui.settings_window import SettingsWindowMixin
from clipqr.ui.theme import THEMES
from clipqr.ui.system_texts import autostart_label, first_run_text, hotkeys_problem
from clipqr.ui.widgets import WidgetsMixin
from clipqr.platform import (CLIPBOARD_POLL_MS, FROZEN, PACKAGED, SYSTEM, HotkeyManager, autostart_current,
                             autostart_entry, autostart_remove, autostart_set, beep, bind_tk, clipboard_token,
                             clipboard_tools_missing, enable_dpi_awareness, gui_python, installed_by_setup,
                             msix_set_startup, msix_startup_state, open_path, pick_fonts, prepare_app,
                             release_single_instance, screen_scale, send_to_trash, single_instance, start_tray,
                             system_theme, tray_is_dark, tray_options, uninstall_program, uninstall_registration)

POLL_MS = CLIPBOARD_POLL_MS  # Windows: GetClipboardSequenceNumber es casi gratis, se puede mirar a menudo
FALLBACK_POLL_MS = 1000  # sin forma de saber si cambió el portapapeles: se lee la imagen y se compara


class NullTray:
    """Sustituto del icono cuando no hay bandeja del sistema (o no se pudo crear): ClipQR sigue funcionando
    y se maneja desde la ventana del historial."""
    HAS_MENU = False
    icon = title = None
    visible = False

    def update_menu(self):
        pass

    def stop(self):
        pass


class ClipQR(PopupMixin, RegionMixin, UpdateMixin, CreateQRMixin, HistoryMixin, SettingsWindowMixin, WidgetsMixin):
    def __init__(self, autostart=False):
        self.autostart_launch = autostart  # abierto por el inicio de Windows (no a mano)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title(APP_NAME)
        self.root.report_callback_exception = log_exception
        bind_tk(self.root)
        prepare_app(self.root)
        self.dpi = screen_scale(self.root)
        families = set(tkfont.families(self.root))
        self.ui_font, self.icon_font, self.mono_font = pick_fonts(families)
        if self.ui_font.startswith("Tk") or self.mono_font.startswith("Tk"):  # sin las fuentes habituales:
            self.ui_font, self.mono_font = (tkfont.nametofont(f).actual("family") if f.startswith("Tk") else f
                                            for f in (self.ui_font, self.mono_font))  # las de Tk por defecto
        self.paused = False
        self.settings = load_settings()
        set_language(self.settings["language"])
        self.started_language = self.settings["language"]  # el idioma cambia al reiniciar
        self.c = THEMES[self.theme_name()]
        self.last_seq = clipboard_token()
        self.last_hash = None
        self.clip_time = time.time()
        self.history = []  # lista de escaneos; cada uno es una lista de dicts {format, text, thumb, time}
        self.popup = None
        self.popup_job = None
        self.history_win = None
        self.settings_win = None
        self._photos = []  # referencias a PhotoImage para que Tk no las libere
        self.tray_has_menu = True
        self.tray = self._start_tray()
        self.root.after(POLL_MS, self._poll)
        self.hotkeys = HotkeyManager()
        self.root.after(300, self._warm_up)
        self.root.after(400, self.apply_hotkeys)
        self.root.after(500, self.first_run)
        self.root.after(700, self._scan_at_start)
        self.root.after(15000, self._periodic_update_check)

    def _periodic_update_check(self):
        self.check_updates()
        self.root.after(6 * 3600 * 1000, self._periodic_update_check)  # por si queda abierta días

    def hotkey_actions(self):
        """Atajo configurado -> qué hace. Las funciones se llaman desde el hilo de los atajos: pasan a Tk."""
        on_tk = lambda fn: (lambda: self.root.after(0, fn))
        actions = {}
        if self.settings["hotkey_focus"]:
            actions[self.settings["hotkey_focus"]] = on_tk(self.focus_popup)
        if self.settings["hotkey_region"]:
            actions[self.settings["hotkey_region"]] = on_tk(self.scan_region)
        if self.settings["hotkey_create"]:
            actions[self.settings["hotkey_create"]] = on_tk(self.show_create_qr)
        return actions

    def apply_hotkeys(self, retries=4):
        failed = self.hotkeys.set(self.hotkey_actions())
        problem = hotkeys_problem(getattr(self.hotkeys, "reason", None))
        if problem and self.hotkey_actions():
            # una vez por motivo: la Configuración lo sigue mostrando en la sección de atajos
            if load_state().get("hotkeys_warned") != self.hotkeys.reason:
                save_state(hotkeys_warned=self.hotkeys.reason)
                self.toast(problem, seconds=10)
            return
        if failed and retries:
            # al reiniciar o actualizar, la instancia anterior puede tardar un momento en soltar el atajo
            self.root.after(1500, lambda: self.apply_hotkeys(retries - 1))
            return
        if failed:
            self.toast(_("El atajo {atajo} ya lo usa otra aplicación.\n"
                         "Puedes elegir otro en Configuración › Atajos.",
                         atajo=", ".join(hotkey_label(h) for h in failed)), seconds=8)

    def _scan_at_start(self):
        """Si se abre a mano y el portapapeles cambió mientras ClipQR no estaba abierto (por ejemplo, se
        copió un QR y luego se abrió la app), se escanea. Al iniciarse con Windows no: lo que haya en el
        portapapeles es de la sesión anterior."""
        changed = load_state().get("clip_seq") != self.last_seq
        save_state(clip_seq=self.last_seq)
        if changed and not self.autostart_launch and not self.paused:
            self.scan()

    def _icon_image(self, paused=False):
        return make_icon(paused, dark_bg=tray_is_dark())

    def _start_tray(self):
        """Icono en la bandeja (Windows, Linux) o en la barra de menús (macOS). Si no se puede crear, ClipQR
        sigue funcionando y abre el historial como ventana principal."""
        try:
            import pystray  # en Linux sin servidor gráfico falla ya al importarlo
            tray = self._build_tray(pystray)
            start_tray(tray, on_error=lambda e: self.root.after(0, lambda: self._tray_failed(e)))
        except Exception as e:
            log_exception(type(e), e, e.__traceback__)
            self.root.after(600, lambda: self._tray_failed(None))
            return NullTray()
        self.tray_has_menu = getattr(tray, "HAS_MENU", True)
        return tray

    def _tray_failed(self, error=None):
        if getattr(self, "_tray_fallback", False):
            return
        self._tray_fallback = True
        if error is not None:
            log_exception(type(error), error, error.__traceback__)
        try:
            self.tray.stop()
        except Exception:
            pass
        self.tray = NullTray()
        self.tray_has_menu = False
        self.show_history()
        self.toast(_("No se pudo mostrar el icono de ClipQR en la bandeja del sistema.\n"
                     "ClipQR sigue activo: usa la ventana del historial."), seconds=10)

    def _build_tray(self, pystray):
        def ui(fn):
            return lambda icon, item: self.root.after(0, fn)

        def last_label(item):
            if not self.history:
                return _("Último: (nada todavía)")
            text = self.history[0][0]["text"].replace("\n", " ")
            return _("Último: {texto}", texto=(text[:40] + "…") if len(text) > 40 else text)

        menu = pystray.Menu(
            pystray.MenuItem(last_label, ui(lambda: self.history and self.show_popup(self.history[0])),
                             enabled=lambda item: bool(self.history)),
            pystray.MenuItem(_("Abrir historial"), ui(self.show_history), default=True),
            pystray.MenuItem(_("Escanear portapapeles ahora"), ui(lambda: self.scan(force=True))),
            pystray.MenuItem(lambda item: _("Escanear zona de la pantalla") + (
                f"  ({hotkey_label(self.settings['hotkey_region'])})" if self.settings["hotkey_region"] else ""),
                ui(self.scan_region)),
            pystray.MenuItem(lambda item: _("Crear QR…") + (
                f"  ({hotkey_label(self.settings['hotkey_create'])})" if self.settings["hotkey_create"] else ""),
                ui(self.show_create_qr)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: _("Actualizar a ClipQR {version}…", version=self.update_info["version"])
                             if self.update_info
                             else "", ui(self.show_update_notice), visible=lambda item: bool(self.update_info)),
            pystray.MenuItem(_("Configuración…"), ui(self.show_settings)),
            pystray.MenuItem(_("Invitar un cafecito ☕"), lambda: open_path(DONATE_URL)),
            pystray.MenuItem(_("Pausar"), ui(self.toggle_pause), checked=lambda item: self.paused),
            pystray.MenuItem(autostart_label(), ui(self.toggle_autostart), checked=lambda item: self.autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(_("Salir"), ui(self.quit)),
        )
        return pystray.Icon(APP_NAME, self._icon_image(), self._tray_title(), menu, **tray_options())

    def _tray_title(self):
        return _("{app} - en pausa", app=APP_NAME) if self.paused else _("{app} - vigilando portapapeles",
                                                                             app=APP_NAME)

    def save_settings(self):
        import json
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except OSError:
            pass

    def set_setting(self, **kw):
        self.settings.update(kw)
        self.save_settings()
        self.tray.update_menu()

    def theme_name(self):
        t = self.settings["theme"]
        return t if t in THEMES else system_theme()

    def toggle_pause(self):
        self.paused = not self.paused
        self.tray.icon = self._icon_image(self.paused)
        self.tray.title = self._tray_title()
        self.tray.update_menu()

    def _autostart_argv(self):
        """Orden con la que se abre ClipQR al iniciar sesión (con --autostart)."""
        if FROZEN:
            return [sys.executable, "--autostart"]
        launcher = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        return [gui_python(), launcher, "--autostart"]

    def autostart_enabled(self):
        if PACKAGED:
            return msix_startup_state() in ("enabled", "enabled_by_policy")
        return autostart_current() is not None

    def _set_autostart(self):
        autostart_set(self._autostart_argv())

    def first_run(self):
        """Primer arranque: activar inicio con Windows y avisar de que está en la bandeja.
        Si el programa se movió de carpeta, corrige la ruta de autoarranque."""
        if not os.path.exists(FIRST_RUN_MARK):
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(FIRST_RUN_MARK, "w") as f:
                f.write("1")
            if PACKAGED:  # en la Store el inicio con Windows lo activa el usuario
                self.toast(_("ClipQR está activo en la bandeja (junto al reloj).\n"
                             "Haz una captura de un QR y aparecerá aquí.\n"
                             "Puedes hacer que se inicie con Windows en Configuración (⚙)."), seconds=10)
                return
            if installed_by_setup():  # el asistente ya preguntó por el inicio con Windows
                self.toast(_("ClipQR está activo en la bandeja (junto al reloj).\n"
                             "Haz una captura de un QR y aparecerá aquí."), seconds=8)
                return
            self._set_autostart()
            self.tray.update_menu()
            self.toast(first_run_text(), seconds=8)
        else:
            if not PACKAGED and self.autostart_enabled() and \
                    autostart_current() != autostart_entry(self._autostart_argv()):
                self._set_autostart()
            self.startup_notice()
        if clipboard_tools_missing():
            self.toast(_("Para leer el portapapeles, instala xclip (X11) o wl-clipboard (Wayland)."), seconds=10)

    def startup_notice(self):
        """Aviso breve de que ClipQR arrancó (en la bandeja no siempre se ve: Windows oculta los iconos nuevos).
        Si al abrirlo ya había un QR en el portapapeles, el aviso del QR lo reemplaza."""
        if not self.settings["startup_notice"] or self.paused:
            return
        region = self.settings["hotkey_region"]
        hint = (_("Captura un QR o pulsa {atajo} para escanear una zona.", atajo=hotkey_label(region)) if region
                else _("Captura o copia un QR y aparecerá aquí."))
        self.toast(_("ClipQR está activo") + "\n" + hint, seconds=3)

    def toggle_autostart(self):
        if PACKAGED:
            ok, msg = msix_set_startup(not self.autostart_enabled())
            if not ok:
                self.toast(msg, seconds=8)
            self.tray.update_menu()
            return
        if self.autostart_enabled():
            autostart_remove()
        else:
            self._set_autostart()
        self.tray.update_menu()

    def quit(self):
        self.hotkeys.stop()
        try:
            self.tray.stop()
        except Exception:
            pass
        self.root.destroy()

    def restart(self):
        """Abre otra instancia de ClipQR y cierra esta (p. ej. para cambiar de idioma). Antes se suelta el
        mutex de instancia única para que la nueva no se crea repetida; los atajos los reintenta ella sola."""
        import subprocess
        if FROZEN:
            args = [sys.executable]
        else:
            launcher = os.path.abspath(sys.argv[0]) if sys.argv[0].lower().endswith(".py") else \
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
            args = [sys.executable, launcher]
        # PyInstaller --onefile: que la nueva instancia se descomprima aparte y no use la carpeta de esta
        env = {**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"}
        release_single_instance()
        try:
            subprocess.Popen(args, cwd=os.getcwd(), env=env, close_fds=True)
        except OSError as e:
            single_instance()
            self.toast(_("No se pudo reiniciar ClipQR.\n{error}", error=e.strerror or e), seconds=6)
            return
        self.quit()

    def _off_tk(self, work, done):
        """Ejecuta work() en otro hilo y luego done(resultado) en el hilo de Tk, para que la ventana nunca se
        congele. Leer el portapapeles puede tardar segundos: en Windows, si la app que copió genera la imagen al
        pedírsela (Recortes, navegadores, Office) o el archivo copiado está en OneDrive sin descargar; en Linux,
        si lo último copiado es nuestro, se le piden los datos a esta misma app. En macOS, directamente."""
        if SYSTEM == "macos":
            done(work())
            return

        def thread():
            result = work()
            try:
                self.root.after(0, lambda: done(result))
            except RuntimeError:  # la app ya se cerró
                pass

        threading.Thread(target=thread, daemon=True).start()

    def _poll(self):
        if SYSTEM == "linux":  # en Linux leer el portapapeles puede esperar a esta misma app
            self._off_tk(clipboard_token, self._on_clipboard_token)
        else:  # contador de cambios del sistema: instantáneo
            self._on_clipboard_token(clipboard_token())

    def _on_clipboard_token(self, seq):
        delay = POLL_MS
        try:
            if seq is None:
                # sin contador de cambios (macOS sin pyobjc, Linux sin xclip): se compara la imagen
                delay = max(POLL_MS, FALLBACK_POLL_MS)
                if not self.paused:
                    self.scan(polling=True)
            elif seq != self.last_seq:
                self.last_seq = seq
                self.clip_time = time.time()
                save_state(clip_seq=seq)
                if not self.paused:
                    self.scan()
                    # reintento: algunas herramientas de captura escriben la imagen con retraso
                    self.root.after(800, lambda s=seq: s == self.last_seq and self.scan())
        finally:
            self.root.after(delay, self._poll)

    def scan(self, force=False, polling=False):
        include_files = self.settings["explorer_files"]

        def read():  # fuera del hilo de la ventana: leer y comparar una captura 4K lleva su tiempo
            imgs = grab_clipboard_images(include_files)
            return imgs, image_hash(imgs) if imgs else None

        self._off_tk(read, lambda result: self._scan_images(*result, force=force, polling=polling))

    def _scan_images(self, imgs, h, force=False, polling=False):
        if not imgs:
            if force:
                self.toast(_("No hay ninguna imagen en el portapapeles."))
            return
        if h == self.last_hash and not force:
            return
        if polling:
            self.clip_time = time.time()
        self.last_hash = h
        # una captura de pantalla (no un archivo copiado) puede tener su archivo en la carpeta de capturas
        is_capture = len(imgs) == 1 and not getattr(imgs[0], "filename", None)
        self.decode_and_show(imgs, force, capture_since=self.clip_time if is_capture else None)

    def decode_and_show(self, imgs, force=False, capture_since=None):
        """Lee los códigos de las imágenes en segundo plano y muestra el aviso. Con capture_since, busca
        después el archivo que Windows guardó de esa captura (para ofrecer borrarlo)."""
        def work():
            # el archivo de la captura se busca a la vez que se leen los códigos: así el botón de borrarla
            # aparece casi junto con el aviso
            found = {}
            finder = None
            if capture_since is not None:
                finder = threading.Thread(target=lambda: found.update(path=find_saved_capture(imgs[0], capture_since)),
                                          daemon=True)
                finder.start()
            codes, texts = [], set()
            for img in imgs:
                for c in decode_image(img, self.settings["qr_only"]):
                    if c["text"] not in texts:
                        texts.add(c["text"])
                        codes.append({"format": c["format"], "text": c["text"],
                                      "thumb": make_thumb(img, c["box"]), "time": time.time(),
                                      "capture_pending": finder is not None})
            self.root.after(0, lambda: self._on_result(codes, force))
            if codes and finder is not None:
                finder.join()
                self.root.after(0, lambda: self._on_capture(codes, found.get("path")))

        threading.Thread(target=work, daemon=True).start()

    def _on_capture(self, codes, path):
        for c in codes:
            c["capture_pending"] = False
            c["capture"] = path
        if not path:
            self._paint_capture_slot(codes)  # no se guardó archivo: quitar «Buscando…»
            return
        if self.settings["delete_capture"]:
            self.trash_in_background(path, codes)
        else:
            self._paint_capture_slot(codes)

    def trash_in_background(self, path, codes, on_done=None):
        """Envía la captura a la Papelera en otro hilo: en una carpeta de OneDrive puede tardar segundos, y en el
        hilo de la ventana dejaba el aviso congelado a medio aparecer. Al terminar, se actualiza el aviso."""
        def work():
            ok = send_to_trash(path)

            def done():
                for c in codes:
                    c["capture_deleted"] = ok
                self._paint_capture_slot(codes)
                if on_done is not None:
                    on_done(ok)
            self.root.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _on_result(self, codes, force):
        if not codes:
            if force:
                self.toast(_("No se encontró ningún QR en la imagen."))
            return
        # los datos personales (documentos de identidad, tarjetas de embarque) no se guardan en el historial
        keep = [c for c in codes if not analyze(c["text"]).private]
        if keep:
            self.history.insert(0, keep)
            del self.history[self.settings["history_max"]:]
        if self.settings["sound"]:
            beep(self.root)
        self.tray.update_menu()
        self.show_popup(codes)
        if self.history_win is not None and self.history_win.winfo_exists():
            self._fill_history()

    def copy(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._off_tk(clipboard_token, lambda seq: setattr(self, "last_seq", seq))  # no re-escanear lo que copiamos
        if btn is not None:
            self._flash(btn, _("✓ Copiado"))

    def run_action(self, kind, arg, btn):
        """Solo se llama al pulsar un botón."""
        try:
            if kind == "copy":
                self.copy(arg, btn)
            elif kind == "open":
                open_path(arg)
                self._close_popup()
            elif kind == "file":
                open_with_default_app(*arg)
                self._close_popup()
            elif kind == "wifi":
                btn.config(text=_("Conectando…"), state="disabled")

                def work():
                    ok, msg = connect_wifi(arg["ssid"], arg["password"], arg["auth"], arg["hidden"])
                    self.root.after(0, lambda: self.toast(("✓ " if ok else "✕ ") + msg, seconds=6))

                threading.Thread(target=work, daemon=True).start()
        except OSError as e:
            self.toast(_("No hay ninguna aplicación para abrir esto.\n{error}", error=e.strerror or e), seconds=6)

    def run(self):
        self.root.mainloop()


def uninstall(silent=False):
    """Desinstalación (instalado con ClipQR-Setup.exe): cierra ClipQR, quita accesos directos,
    inicio con Windows, la entrada de «Aplicaciones instaladas», los ajustes y el propio programa.
    Con silent no pregunta ni muestra nada (QuietUninstallString, winget). En macOS y Linux quita el inicio
    al iniciar sesión y los ajustes."""
    import shutil
    from tkinter import messagebox

    root = None
    if not silent:
        root = tk.Tk()
        root.withdraw()
        if not messagebox.askyesno(_("Desinstalar ClipQR"), _("¿Quieres desinstalar ClipQR de este equipo?")):
            return
    uninstall_registration()
    shutil.rmtree(CONFIG_DIR, ignore_errors=True)
    if root is not None:
        messagebox.showinfo("ClipQR", _("ClipQR se ha desinstalado."))
        root.destroy()
    uninstall_program()

def image_hash(imgs):
    """Huella de las imágenes del portapapeles, para no volver a escanear la misma."""
    return hashlib.md5(b"".join(i.convert("RGB").tobytes()[:2_000_000] for i in imgs)).hexdigest()


def parse_cli(argv):
    """Qué hacer según la línea de órdenes:
    ("uninstall", silent)  ClipQR.exe --uninstall [/silent]   (desde «Aplicaciones instaladas»)
    ("decode", rutas)      ClipQR.exe imagen.png …            (muestra lo que hay en cada imagen)
    ("run", autostart)     ClipQR.exe [--autostart]           (--autostart: abierto por el inicio de Windows)"""
    if argv[:1] == ["--uninstall"]:
        return "uninstall", any(a.lower() in ("/silent", "--silent") for a in argv[1:])
    files = [a for a in argv if not a.startswith("--")]
    if files:
        return "decode", files
    return "run", "--autostart" in argv


def main():
    enable_dpi_awareness()
    mode, arg = parse_cli(sys.argv[1:])
    if mode == "uninstall":
        set_language(load_settings()["language"])
        uninstall(silent=arg)
        return
    if mode == "decode":
        sys.stdout.reconfigure(encoding="utf-8")
        for path in arg:
            for c in decode_image(Image.open(path)):
                print(c["format"], "|", c["text"], "|", parse_payload(c["text"]))
        return
    if not single_instance():
        return
    ClipQR(autostart=arg).run()
