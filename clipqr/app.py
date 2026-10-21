"""Aplicación: bandeja del sistema, vigilancia del portapapeles y acciones."""
import ctypes
import hashlib
import os
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont

import pystray
from PIL import Image

from clipqr import APP_NAME
from clipqr.actions import connect_wifi, find_saved_capture, open_with_default_app
from clipqr.decode import decode_image, grab_clipboard_images, make_thumb
from clipqr.icons import make_icon
from clipqr.payloads import parse_payload
from clipqr.settings import CONFIG_DIR, FIRST_RUN_MARK, SETTINGS_FILE, load_settings, log_exception
from clipqr.ui.history import HistoryMixin
from clipqr.ui.popup import PopupMixin
from clipqr.ui.settings_window import SettingsWindowMixin
from clipqr.ui.theme import THEMES
from clipqr.ui.widgets import WidgetsMixin
from clipqr.winplatform import (FROZEN, PACKAGED, RUN_KEY, UNINSTALL_KEY, installed_by_setup, msix_set_startup,
                                msix_startup_state, send_to_recycle_bin, shortcut_paths, single_instance,
                                taskbar_is_dark, user32, windows_theme)

POLL_MS = 150  # GetClipboardSequenceNumber es casi gratis: se puede mirar a menudo


class ClipQR(PopupMixin, HistoryMixin, SettingsWindowMixin, WidgetsMixin):
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title(APP_NAME)
        self.root.report_callback_exception = log_exception
        self.dpi = self.root.winfo_fpixels("1i") / 96
        families = set(tkfont.families(self.root))
        self.icon_font = next((f for f in ("Segoe Fluent Icons", "Segoe MDL2 Assets") if f in families), None)
        self.ui_font = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
        self.paused = False
        self.settings = load_settings()
        self.c = THEMES[self.theme_name()]
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.last_hash = None
        self.clip_time = time.time()
        self.history = []  # lista de escaneos; cada uno es una lista de dicts {format, text, thumb, time}
        self.popup = None
        self.popup_job = None
        self.history_win = None
        self.settings_win = None
        self._photos = []  # referencias a PhotoImage para que Tk no las libere
        self.tray = self._build_tray()
        self.tray.run_detached()
        self.root.after(POLL_MS, self._poll)
        self.root.after(300, self._warm_up)
        self.root.after(500, self.first_run)

    def _icon_image(self, paused=False):
        return make_icon(paused, dark_bg=taskbar_is_dark())

    def _build_tray(self):
        def ui(fn):
            return lambda icon, item: self.root.after(0, fn)

        def last_label(item):
            if not self.history:
                return "Último: (nada todavía)"
            text = self.history[0][0]["text"].replace("\n", " ")
            return "Último: " + ((text[:40] + "…") if len(text) > 40 else text)

        menu = pystray.Menu(
            pystray.MenuItem(last_label, ui(lambda: self.history and self.show_popup(self.history[0])),
                             enabled=lambda item: bool(self.history)),
            pystray.MenuItem("Abrir historial", ui(self.show_history), default=True),
            pystray.MenuItem("Escanear portapapeles ahora", ui(lambda: self.scan(force=True))),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Configuración…", ui(self.show_settings)),
            pystray.MenuItem("Pausar", ui(self.toggle_pause), checked=lambda item: self.paused),
            pystray.MenuItem("Iniciar con Windows", ui(self.toggle_autostart), checked=lambda item: self.autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", ui(self.quit)),
        )
        return pystray.Icon(APP_NAME, self._icon_image(), f"{APP_NAME} - vigilando portapapeles", menu)

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
        return t if t in THEMES else windows_theme()

    def toggle_pause(self):
        self.paused = not self.paused
        self.tray.icon = self._icon_image(self.paused)
        self.tray.title = f"{APP_NAME} - {'en pausa' if self.paused else 'vigilando portapapeles'}"
        self.tray.update_menu()

    def _autostart_cmd(self):
        if FROZEN:
            return f'"{sys.executable}"'
        exe = sys.executable
        pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
        if os.path.exists(pyw):
            exe = pyw
        launcher = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        return f'"{exe}" "{launcher}"'

    def _autostart_value(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
                return winreg.QueryValueEx(k, APP_NAME)[0]
        except OSError:
            return None

    def autostart_enabled(self):
        if PACKAGED:
            return msix_startup_state() in ("enabled", "enabled_by_policy")
        return self._autostart_value() is not None

    def _set_autostart(self):
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, self._autostart_cmd())

    def first_run(self):
        """Primer arranque: activar inicio con Windows y avisar de que está en la bandeja.
        Si el programa se movió de carpeta, corrige la ruta de autoarranque."""
        if not os.path.exists(FIRST_RUN_MARK):
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(FIRST_RUN_MARK, "w") as f:
                f.write("1")
            if PACKAGED:  # en la Store el inicio con Windows lo activa el usuario
                self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                           "Haz una captura de un QR y aparecerá aquí.\n"
                           "Puedes hacer que se inicie con Windows en Configuración (⚙).", seconds=10)
                return
            if installed_by_setup():  # el asistente ya preguntó por el inicio con Windows
                self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                           "Haz una captura de un QR y aparecerá aquí.", seconds=8)
                return
            self._set_autostart()
            self.tray.update_menu()
            self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                       "Haz una captura de un QR y aparecerá aquí.\n"
                       "Se iniciará solo con Windows.", seconds=8)
        elif not PACKAGED and self.autostart_enabled() and self._autostart_value() != self._autostart_cmd():
            self._set_autostart()

    def toggle_autostart(self):
        if PACKAGED:
            ok, msg = msix_set_startup(not self.autostart_enabled())
            if not ok:
                self.toast(msg, seconds=8)
            self.tray.update_menu()
            return
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if self.autostart_enabled():
                winreg.DeleteValue(k, APP_NAME)
            else:
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, self._autostart_cmd())
        self.tray.update_menu()

    def quit(self):
        self.tray.stop()
        self.root.destroy()

    def _poll(self):
        try:
            seq = user32.GetClipboardSequenceNumber()
            if seq != self.last_seq:
                self.last_seq = seq
                self.clip_time = time.time()
                if not self.paused:
                    self.scan()
                    # reintento: algunas herramientas de captura escriben la imagen con retraso
                    self.root.after(800, lambda s=seq: s == self.last_seq and self.scan())
        finally:
            self.root.after(POLL_MS, self._poll)

    def scan(self, force=False):
        imgs = grab_clipboard_images(self.settings["explorer_files"])
        if not imgs:
            if force:
                self.toast("No hay ninguna imagen en el portapapeles.")
            return
        h = hashlib.md5(b"".join(i.convert("RGB").tobytes()[:2_000_000] for i in imgs)).hexdigest()
        if h == self.last_hash and not force:
            return
        self.last_hash = h

        def work():
            codes, texts = [], set()
            for img in imgs:
                for c in decode_image(img, self.settings["qr_only"]):
                    if c["text"] not in texts:
                        texts.add(c["text"])
                        codes.append({"format": c["format"], "text": c["text"],
                                      "thumb": make_thumb(img, c["box"]), "time": time.time()})
            self.root.after(0, lambda: self._on_result(codes, force))
            # captura de pantalla (no un archivo copiado): buscar el archivo que guarda Windows
            if codes and len(imgs) == 1 and not getattr(imgs[0], "filename", None):
                path = find_saved_capture(imgs[0], since)
                if path:
                    self.root.after(0, lambda: self._on_capture(codes, path))

        since = self.clip_time
        threading.Thread(target=work, daemon=True).start()

    def _on_capture(self, codes, path):
        for c in codes:
            c["capture"] = path
        if self.settings["delete_capture"]:
            deleted = send_to_recycle_bin(path)
            for c in codes:
                c["capture_deleted"] = deleted
        self._paint_capture_slot(codes)

    def _on_result(self, codes, force):
        if not codes:
            if force:
                self.toast("No se encontró ningún QR en la imagen.")
            return
        self.history.insert(0, codes)
        del self.history[self.settings["history_max"]:]
        if self.settings["sound"]:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        self.tray.update_menu()
        self.show_popup(codes)
        if self.history_win is not None and self.history_win.winfo_exists():
            self._fill_history()

    def copy(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.last_seq = user32.GetClipboardSequenceNumber()  # no re-escanear lo que copiamos
        if btn is not None:
            self._flash(btn, "✓ Copiado")

    def run_action(self, kind, arg, btn):
        """Solo se llama al pulsar un botón."""
        try:
            if kind == "open":
                os.startfile(arg)
                self._close_popup()
            elif kind == "file":
                open_with_default_app(*arg)
                self._close_popup()
            elif kind == "wifi":
                btn.config(text="Conectando…", state="disabled")

                def work():
                    ok, msg = connect_wifi(arg["ssid"], arg["password"], arg["auth"], arg["hidden"])
                    self.root.after(0, lambda: self.toast(("✓ " if ok else "✕ ") + msg, seconds=6))

                threading.Thread(target=work, daemon=True).start()
        except OSError as e:
            self.toast(f"No hay ninguna aplicación para abrir esto.\n{e.strerror or e}", seconds=6)

    def run(self):
        self.root.mainloop()


def uninstall(silent=False):
    """Desinstalación (instalado con ClipQR-Setup.exe): cierra ClipQR, quita accesos directos,
    inicio con Windows, la entrada de «Aplicaciones instaladas», los ajustes y el propio programa.
    Con silent no pregunta ni muestra nada (QuietUninstallString, winget)."""
    import shutil
    import subprocess
    import winreg
    from tkinter import messagebox

    root = None
    if not silent:
        root = tk.Tk()
        root.withdraw()
        if not messagebox.askyesno("Desinstalar ClipQR", "¿Quieres desinstalar ClipQR de este equipo?"):
            return
    no_window = 0x08000000
    subprocess.run(["taskkill", "/F", "/IM", "ClipQR.exe", "/FI", f"PID ne {os.getpid()}",
                    "/FI", f"PID ne {os.getppid()}"], capture_output=True, creationflags=no_window)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, APP_NAME)
    except OSError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    except OSError:
        pass
    for lnk in shortcut_paths():
        try:
            os.remove(lnk)
        except OSError:
            pass
    shutil.rmtree(CONFIG_DIR, ignore_errors=True)
    if root is not None:
        messagebox.showinfo("ClipQR", "ClipQR se ha desinstalado.")
        root.destroy()
    if FROZEN:  # el programa no puede borrarse a sí mismo mientras se ejecuta: cmd lo reintenta al salir
        exe, folder = sys.executable, os.path.dirname(sys.executable)
        setup_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", APP_NAME)
        if os.path.normcase(folder) == os.path.normcase(setup_dir):  # carpeta del asistente: entera
            remove = f'rmdir /s /q "{folder}" 2>nul & if not exist "{folder}" exit'
        else:  # en cualquier otro sitio solo el propio .exe (y la carpeta si queda vacía)
            remove = f'del /f /q "{exe}" 2>nul & if not exist "{exe}" (rmdir "{folder}" 2>nul & exit)'
        subprocess.Popen(f'cmd /c for /l %i in (1,1,30) do (ping -n 2 127.0.0.1 >nul & {remove})',
                         creationflags=no_window)

def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if sys.argv[1:2] == ["--uninstall"]:  # lo lanza Windows desde «Aplicaciones instaladas»
        uninstall(silent=any(a.lower() in ("/silent", "--silent") for a in sys.argv[2:]))
        return
    if len(sys.argv) > 1:  # modo prueba: py main.py imagen.png
        sys.stdout.reconfigure(encoding="utf-8")
        for path in sys.argv[1:]:
            for c in decode_image(Image.open(path)):
                print(c["format"], "|", c["text"], "|", parse_payload(c["text"]))
        return
    if not single_instance():
        return
    ClipQR().run()
