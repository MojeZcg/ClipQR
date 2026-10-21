"""Ajustes del usuario, estado interno y registro de errores (en %APPDATA%\\ClipQR)."""
import json
import os
import time

from clipqr import APP_NAME
from clipqr.i18n import N_, _

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
FIRST_RUN_MARK = os.path.join(CONFIG_DIR, "first_run_done")
ERROR_LOG = os.path.join(CONFIG_DIR, "error.log")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
STATE_FILE = os.path.join(CONFIG_DIR, "state.json")  # datos internos, no ajustes del usuario

DEFAULT_SETTINGS = {
    "position": "top-right", "x": None, "y": None,
    "autoclose": True, "seconds": 25, "pause_on_hover": True,
    "theme": "auto", "animation": True, "sound": False,
    "qr_only": False, "explorer_files": True, "history_max": 50, "delete_capture": False,
    # "" = desactivado. Nada de Ctrl+Alt+letra: en teclados español/latinoamericano Ctrl+Alt es AltGr
    # (Ctrl+Alt+Q escribe @) y el atajo impediría escribir esos caracteres.
    "hotkey_focus": "Ctrl+Shift+Space",
    "hotkey_region": "Win+Shift+Q",  # junto a Win+Shift+S, el de las capturas de Windows
    "hotkey_create": "Win+Shift+G",  # G de «generar»
    "check_updates": True,  # una vez al día consulta las releases de GitHub
    "show_passwords": False,  # contraseñas Wi-Fi y secretos 2FA visibles sin pulsar el ojo
    "startup_notice": True,  # aviso breve «ClipQR está activo» al iniciarse
    "language": "auto",  # «auto» = el de Windows (español si Windows está en español; si no, inglés)
}


def error_report(version, limit=60):
    """Texto para pegar en una incidencia de GitHub: versión, Windows y los últimos errores registrados.
    No contiene imágenes ni el contenido de los códigos (los errores no los guardan)."""
    import platform
    try:
        with open(ERROR_LOG, encoding="utf-8") as f:
            lines = f.read().splitlines()[-limit:]
    except OSError:
        lines = []
    body = "\n".join(lines) if lines else _("(no hay errores registrados)")
    return f"ClipQR {version} · {platform.platform()} · Python {platform.python_version()}\n\n```\n{body}\n```\n"

HOTKEY_FOCUS_CHOICES = ("Ctrl+Shift+Space", "Win+Alt+Space", "")
HOTKEY_REGION_CHOICES = ("Win+Shift+Q", "Win+Alt+Q", "Alt+Shift+Q", "")
HOTKEY_CREATE_CHOICES = ("Win+Shift+G", "Alt+Shift+G", "")


def hotkey_label(hotkey):
    """«Ctrl+Alt+Space» -> «Ctrl+Alt+Espacio» para mostrarlo (en el idioma de la interfaz)."""
    return hotkey.replace("Space", _("Espacio")) if hotkey else _("Desactivado")


POSITIONS = (("top-right", N_("Arriba a la derecha")), ("bottom-right", N_("Abajo a la derecha")),
             ("center", N_("En el centro")), ("custom", N_("Donde lo dejé al arrastrarlo")))


def load_settings():
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    except (OSError, ValueError):
        return dict(DEFAULT_SETTINGS)


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(**values):
    state = {**load_state(), **values}
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except OSError:
        pass


def log_exception(*exc_info):
    """Sin consola (pythonw / exe) los errores se perderían: se guardan en %APPDATA%\\ClipQR\\error.log."""
    import traceback
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "".join(traceback.format_exception(*exc_info)) + "\n")
    except OSError:
        pass
