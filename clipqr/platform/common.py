"""Piezas comunes a todas las plataformas: rectángulos de pantalla, carpeta de ajustes, ejecución de
órdenes del sistema y lo que en macOS y Linux se resuelve igual (Tk, bloqueo de instancia única…).

Nada de esto usa APIs de Windows: se puede importar (y probar) en cualquier sistema."""
import os
import re
import subprocess
import sys
import time
from collections import namedtuple

from clipqr import APP_NAME

Area = namedtuple("Area", "left top right bottom")

FROZEN = getattr(sys, "frozen", False)  # empaquetado con PyInstaller


def area_containing(x, y, areas):
    """El área que contiene el punto, o None (por ejemplo, si se desconectó ese monitor)."""
    return next((a for a in areas if a.left <= x < a.right and a.top <= y < a.bottom), None)


def clamp_to_area(x, y, w, h, area):
    """Mueve (x, y) lo justo para que una ventana w×h quede dentro del área."""
    return min(max(x, area.left), area.right - w), min(max(y, area.top), area.bottom - h)


def config_dir(platform=None, env=None, home=None):
    """Carpeta de ajustes: %APPDATA%\\ClipQR en Windows, ~/Library/Application Support/ClipQR en macOS y
    $XDG_CONFIG_HOME/ClipQR (~/.config/ClipQR) en Linux."""
    platform = platform or sys.platform
    env = os.environ if env is None else env
    home = home or os.path.expanduser("~")
    if platform == "win32":
        return os.path.join(env.get("APPDATA", home), APP_NAME)
    if platform == "darwin":
        return os.path.join(home, "Library", "Application Support", APP_NAME)
    return os.path.join(env.get("XDG_CONFIG_HOME") or os.path.join(home, ".config"), APP_NAME)


def run(args, timeout=10, input=None):
    """Ejecuta una orden del sistema y devuelve (código, salida como texto). Si la orden no existe o tarda
    demasiado, devuelve (None, mensaje) en vez de lanzar una excepción."""
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout, input=input)
    except (OSError, subprocess.SubprocessError) as e:
        return None, str(e)
    out = (r.stdout or r.stderr or b"").decode("utf-8", "replace").strip()
    return r.returncode, out


def gui_python():
    """Python con el que relanzar ClipQR desde el código fuente."""
    return sys.executable


# --- Tk: en macOS y Linux los monitores y el ratón se consultan a la ventana raíz -----------------------

_tk_root = None


def bind_tk(root):
    """Guarda la ventana raíz de Tk para las funciones que la necesitan (monitores, cursor)."""
    global _tk_root
    _tk_root = root


def tk_root():
    if _tk_root is not None:
        return _tk_root
    import tkinter
    return tkinter._default_root


def tk_cursor_pos():
    root = tk_root()
    return root.winfo_pointerxy() if root is not None else (0, 0)


def tk_screen():
    """Pantalla entera según Tk (en X11 abarca todos los monitores)."""
    root = tk_root()
    if root is None:
        return Area(0, 0, 1920, 1080)
    return Area(0, 0, root.winfo_screenwidth(), root.winfo_screenheight())


def tk_bring_to_front(win):
    """Sube la ventana por encima de las demás. El foco de teclado lo pide quien llama (focus_force)."""
    try:
        win.lift()
        win.attributes("-topmost", True)
    except Exception:
        pass


# --- instancia única con un archivo bloqueado (macOS y Linux) ----------------------------------------------

_lock_file = None


def posix_single_instance(folder=None):
    """True si no hay otra instancia de ClipQR abierta. El bloqueo (flock) lo suelta el sistema al salir,
    aunque el proceso termine de golpe."""
    global _lock_file
    import fcntl
    folder = folder or config_dir()
    os.makedirs(folder, exist_ok=True)
    f = open(os.path.join(folder, "instance.lock"), "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False
    _lock_file = f
    return True


def posix_release_single_instance():
    """Suelta el bloqueo (al reiniciar, para que la nueva instancia pueda arrancar)."""
    global _lock_file
    if _lock_file is not None:
        try:
            _lock_file.close()
        except OSError:
            pass
        _lock_file = None


def write_file(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def remove_file(path):
    try:
        os.remove(path)
    except OSError:
        pass


def cached(seconds):
    """Recuerda el resultado de una función sin argumentos durante `seconds` (para no lanzar una orden del
    sistema cada vez que se abre un aviso)."""
    def wrap(fn):
        memo = {}

        def inner():
            now = time.monotonic()
            if "t" not in memo or now - memo["t"] > seconds:
                memo["v"], memo["t"] = fn(), now
            return memo["v"]
        inner.__doc__ = fn.__doc__
        return inner
    return wrap


def first_family(candidates, families, default):
    """La primera fuente de `candidates` instalada, o `default`."""
    return next((f for f in candidates if f in families), default)


def parse_wifi_profile(text):
    """Salida de «netsh wlan show profile name=… key=clear» (en español o en inglés) ->
    (contraseña, seguridad para el QR: WPA / WEP / nopass)."""
    password, auth = "", ""
    for line in text.splitlines():
        m = re.match(r"^\s*([^:]+?)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1).lower(), m.group(2).strip()
        if key in ("contenido de la clave", "key content"):
            password = value
        elif key in ("autenticación", "authentication") and not auth:
            auth = value
    if not password:
        return "", "nopass"
    return password, "WEP" if "wep" in auth.lower() else "WPA"
