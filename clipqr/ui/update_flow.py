"""Flujo de actualización: comprobar, avisar e instalar (en segundo plano, sin bloquear la interfaz)."""
import os
import subprocess
import threading
import time

from clipqr import VERSION
from clipqr.i18n import _
from clipqr.settings import load_state, save_state
from clipqr.updates import CHECK_EVERY, download_verified, fetch_latest, is_newer, setup_args
from clipqr.winplatform import FROZEN, PACKAGED, installed_by_setup, shortcut_paths


class UpdateMixin:
    update_info = None

    def can_self_update(self):
        """Solo la instalación hecha con el asistente se actualiza sola; la portátil y la de la Store no."""
        return FROZEN and not PACKAGED and installed_by_setup()

    def check_updates(self, manual=False):
        """Automático: como mucho una vez al día y si está activado. Manual: siempre, y dice el resultado."""
        if PACKAGED:
            if manual:
                self.toast(_("Las actualizaciones de la versión de la Microsoft Store las gestiona la Store."), 6)
            return
        last = load_state().get("last_update_check", 0)
        if not manual and (not self.settings["check_updates"] or time.time() - last < CHECK_EVERY):
            return

        def work():
            try:
                info = fetch_latest()
            except Exception as e:
                if manual:
                    msg = _("No se pudo consultar GitHub.\n{error}", error=e)
                    self.root.after(0, lambda: self.toast(msg, 6))
                return
            save_state(last_update_check=time.time())
            if is_newer(info["version"]):
                self.root.after(0, lambda: self._update_available(info, manual))
            elif manual:
                self.root.after(0, lambda: self.toast(_("Tienes la última versión ({version}).", version=VERSION), 4))

        threading.Thread(target=work, daemon=True).start()

    def _update_available(self, info, manual=False):
        self.update_info = info
        self.tray.update_menu()
        if not manual and load_state().get("skipped_version") == info["version"]:
            return  # el usuario dijo «Ahora no» a esta versión: solo queda en el menú de la bandeja
        self.show_update_notice()

    def show_update_notice(self):
        info = self.update_info
        if not info:
            return
        page = lambda b: (os.startfile(info["page"]), self._close_popup())
        skip = lambda b: (save_state(skipped_version=info["version"]), self._close_popup())
        if self.can_self_update():
            buttons = [(_("Instalar"), self.install_update, True), (_("Ver novedades ↗"), page, False),
                       (_("Ahora no"), skip, False)]
            text = _("Tienes la {version}. Se descarga, se comprueba y se instala sola; tus ajustes se conservan.",
                     version=VERSION)
        else:
            buttons = [(_("Descargar ↗"), page, True), (_("Ahora no"), skip, False)]
            text = _("Tienes la {version}. Descárgala desde GitHub.", version=VERSION)
        self.notice(_("ClipQR {version} disponible", version=info["version"]), text, buttons)

    def install_update(self, button=None):
        info = self.update_info
        if button is not None:
            button.config(text=_("Descargando…"), state="disabled")

        def work():
            try:
                path = download_verified(info)
            except Exception as e:
                msg = _("No se pudo actualizar.\n{error}", error=e)
                self.root.after(0, lambda: self.toast(msg, 8))
                return
            desktop = os.path.exists(shortcut_paths()[1])
            subprocess.Popen([path, *setup_args(self.autostart_enabled(), desktop)], creationflags=0x00000008)
            self.root.after(0, self.quit)  # el instalador cierra lo que quede y vuelve a abrir ClipQR

        threading.Thread(target=work, daemon=True).start()
