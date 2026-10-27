"""macOS: portapapeles (NSPasteboard), barra de menús, LaunchAgent para iniciar al iniciar sesión,
papelera, Wi‑Fi (networksetup) y atajos con pynput.

AppKit (pyobjc) se importa dentro de cada función: si falta, se usan órdenes del sistema (osascript,
defaults…) y este módulo se puede importar (y probar) en cualquier sistema."""
import os
import plistlib
import re

from clipqr.hotkeys import PynputHotkeyManager
from clipqr.i18n import _
from clipqr.platform.common import (Area, cached, first_family, posix_release_single_instance, posix_single_instance,
                                    read_file, remove_file, run, tk_bring_to_front, tk_cursor_pos, tk_root,
                                    tk_screen, write_file)

CLIPBOARD_POLL_MS = 150  # changeCount es casi gratis
FONT_SCALE = 4 / 3  # Tk mide los puntos a 72 ppp en macOS; en Windows, a 96: así el texto mide lo mismo
MENU_BAR = 25  # alto aproximado de la barra de menús (si no se puede preguntar a AppKit)
BUNDLE_ID = "io.github.mojezcg.clipqr"
LAUNCH_AGENT = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents", f"{BUNDLE_ID}.plist")

PACKAGED = False


def _appkit():
    try:
        import AppKit
        return AppKit
    except Exception:
        return None


# --- tema y aspecto -------------------------------------------------------------------------------------------

def parse_interface_style(output, code):
    """Salida de «defaults read -g AppleInterfaceStyle»: «Dark» si el modo oscuro está activo; si no, la
    clave no existe (código distinto de 0)."""
    return "dark" if code == 0 and output.strip().lower() == "dark" else "light"


@cached(5)
def system_theme():
    code, out = run(["defaults", "read", "-g", "AppleInterfaceStyle"], timeout=3)
    return parse_interface_style(out, code)


def tray_is_dark():
    return system_theme() == "dark"


def style_window(win, border=None, dark=None):
    """En macOS las ventanas ya tienen el aspecto del sistema. Las ventanas normales (historial,
    configuración, crear QR: las que pasan `dark`) se traen al frente: una app sin icono en el Dock no se
    activa sola y quedarían detrás de las demás. Los avisos (`border`) no, para no quitar el foco."""
    if dark is not None:
        bring_to_front(win)


def enable_dpi_awareness():
    pass


def prepare_app(root):
    """Sin icono en el Dock (vive en la barra de menús), también al ejecutarlo desde el código fuente."""
    AppKit = _appkit()
    if AppKit is not None:
        try:
            AppKit.NSApplication.sharedApplication().setActivationPolicy_(
                AppKit.NSApplicationActivationPolicyAccessory)
        except Exception:
            pass


def screen_scale(root):
    return 1.0  # Tk ya trabaja en puntos; la pantalla Retina la escala el sistema


def pick_fonts(families):
    ui = first_family((".AppleSystemUIFont", "SF Pro Text", "Helvetica Neue"), families, "Helvetica")
    mono = first_family(("SF Mono", "Menlo", "Monaco"), families, "Courier")
    return ui, None, mono


def ui_langid():
    return None


def parse_apple_languages(output):
    """Salida de «defaults read -g AppleLanguages» («( "es-AR", "en-US" )») -> «es-AR»."""
    m = re.search(r'"?([A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)*)"?\s*[,)]', output or "")
    return m.group(1) if m else None


def ui_locale_name():
    """Idioma preferido del usuario. Las apps abiertas desde el Finder no reciben LANG."""
    code, out = run(["defaults", "read", "-g", "AppleLanguages"], timeout=3)
    return parse_apple_languages(out) if code == 0 else None


def beep(root=None):
    root = root or tk_root()
    if root is not None:
        root.bell()


# --- monitores ----------------------------------------------------------------------------------------------

def _screens():
    """[(monitor, área de trabajo)] en coordenadas de Tk (origen arriba a la izquierda del monitor principal).
    Cocoa cuenta desde abajo a la izquierda: se da la vuelta con el alto del monitor principal."""
    AppKit = _appkit()
    if AppKit is not None:
        try:
            screens = list(AppKit.NSScreen.screens())
            main_h = screens[0].frame().size.height
            out = []
            for s in screens:
                f, v = s.frame(), s.visibleFrame()
                out.append((cocoa_to_area(f, main_h), cocoa_to_area(v, main_h)))
            if out:
                return out
        except Exception:
            pass
    full = tk_screen()
    return [(full, Area(full.left, full.top + MENU_BAR, full.right, full.bottom))]


def cocoa_to_area(rect, main_h):
    x, y, w, h = rect.origin.x, rect.origin.y, rect.size.width, rect.size.height
    return Area(int(x), int(main_h - y - h), int(x + w), int(main_h - y))


def cursor_pos():
    return tk_cursor_pos()


def _pick(point, index):
    x, y = point if point is not None else cursor_pos()
    screens = _screens()
    hit = next((s for s in screens if s[0].left <= x < s[0].right and s[0].top <= y < s[0].bottom), screens[0])
    return hit[index]


def work_area(point=None):
    return _pick(point, 1)


def monitor_area(point):
    return _pick(point, 0)


def work_areas():
    return [s[1] for s in _screens()]


def virtual_screen():
    screens = [s[0] for s in _screens()]
    return Area(min(a.left for a in screens), min(a.top for a in screens),
                max(a.right for a in screens), max(a.bottom for a in screens))


def bring_to_front(win):
    """Una app sin icono en el Dock no pasa al frente sola: hay que activarla."""
    AppKit = _appkit()
    if AppKit is not None:
        try:
            AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        except Exception:
            pass
    tk_bring_to_front(win)


# --- portapapeles y pantalla --------------------------------------------------------------------------------

def clipboard_token():
    """changeCount del portapapeles general (cambia con cada copia), o None sin pyobjc."""
    AppKit = _appkit()
    if AppKit is None:
        return None
    try:
        return int(AppKit.NSPasteboard.generalPasteboard().changeCount())
    except Exception:
        return None


def clipboard_tools_missing():
    return False


def copy_image_to_clipboard(img):
    """Copia una imagen PIL al portapapeles como PNG."""
    import io
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, "PNG")
    data = buf.getvalue()
    AppKit = _appkit()
    if AppKit is not None:
        try:
            pb = AppKit.NSPasteboard.generalPasteboard()
            pb.clearContents()
            return bool(pb.setData_forType_(AppKit.NSData.dataWithBytes_length_(data, len(data)),
                                            AppKit.NSPasteboardTypePNG))
        except Exception:
            pass
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".png", prefix="clipqr_")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    try:
        code, __ = run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{path}") as «class PNGf»)'])
        return code == 0
    finally:
        remove_file(path)


def grab_screen():
    """Captura de la pantalla. Sin el permiso de Grabación de pantalla, macOS devuelve solo el fondo."""
    from PIL import ImageGrab
    return ImageGrab.grab()


# --- archivos -----------------------------------------------------------------------------------------------

def screenshots_folder():
    """Carpeta donde macOS guarda las capturas: la elegida en Captura de pantalla o, por defecto, el Escritorio."""
    code, out = run(["defaults", "read", "com.apple.screencapture", "location"], timeout=3)
    if code == 0 and out:
        path = os.path.expanduser(out.strip())
        if os.path.isdir(path):
            return path
    return os.path.join(os.path.expanduser("~"), "Desktop")


def send_to_trash(path):
    """Envía un archivo a la Papelera (recuperable). Devuelve True si se pudo."""
    path = os.path.abspath(path)
    try:
        import Foundation
        url = Foundation.NSURL.fileURLWithPath_(path)
        ok, __, __ = Foundation.NSFileManager.defaultManager().trashItemAtURL_resultingItemURL_error_(url, None, None)
        if ok:
            return not os.path.exists(path)
    except Exception:
        pass
    escaped = path.replace("\\", "\\\\").replace('"', '\\"')
    code, __ = run(["osascript", "-e", f'tell application "Finder" to delete POSIX file "{escaped}"'])
    return code == 0 and not os.path.exists(path)


def open_path(target):
    """Abre un archivo o una dirección con la aplicación predeterminada (orden «open»)."""
    import subprocess
    subprocess.Popen(["open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


single_instance = posix_single_instance
release_single_instance = posix_release_single_instance


def installed_by_setup():
    return False


def shortcut_paths():
    return [LAUNCH_AGENT]


def uninstall_registration():
    remove_file(LAUNCH_AGENT)


def uninstall_program():
    """El .app se borra arrastrándolo a la Papelera."""


# --- iniciar al iniciar sesión (LaunchAgent) -----------------------------------------------------------------

def autostart_entry(argv):
    """Contenido de ~/Library/LaunchAgents/io.github.mojezcg.clipqr.plist."""
    return plistlib.dumps({"Label": BUNDLE_ID, "ProgramArguments": list(argv), "RunAtLoad": True,
                           "ProcessType": "Interactive"}).decode("utf-8")


def autostart_current():
    return read_file(LAUNCH_AGENT)


def autostart_set(argv):
    write_file(LAUNCH_AGENT, autostart_entry(argv))


def autostart_remove():
    remove_file(LAUNCH_AGENT)


def msix_startup_state():
    return None


def msix_set_startup(enable):
    return False, ""


# --- barra de menús -----------------------------------------------------------------------------------------

def start_tray(icon, on_error=None):
    """El NSStatusItem lo crea pystray en el hilo principal (el de Tk). No hace falta un bucle propio:
    Tk ya atiende los eventos de Cocoa (es una app de Cocoa), también los del menú. El icono se muestra
    desde aquí (hilo principal) y no desde el hilo de preparación de pystray: AppKit solo admite cambios en
    la interfaz desde el hilo principal."""
    icon.run_detached(setup=lambda icon: None)
    icon.visible = True


def tray_options():
    """Opciones de pystray.Icon: que use la NSApplication de Tk."""
    AppKit = _appkit()
    return {"nsapplication": AppKit.NSApplication.sharedApplication()} if AppKit is not None else {}


# --- Wi‑Fi (networksetup) ------------------------------------------------------------------------------------

def parse_wifi_device(output):
    """Salida de «networksetup -listallhardwareports» -> dispositivo Wi‑Fi («en0»), o None."""
    port = None
    for line in output.splitlines():
        if line.startswith("Hardware Port:"):
            port = line.split(":", 1)[1].strip()
        elif line.startswith("Device:") and port in ("Wi-Fi", "AirPort", "Wi‑Fi"):
            return line.split(":", 1)[1].strip()
    return None


def networksetup_join_args(device, ssid, password):
    args = ["networksetup", "-setairportnetwork", device, ssid]
    return args + [password] if password else args


def _wifi_device():
    code, out = run(["networksetup", "-listallhardwareports"])
    return parse_wifi_device(out) if code == 0 else None


def connect_wifi(ssid, password, auth, hidden=False):
    """Conecta con networksetup (sirve también para redes ocultas). Devuelve (ok, mensaje)."""
    device = _wifi_device()
    if not device:
        return False, _("No se encontró la interfaz Wi‑Fi.")
    use_password = password if auth.upper() not in ("", "NOPASS") else ""
    code, out = run(networksetup_join_args(device, ssid, use_password), timeout=40)
    # networksetup sale con 0 aunque falle: el error solo aparece en la salida
    if code == 0 and not out:
        return True, _("Conectado a «{red}».", red=ssid)
    return False, out or _("No se pudo conectar.")


def parse_airport_network(output):
    """«Current Wi-Fi Network: MiRed» -> «MiRed» (None si no está conectado)."""
    m = re.match(r"^Current (?:Wi-Fi|AirPort) Network:\s*(.+)$", output.strip())
    return m.group(1).strip() if m else None


def current_wifi():
    """(red, contraseña, seguridad) de la Wi‑Fi actual, o None. La contraseña sale del llavero: macOS
    pide permiso (usuario y contraseña del Mac) antes de darla."""
    device = _wifi_device()
    if not device:
        return None
    __, out = run(["networksetup", "-getairportnetwork", device])
    ssid = parse_airport_network(out)
    if not ssid:
        return None
    code, password = run(["security", "find-generic-password", "-wa", ssid], timeout=60)
    password = password if code == 0 else ""
    return ssid, password, "WPA" if password else "nopass"


# --- atajos de teclado globales ------------------------------------------------------------------------------

def hotkeys_unavailable_reason():
    return None


def accessibility_trusted():
    """True si ClipQR tiene el permiso de Accesibilidad (sin él, pynput no recibe las teclas)."""
    try:
        import HIServices
        return bool(HIServices.AXIsProcessTrusted())
    except Exception:
        return True  # no se puede saber: no se avisa


def HotkeyManager():
    return PynputHotkeyManager(hotkeys_unavailable_reason(), trusted=accessibility_trusted)

