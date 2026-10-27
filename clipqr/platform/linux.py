"""Linux (y otros Unix con X11 o Wayland): portapapeles con xclip / wl-clipboard, bandeja con pystray
(AppIndicator o X11), inicio al iniciar sesión con ~/.config/autostart, papelera de freedesktop, Wi‑Fi con
NetworkManager (nmcli) y atajos con pynput (solo X11).

Solo usa la biblioteca estándar y órdenes del sistema: se puede importar (y probar) en cualquier sistema."""
import hashlib
import os
import re
import shutil
import threading
import time
import urllib.parse

from clipqr import APP_NAME
from clipqr.hotkeys import PynputHotkeyManager
from clipqr.i18n import _
from clipqr.platform.common import (Area, cached, first_family, posix_release_single_instance, posix_single_instance,
                                    read_file, remove_file, run, tk_bring_to_front, tk_cursor_pos, tk_root,
                                    tk_screen, write_file)

# no hay un contador de cambios del portapapeles: se compara el contenido, así que se mira menos a menudo
CLIPBOARD_POLL_MS = 500
FONT_SCALE = 1
PACKAGED = False

AUTOSTART_FILE = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config"),
                              "autostart", "clipqr.desktop")


def is_wayland(env=None):
    env = os.environ if env is None else env
    return env.get("XDG_SESSION_TYPE", "").lower() == "wayland" or bool(env.get("WAYLAND_DISPLAY"))


# --- tema y aspecto -------------------------------------------------------------------------------------------

def parse_color_scheme(output):
    """Salida de «gsettings get org.gnome.desktop.interface color-scheme» («'prefer-dark'») -> tema."""
    return "dark" if "dark" in (output or "").lower() else "light"


@cached(5)
def system_theme():
    code, out = run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"], timeout=3)
    if code == 0 and "default" not in out:
        return parse_color_scheme(out)
    code, out = run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"], timeout=3)
    return parse_color_scheme(out) if code == 0 else "light"


def tray_is_dark():
    """La barra superior de GNOME es oscura siempre; en los demás escritorios sigue al tema."""
    if "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "").upper():
        return True
    return system_theme() == "dark"


def style_window(win, border=None, dark=None):
    """El aspecto de las ventanas lo pone el gestor de ventanas."""


def enable_dpi_awareness():
    pass


def prepare_app(root):
    pass


def screen_scale(root):
    return root.winfo_fpixels("1i") / 96


def pick_fonts(families):
    ui = first_family(("Noto Sans", "Cantarell", "Ubuntu", "DejaVu Sans", "Liberation Sans"), families,
                      "TkDefaultFont")
    mono = first_family(("Noto Sans Mono", "DejaVu Sans Mono", "Ubuntu Mono", "Liberation Mono"), families,
                        "TkFixedFont")
    return ui, None, mono


def ui_langid():
    return None


def ui_locale_name():
    return None


def beep(root=None):
    root = root or tk_root()
    if root is not None:
        root.bell()


# --- monitores ----------------------------------------------------------------------------------------------

def parse_workarea(output):
    """Salida de «xprop -root -notype _NET_WORKAREA» («_NET_WORKAREA = 0, 32, 1920, 1048, …») -> Area del
    primer escritorio, o None."""
    nums = [int(n) for n in re.findall(r"-?\d+", output.split("=", 1)[1])] if "=" in (output or "") else []
    if len(nums) < 4 or nums[2] <= 0 or nums[3] <= 0:
        return None
    x, y, w, h = nums[:4]
    return Area(x, y, x + w, y + h)


def cursor_pos():
    return tk_cursor_pos()


@cached(5)
def _net_workarea():
    code, out = run(["xprop", "-root", "-notype", "_NET_WORKAREA"], timeout=2)
    return parse_workarea(out) if code == 0 else None


def work_area(point=None):
    """Área libre de paneles. Tk no distingue monitores en X11: es la del escritorio entero."""
    return _net_workarea() or tk_screen()


def monitor_area(point):
    return tk_screen()


def work_areas():
    return [work_area()]


def virtual_screen():
    return tk_screen()


def bring_to_front(win):
    tk_bring_to_front(win)


# --- portapapeles ----------------------------------------------------------------------------------------

def _clip_tool():
    """«wl» (wl-clipboard) en Wayland, «x» (xclip) en X11, o None si falta la herramienta."""
    if is_wayland() and shutil.which("wl-paste"):
        return "wl"
    if os.environ.get("DISPLAY") and shutil.which("xclip"):
        return "x"
    return None


def clipboard_tools_missing():
    return _clip_tool() is None


def _clip_read(tool, target):
    if tool == "wl":
        args = ["wl-paste", "--no-newline", "--list-types"] if target == "TARGETS" else \
            ["wl-paste", "--no-newline", "--type", target]
    else:
        args = ["xclip", "-selection", "clipboard", "-t", target, "-o"]
    import subprocess
    try:
        r = subprocess.run(args, capture_output=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return b""
    return r.stdout if r.returncode == 0 else b""


def clipboard_token():
    """Huella del contenido del portapapeles (tipos + imagen o archivos copiados). No hay un contador de
    cambios como en Windows o macOS: si la huella cambia, cambió el portapapeles. None sin xclip/wl-clipboard."""
    tool = _clip_tool()
    if tool is None:
        return None
    types = _clip_read(tool, "TARGETS")
    h = hashlib.md5(types)
    names = types.decode("utf-8", "replace").split()
    for t in ("image/png", "text/uri-list"):
        if t in names:
            h.update(_clip_read(tool, t))
            break
    return h.hexdigest()


def copy_image_to_clipboard(img):
    """Copia una imagen PIL al portapapeles como PNG (wl-copy o xclip se quedan sirviéndola)."""
    import io
    import subprocess
    tool = _clip_tool()
    if tool is None:
        return False
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, "PNG")
    args = ["wl-copy", "--type", "image/png"] if tool == "wl" else \
        ["xclip", "-selection", "clipboard", "-t", "image/png", "-i"]
    try:
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.stdin.write(buf.getvalue())
        p.stdin.close()
    except OSError:
        return False
    # xclip y wl-copy siguen en segundo plano mientras nadie más copie: no se espera a que terminen
    time.sleep(0.1)
    return p.poll() in (None, 0)


def grab_screen():
    """Captura del escritorio (X11). En Wayland las aplicaciones no pueden capturar la pantalla."""
    from PIL import ImageGrab
    if is_wayland() and not os.environ.get("DISPLAY"):
        raise OSError("Wayland")
    img = ImageGrab.grab()
    if img.getbbox() is None:  # XWayland devuelve una imagen negra
        raise OSError("Wayland")
    return img


# --- archivos -----------------------------------------------------------------------------------------------

def pictures_folder():
    code, out = run(["xdg-user-dir", "PICTURES"], timeout=3)
    if code == 0 and out and out.rstrip("/") != os.path.expanduser("~"):
        return out
    return os.path.join(os.path.expanduser("~"), "Pictures")


def screenshots_folder():
    """Carpeta donde GNOME y KDE guardan las capturas: Imágenes/Screenshots (o la traducida)."""
    pictures = pictures_folder()
    for name in ("Screenshots", "Capturas de pantalla", "Capturas"):
        path = os.path.join(pictures, name)
        if os.path.isdir(path):
            return path
    return os.path.join(pictures, "Screenshots")


def trashinfo(path, deleted_at=None):
    """Contenido del .trashinfo de la especificación de papelera de freedesktop.org."""
    when = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(deleted_at))
    return f"[Trash Info]\nPath={urllib.parse.quote(os.path.abspath(path))}\nDeletionDate={when}\n"


def trash_manually(path, trash_dir=None):
    """Mueve el archivo a ~/.local/share/Trash como lo hace el gestor de archivos (recuperable desde él)."""
    data = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    trash_dir = trash_dir or os.path.join(data, "Trash")
    files, info = os.path.join(trash_dir, "files"), os.path.join(trash_dir, "info")
    os.makedirs(files, exist_ok=True)
    os.makedirs(info, exist_ok=True)
    base, ext = os.path.splitext(os.path.basename(path))
    name, n = base + ext, 1
    while os.path.exists(os.path.join(files, name)) or os.path.exists(os.path.join(info, name + ".trashinfo")):
        n += 1
        name = f"{base}.{n}{ext}"
    write_file(os.path.join(info, name + ".trashinfo"), trashinfo(path))
    shutil.move(path, os.path.join(files, name))
    return True


def send_to_trash(path):
    """Envía un archivo a la Papelera (recuperable). Devuelve True si se pudo."""
    code, __ = run(["gio", "trash", path])
    if code == 0 and not os.path.exists(path):
        return True
    try:
        return trash_manually(path) and not os.path.exists(path)
    except OSError:
        return False


def open_path(target):
    """Abre un archivo o una dirección con la aplicación predeterminada (xdg-open)."""
    import subprocess
    subprocess.Popen(["xdg-open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


single_instance = posix_single_instance
release_single_instance = posix_release_single_instance


def installed_by_setup():
    return False


def shortcut_paths():
    return [AUTOSTART_FILE]


def uninstall_registration():
    remove_file(AUTOSTART_FILE)


def uninstall_program():
    """La versión instalada con install.sh se quita con uninstall.sh."""


# --- iniciar al iniciar sesión (~/.config/autostart) ---------------------------------------------------------

def desktop_exec(argv):
    """Línea Exec= de un .desktop: cada argumento entre comillas si hace falta, con \\, ", ` y $ escapados."""
    def quote(a):
        if a and not re.search(r'[\s"\'`$\\<>~|&;*?#()]', a):
            return a
        return '"' + re.sub(r'(["`$\\])', r"\\\1", a) + '"'
    return " ".join(quote(a) for a in argv)


def autostart_entry(argv):
    """Contenido de ~/.config/autostart/clipqr.desktop."""
    return ("[Desktop Entry]\n"
            "Type=Application\n"
            f"Name={APP_NAME}\n"
            "Comment=QR codes from your clipboard\n"
            f"Exec={desktop_exec(argv)}\n"
            "Icon=clipqr\n"
            "Terminal=false\n"
            "X-GNOME-Autostart-enabled=true\n")


def autostart_current():
    return read_file(AUTOSTART_FILE)


def autostart_set(argv):
    write_file(AUTOSTART_FILE, autostart_entry(argv))


def autostart_remove():
    remove_file(AUTOSTART_FILE)


def msix_startup_state():
    return None


def msix_set_startup(enable):
    return False, ""


# --- bandeja del sistema ------------------------------------------------------------------------------------

def start_tray(icon, on_error=None):
    """pystray en su propio hilo con su propio bucle (GTK/AppIndicator o X11). Si falla (no hay bandeja, no
    hay servidor gráfico…), se avisa con on_error(excepción) desde ese hilo."""
    def work():
        try:
            icon.run()
        except Exception as e:
            if on_error is not None:
                on_error(e)

    def check_xembed():
        # el modo X11 de pystray (sin AppIndicator) necesita una bandeja XEmbed; GNOME no la tiene y el icono
        # quedaría invisible sin ningún error
        time.sleep(3)
        if hasattr(icon, "_systray_manager") and not icon._systray_manager and on_error is not None:
            on_error(RuntimeError("no hay bandeja del sistema (XEmbed)"))

    threading.Thread(target=work, daemon=True).start()
    threading.Thread(target=check_xembed, daemon=True).start()


def tray_options():
    return {}


# --- Wi‑Fi (NetworkManager) ---------------------------------------------------------------------------------

def nmcli_connect_args(ssid, password, auth, hidden=False):
    """Orden de nmcli para conectarse (crea o actualiza la conexión guardada)."""
    args = ["nmcli", "device", "wifi", "connect", ssid]
    auth = auth.upper()
    if password and auth not in ("", "NOPASS"):
        args += ["password", password]
        if auth == "WEP":
            args += ["wep-key-type", "key"]
    if hidden:
        args += ["hidden", "yes"]
    return args


def connect_wifi(ssid, password, auth, hidden=False):
    """Conecta con nmcli. Devuelve (ok, mensaje)."""
    if not shutil.which("nmcli"):
        return False, _("Hace falta NetworkManager (nmcli) para conectarse a la Wi‑Fi.")
    code, out = run(nmcli_connect_args(ssid, password, auth, hidden), timeout=45)
    if code == 0:
        return True, _("Conectado a «{red}».", red=ssid)
    return False, out or _("No se pudo conectar.")


def nmcli_split(line):
    """Campos de la salida «-t» de nmcli («yes:Mi\\:Red» -> ["yes", "Mi:Red"])."""
    return [f.replace("\\:", ":").replace("\\\\", "\\") for f in re.split(r"(?<!\\):", line)]


def parse_nmcli_active(output):
    """Salida de «nmcli -t -f ACTIVE,SSID device wifi» -> red conectada, o None."""
    for line in output.splitlines():
        fields = nmcli_split(line)
        if len(fields) >= 2 and fields[0] in ("yes", "sí") and fields[1]:
            return fields[1]
    return None


def security_for_key_mgmt(key_mgmt, password):
    """«wpa-psk» / «sae» -> WPA; «none» con clave (WEP) -> WEP; sin clave -> nopass."""
    if not password:
        return "nopass"
    return "WEP" if key_mgmt.strip() in ("none", "ieee8021x") else "WPA"


def current_wifi():
    """(red, contraseña, seguridad) de la Wi‑Fi actual, o None. NetworkManager da la contraseña de las
    redes guardadas por el usuario."""
    if not shutil.which("nmcli"):
        return None
    code, out = run(["nmcli", "-t", "-f", "ACTIVE,SSID", "device", "wifi"])
    ssid = parse_nmcli_active(out) if code == 0 else None
    if not ssid:
        return None
    __, password = run(["nmcli", "-s", "-g", "802-11-wireless-security.psk,802-11-wireless-security.wep-key0",
                        "connection", "show", "id", ssid])
    password = next((p for p in password.splitlines() if p.strip()), "")
    __, key_mgmt = run(["nmcli", "-g", "802-11-wireless-security.key-mgmt", "connection", "show", "id", ssid])
    return ssid, password, security_for_key_mgmt(key_mgmt, password)


# --- atajos de teclado globales ------------------------------------------------------------------------------

def hotkeys_unavailable_reason(env=None):
    """pynput escucha el teclado con X11; en Wayland el sistema no deja hacerlo a las aplicaciones."""
    return "wayland" if is_wayland(env) else None


def HotkeyManager():
    return PynputHotkeyManager(hotkeys_unavailable_reason())
