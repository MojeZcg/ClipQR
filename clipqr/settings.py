"""Ajustes del usuario, estado interno y registro de errores (en %APPDATA%\\ClipQR en Windows,
~/Library/Application Support/ClipQR en macOS y ~/.config/ClipQR en Linux)."""
import json
import os
import time

from clipqr.i18n import N_, _
from clipqr.platform import SYSTEM, config_dir

CONFIG_DIR = config_dir()
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

# macOS: «Win» es ⌘. Los atajos no se interceptan (la app de delante también recibe las teclas), así que se
# evita todo lo que use el sistema o las apps: ⌘⇧Q cierra la sesión, ⌘⇧3/4/5 son capturas, ⌃⌘Q bloquea la
# pantalla, ⌃⌘Espacio abre los emojis y ⌥⌘Q es «Salir» en muchas apps. Con ⌃⌥⌘ no choca nada conocido.
MAC_HOTKEYS = {"hotkey_focus": "Ctrl+Alt+Win+Space", "hotkey_region": "Ctrl+Alt+Win+Q",
               "hotkey_create": "Ctrl+Alt+Win+G"}


def default_settings(system=SYSTEM):
    """Ajustes por defecto en cada sistema (solo cambian los atajos de macOS)."""
    return {**DEFAULT_SETTINGS, **(MAC_HOTKEYS if system == "macos" else {})}


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

HOTKEY_CHOICES = {
    "windows": {"focus": ("Ctrl+Shift+Space", "Win+Alt+Space", ""),
                "region": ("Win+Shift+Q", "Win+Alt+Q", "Alt+Shift+Q", ""),
                "create": ("Win+Shift+G", "Alt+Shift+G", "")},
    "macos": {"focus": ("Ctrl+Alt+Win+Space", "Ctrl+Alt+Space", ""),
              "region": ("Ctrl+Alt+Win+Q", "Ctrl+Alt+Q", ""),
              "create": ("Ctrl+Alt+Win+G", "Ctrl+Alt+G", "")},
}
HOTKEY_CHOICES["linux"] = HOTKEY_CHOICES["windows"]  # «Win» es la tecla Súper
HOTKEY_FOCUS_CHOICES = HOTKEY_CHOICES[SYSTEM]["focus"]
HOTKEY_REGION_CHOICES = HOTKEY_CHOICES[SYSTEM]["region"]
HOTKEY_CREATE_CHOICES = HOTKEY_CHOICES[SYSTEM]["create"]

MAC_SYMBOLS = {"ctrl": "⌃", "alt": "⌥", "shift": "⇧", "win": "⌘"}


def hotkey_label(hotkey, system=SYSTEM):
    """«Ctrl+Alt+Space» -> «Ctrl+Alt+Espacio» para mostrarlo (en el idioma de la interfaz). En macOS con los
    símbolos de las teclas en el orden del sistema («⌃⌥⌘Espacio»); en Linux «Win» se llama «Super»."""
    if not hotkey:
        return _("Desactivado")
    if system == "macos":
        *mods, key = hotkey.split("+")
        mods = {m.lower() for m in mods}
        return "".join(MAC_SYMBOLS[m] for m in ("ctrl", "alt", "shift", "win") if m in mods) +             key.replace("Space", _("Espacio"))
    if system == "linux":
        hotkey = hotkey.replace("Win+", "Super+")
    return hotkey.replace("Space", _("Espacio"))


POSITIONS = (("top-right", N_("Arriba a la derecha")), ("bottom-right", N_("Abajo a la derecha")),
             ("center", N_("En el centro")), ("custom", N_("Donde lo dejé al arrastrarlo")))


def load_settings():
    defaults = default_settings()
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return {**defaults, **json.load(f)}
    except (OSError, ValueError):
        return defaults


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
    """Sin consola (pythonw / exe / .app) los errores se perderían: se guardan en CONFIG_DIR/error.log."""
    import traceback
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "".join(traceback.format_exception(*exc_info)) + "\n")
    except OSError:
        pass
