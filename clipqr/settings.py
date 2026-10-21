"""Ajustes del usuario y registro de errores (en %APPDATA%\\ClipQR)."""
import os
import time

from clipqr import APP_NAME

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)

FIRST_RUN_MARK = os.path.join(CONFIG_DIR, "first_run_done")

ERROR_LOG = os.path.join(CONFIG_DIR, "error.log")

SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "position": "top-right", "x": None, "y": None,
    "autoclose": True, "seconds": 25, "pause_on_hover": True,
    "theme": "auto", "animation": True, "sound": False,
    "qr_only": False, "explorer_files": True, "history_max": 50, "delete_capture": False,
}

POSITIONS = (("top-right", "Arriba a la derecha"), ("bottom-right", "Abajo a la derecha"),
             ("center", "En el centro"), ("custom", "Donde lo dejé al arrastrarlo"))

def load_settings():
    import json
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    except (OSError, ValueError):
        return dict(DEFAULT_SETTINGS)

def log_exception(*exc_info):
    """Sin consola (pythonw / exe) los errores se perderían: se guardan en %APPDATA%\\ClipQR\\error.log."""
    import traceback
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "".join(traceback.format_exception(*exc_info)) + "\n")
    except OSError:
        pass
