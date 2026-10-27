"""Todo lo específico de Windows: registro, DWM, monitores, portapapeles, papelera, atajos globales
(RegisterHotKey), Wi‑Fi (netsh), inicio con Windows y StartupTask (MSIX)."""
import ctypes
import os
import re
import sys
import threading
import time
from ctypes import wintypes

from clipqr import APP_NAME
from clipqr.hotkeys import parse_hotkey
from clipqr.i18n import _
from clipqr.platform.common import FROZEN, Area, parse_wifi_profile

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipQR"  # lo crea ClipQR-Setup.exe
CREATE_NO_WINDOW = 0x08000000

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
dwmapi = ctypes.windll.dwmapi
user32.GetClipboardSequenceNumber.restype = wintypes.DWORD
user32.GetParent.restype = wintypes.HWND

CLIPBOARD_POLL_MS = 150  # GetClipboardSequenceNumber es casi gratis: se puede mirar a menudo
FONT_SCALE = 1


def windows_theme():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
    except OSError:
        return "dark"

def taskbar_is_dark():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return not winreg.QueryValueEx(k, "SystemUsesLightTheme")[0]
    except OSError:
        return True


system_theme = windows_theme
tray_is_dark = taskbar_is_dark


def _hex_to_colorref(h):
    h = h.lstrip("#")
    return int(h[4:6] + h[2:4] + h[0:2], 16)

def style_window(win, border=None, dark=None):
    """Esquinas redondeadas de Windows 11, color de borde y barra de título oscura."""
    try:
        win.update_idletasks()
        hwnd = user32.GetParent(win.winfo_id()) or win.winfo_id()
        val = ctypes.c_int(2)  # DWMWCP_ROUND
        dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(val), ctypes.sizeof(val))
        if border:
            c = ctypes.c_int(_hex_to_colorref(border))
            dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(c), ctypes.sizeof(c))
        if dark is not None:
            d = ctypes.c_int(1 if dark else 0)
            dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(d), ctypes.sizeof(d))
    except Exception:
        pass


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def prepare_app(root):
    """Ajustes del proceso una vez creada la ventana raíz de Tk (en Windows, ninguno)."""


def screen_scale(root):
    """Factor de escala de la interfaz (1 = 96 ppp)."""
    return root.winfo_fpixels("1i") / 96


def pick_fonts(families):
    """(fuente de la interfaz, fuente de iconos o None, fuente monoespaciada)."""
    icon = next((f for f in ("Segoe Fluent Icons", "Segoe MDL2 Assets") if f in families), None)
    ui = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
    return ui, icon, "Consolas"


def ui_langid():
    """LANGID del idioma de la interfaz de Windows."""
    return kernel32.GetUserDefaultUILanguage()


def ui_locale_name():
    return None


def beep(root=None):
    import winsound
    winsound.MessageBeep(winsound.MB_ICONASTERISK)


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD)]


def _work_of(hmonitor):
    info = _MONITORINFO(cbSize=ctypes.sizeof(_MONITORINFO))
    user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
    r = info.rcWork
    return Area(r.left, r.top, r.right, r.bottom)


def force_foreground(hwnd):
    """Trae una ventana al frente aunque ClipQR esté en segundo plano. Windows se lo niega a las apps que
    no tienen el foco; uniéndose un instante a la entrada del hilo que sí lo tiene, se permite."""
    fg = user32.GetForegroundWindow()
    fg_thread = user32.GetWindowThreadProcessId(fg, None)
    me = kernel32.GetCurrentThreadId()
    attached = fg_thread and fg_thread != me and user32.AttachThreadInput(me, fg_thread, True)
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(me, fg_thread, False)


def bring_to_front(win):
    """Trae al frente una ventana de Tk (el foco de teclado lo pide quien llama con focus_force)."""
    force_foreground(user32.GetParent(win.winfo_id()))


def clipboard_token():
    """Número que cambia cada vez que cambia el portapapeles."""
    return user32.GetClipboardSequenceNumber()


def clipboard_tools_missing():
    return False


def copy_image_to_clipboard(img):
    """Copia una imagen PIL al portapapeles de Windows (formato CF_DIB: lo que pega Word, Paint, WhatsApp…)."""
    import io
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "BMP")
    data = buf.getvalue()[14:]  # sin la cabecera de archivo BMP
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    handle = kernel32.GlobalAlloc(0x2, len(data))  # GMEM_MOVEABLE
    ctypes.memmove(kernel32.GlobalLock(handle), data, len(data))
    kernel32.GlobalUnlock(handle)
    for __ in range(10):  # otra app puede tener el portapapeles abierto un instante
        if user32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return False
    try:
        user32.EmptyClipboard()
        return bool(user32.SetClipboardData(8, handle))  # CF_DIB; Windows se queda con la memoria
    finally:
        user32.CloseClipboard()


def grab_screen():
    """Captura de todo el escritorio (todos los monitores)."""
    from PIL import ImageGrab
    return ImageGrab.grab(all_screens=True)


def cursor_pos():
    p = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y


def work_area(point=None):
    """Área de trabajo (sin la barra de tareas) del monitor donde está `point`; por defecto, el del ratón."""
    x, y = point if point is not None else cursor_pos()
    user32.MonitorFromPoint.restype = wintypes.HMONITOR
    hmon = user32.MonitorFromPoint(wintypes.POINT(int(x), int(y)), 2)  # MONITOR_DEFAULTTONEAREST
    return _work_of(hmon)


def monitor_area(point):
    """Rectángulo completo (con la barra de tareas) del monitor donde está `point`."""
    user32.MonitorFromPoint.restype = wintypes.HMONITOR
    hmon = user32.MonitorFromPoint(wintypes.POINT(int(point[0]), int(point[1])), 2)
    info = _MONITORINFO(cbSize=ctypes.sizeof(_MONITORINFO))
    user32.GetMonitorInfoW(hmon, ctypes.byref(info))
    r = info.rcMonitor
    return Area(r.left, r.top, r.right, r.bottom)


def virtual_screen():
    """Rectángulo que abarca todos los monitores (puede empezar en coordenadas negativas)."""
    x, y = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)  # SM_X/YVIRTUALSCREEN
    return Area(x, y, x + user32.GetSystemMetrics(78), y + user32.GetSystemMetrics(79))


def work_areas():
    """Áreas de trabajo de todos los monitores conectados."""
    areas = []
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT),
                              wintypes.LPARAM)

    def cb(hmon, hdc, rect, data):
        areas.append(_work_of(hmon))
        return True

    user32.EnumDisplayMonitors(None, None, proc(cb), 0)
    return areas


def _is_packaged():
    """True si se ejecuta instalado como paquete MSIX (Microsoft Store)."""
    n = ctypes.c_uint32(0)
    return kernel32.GetCurrentPackageFullName(ctypes.byref(n), None) != 15700  # APPMODEL_ERROR_NO_PACKAGE

PACKAGED = _is_packaged()

STARTUP_TASK_ID = "ClipQRStartup"  # debe coincidir con el TaskId de msix/AppxManifest.xml

def _startup_task_call(fn):
    """Ejecuta fn(task) sobre el StartupTask del paquete (API WinRT asíncrona) y devuelve su resultado."""
    import asyncio
    from winrt.windows.applicationmodel import StartupTask

    async def run():
        task = await StartupTask.get_async(STARTUP_TASK_ID)
        res = fn(task)
        return await res if hasattr(res, "__await__") else res

    return asyncio.run(run())

def msix_startup_state():
    try:
        return _startup_task_call(lambda t: t.state.name.lower())
    except Exception:
        return None

def msix_set_startup(enable):
    """En MSIX el inicio con Windows es una StartupTask declarada en el manifiesto. Devuelve (ok, mensaje)."""
    try:
        if not enable:
            _startup_task_call(lambda t: t.disable())
            return True, ""
        state = _startup_task_call(lambda t: t.request_enable_async()).name.lower()
    except Exception as e:
        return False, _("No se pudo cambiar el inicio con Windows.\n{error}", error=e)
    if state.startswith("enabled"):
        return True, ""
    if state == "disabled_by_user":
        return False, _("Lo desactivaste desde Windows. Actívalo en\n"
                         "Configuración de Windows › Aplicaciones › Inicio.")
    return False, _("Windows no permite el inicio automático (directiva del equipo).")


# --- inicio con Windows (clave Run del registro) ------------------------------------------------------------

def gui_python():
    """pythonw.exe si existe (sin ventana de consola); si no, el Python actual."""
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return pyw if os.path.exists(pyw) else exe


def autostart_entry(argv):
    """Valor de la clave Run: «"C:\\…\\ClipQR.exe" --autostart» (las opciones van sin comillas)."""
    return " ".join(a if a.startswith("--") else f'"{a}"' for a in argv)


def autostart_current():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            return winreg.QueryValueEx(k, APP_NAME)[0]
    except OSError:
        return None


def autostart_set(argv):
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, autostart_entry(argv))


def autostart_remove():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.DeleteValue(k, APP_NAME)


def screenshots_folder():
    """Carpeta donde Windows guarda las capturas (Recortes, Win+Impr Pant): Imágenes › Capturas de pantalla."""
    import uuid

    class GUID(ctypes.Structure):
        _fields_ = [("data", ctypes.c_byte * 16)]

    guid = GUID()
    ctypes.memmove(ctypes.byref(guid), uuid.UUID("b7bede81-df94-4682-a7d8-57a52620b86f").bytes_le, 16)
    path = ctypes.c_wchar_p()
    if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(path)) != 0:
        return None
    return path.value

def send_to_recycle_bin(path):
    """Envía un archivo a la Papelera de reciclaje (recuperable). Devuelve True si se pudo."""
    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]

    FO_DELETE, FOF_SILENT, FOF_NOCONFIRMATION, FOF_ALLOWUNDO, FOF_NOERRORUI = 3, 0x4, 0x10, 0x40, 0x400
    op = SHFILEOPSTRUCTW(wFunc=FO_DELETE, pFrom=os.path.abspath(path) + "\0",
                         fFlags=FOF_SILENT | FOF_NOCONFIRMATION | FOF_ALLOWUNDO | FOF_NOERRORUI)
    return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0 and not os.path.exists(path)


send_to_trash = send_to_recycle_bin


def open_path(target):
    """Abre un archivo o una dirección con la aplicación predeterminada."""
    os.startfile(target)


_mutex = None


def single_instance():
    global _mutex
    _mutex = kernel32.CreateMutexW(None, False, "Local\\ClipQR_single_instance")
    return kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def release_single_instance():
    """Suelta el mutex de instancia única (al reiniciar, para que la nueva instancia pueda arrancar)."""
    global _mutex
    if _mutex:
        kernel32.CloseHandle(_mutex)
        _mutex = None

def installed_by_setup():
    import winreg
    try:
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY))
        return True
    except OSError:
        return False

def shortcut_paths():
    """Accesos directos que puede crear el asistente: menú Inicio y escritorio."""
    def folder(csidl):  # rutas reales (el escritorio puede estar en OneDrive)
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
        return buf.value

    return [os.path.join(folder(0x02), f"{APP_NAME}.lnk"),   # CSIDL_PROGRAMS (menú Inicio)
            os.path.join(folder(0x10), f"{APP_NAME}.lnk")]   # CSIDL_DESKTOPDIRECTORY


def uninstall_registration():
    """Desinstalación: cierra las otras instancias y quita inicio con Windows, la entrada de
    «Aplicaciones instaladas» y los accesos directos."""
    import subprocess
    import winreg
    subprocess.run(["taskkill", "/F", "/IM", "ClipQR.exe", "/FI", f"PID ne {os.getpid()}",
                    "/FI", f"PID ne {os.getppid()}"], capture_output=True, creationflags=CREATE_NO_WINDOW)
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


def uninstall_program():
    """El programa no puede borrarse a sí mismo mientras se ejecuta: cmd lo reintenta al salir."""
    import subprocess
    if not FROZEN:
        return
    exe, folder = sys.executable, os.path.dirname(sys.executable)
    setup_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", APP_NAME)
    if os.path.normcase(folder) == os.path.normcase(setup_dir):  # carpeta del asistente: entera
        remove = f'rmdir /s /q "{folder}" 2>nul & if not exist "{folder}" exit'
    else:  # en cualquier otro sitio solo el propio .exe (y la carpeta si queda vacía)
        remove = f'del /f /q "{exe}" 2>nul & if not exist "{exe}" (rmdir "{folder}" 2>nul & exit)'
    subprocess.Popen(f'cmd /c for /l %i in (1,1,30) do (ping -n 2 127.0.0.1 >nul & {remove})',
                     creationflags=CREATE_NO_WINDOW)


# --- bandeja del sistema ----------------------------------------------------------------------------------------

def start_tray(icon, on_error=None):
    """Arranca el icono de pystray en su propio hilo."""
    icon.run_detached()


def tray_options():
    return {}


# --- Wi‑Fi (netsh) -----------------------------------------------------------------------------------------------

def _xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def wlan_profile_xml(ssid, password, auth, hidden=False):
    """Perfil WLAN de Windows para `netsh wlan add profile`."""
    auth = auth.upper()
    if auth in ("", "NOPASS") or not password:
        authentication, encryption, key = "open", "none", ""
    elif auth == "WEP":
        authentication, encryption = "open", "WEP"
        key = ("<sharedKey><keyType>networkKey</keyType><protected>false</protected>"
               f"<keyMaterial>{_xml(password)}</keyMaterial></sharedKey>")
    else:
        authentication, encryption = ("WPA3SAE" if auth in ("SAE", "WPA3") else "WPA2PSK"), "AES"
        key = ("<sharedKey><keyType>passPhrase</keyType><protected>false</protected>"
               f"<keyMaterial>{_xml(password)}</keyMaterial></sharedKey>")
    return f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{_xml(ssid)}</name>
  <SSIDConfig><SSID><name>{_xml(ssid)}</name></SSID><nonBroadcast>{str(hidden).lower()}</nonBroadcast></SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>manual</connectionMode>
  <MSM><security>
    <authEncryption><authentication>{authentication}</authentication><encryption>{encryption}</encryption><useOneX>false</useOneX></authEncryption>
    {key}
  </security></MSM>
</WLANProfile>"""


def _netsh(*args):
    import subprocess
    r = subprocess.run(["netsh", "wlan", *args], capture_output=True, creationflags=CREATE_NO_WINDOW)
    raw = r.stdout or r.stderr
    try:  # netsh escribe en UTF-8 o en la página OEM según el equipo
        return r.returncode, raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return r.returncode, raw.decode("oem", errors="replace").strip()


def connect_wifi(ssid, password, auth, hidden=False):
    """Crea un perfil Wi-Fi para el usuario actual y conecta. Devuelve (ok, mensaje)."""
    import tempfile
    profile = wlan_profile_xml(ssid, password, auth, hidden)

    def connected():
        __, out = _netsh("show", "interfaces")
        return any(re.match(r"^\s*SSID\s*:\s*(.*)$", l) and l.split(":", 1)[1].strip() == ssid
                   for l in out.splitlines())

    fd, path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(profile)
        # 1) perfil para todos los usuarios (actualiza el que ya exista, que es lo normal);
        # 2) si no hay permiso, perfil solo para este usuario;
        # 3) si ninguno se puede escribir pero ya hay un perfil con ese nombre, se usa ese.
        code, err = _netsh("add", "profile", f"filename={path}", "user=all")
        if code != 0:
            code, err2 = _netsh("add", "profile", f"filename={path}", "user=current")
            if code != 0:
                exists, __ = _netsh("show", "profile", f"name={ssid}")
                if exists != 0:
                    return False, err2 or err or _("No se pudo crear el perfil Wi‑Fi.")
    finally:
        os.remove(path)

    if connected():
        return True, _("Ya estás conectado a «{red}».", red=ssid)
    code, out = _netsh("connect", f"name={ssid}", f"ssid={ssid}")
    if code != 0:
        return False, out or _("No se pudo conectar.")
    for __ in range(20):  # esperar hasta ~10 s a que Windows confirme la conexión
        time.sleep(0.5)
        if connected():
            return True, _("Conectado a «{red}».", red=ssid)
    return False, _("Windows no confirmó la conexión a «{red}».\n"
                    "Comprueba que la red está al alcance y que la contraseña es correcta.", red=ssid)


def current_wifi():
    """(red, contraseña, seguridad) de la Wi‑Fi a la que está conectado el equipo, o None.
    Windows solo da la contraseña de redes cuyo perfil está guardado en este equipo."""
    __, out = _netsh("show", "interfaces")
    ssid = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                 if re.match(r"^\s*SSID\s*:", l)), None)
    if not ssid:
        return None
    __, profile = _netsh("show", "profile", f"name={ssid}", "key=clear")
    password, security = parse_wifi_profile(profile)
    return ssid, password, security


# --- atajos de teclado globales (RegisterHotKey) ---------------------------------------------------------------

WM_HOTKEY, WM_QUIT, WM_APP = 0x0312, 0x0012, 0x8000


def hotkeys_unavailable_reason():
    """Por qué no hay atajos globales (None = sí los hay)."""
    return None


class HotkeyManager:
    """Registra atajos en un hilo propio. set() reemplaza todos los atajos; devuelve los que fallaron
    (por ejemplo, porque otra aplicación ya usa esa combinación).

    Windows entrega WM_HOTKEY al hilo que registró el atajo, así que un hilo propio registra los atajos y
    espera mensajes; al pulsarse uno, llama a su función (que debe pasar el trabajo al hilo de Tk)."""

    available = True

    def __init__(self):
        self._thread_id = None
        self._ready = threading.Event()
        self._pending = None
        self._result = None
        self._done = threading.Event()
        self._callbacks = {}
        threading.Thread(target=self._loop, daemon=True).start()
        self._ready.wait(2)

    def set(self, hotkeys):
        """hotkeys: {texto del atajo: función}. Devuelve la lista de atajos que no se pudieron registrar."""
        self._pending = dict(hotkeys)
        self._done.clear()
        user32.PostThreadMessageW(self._thread_id, WM_APP, 0, 0)
        self._done.wait(2)
        return self._result or []

    def stop(self):
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def _apply(self):
        for hid in list(self._callbacks):
            user32.UnregisterHotKey(None, hid)
        self._callbacks.clear()
        failed = []
        for hid, (text, fn) in enumerate(self._pending.items(), start=1):
            try:
                mods, vk = parse_hotkey(text)
            except ValueError:
                failed.append(text)
                continue
            if user32.RegisterHotKey(None, hid, mods, vk):
                self._callbacks[hid] = fn
            else:
                failed.append(text)
        self._result = failed
        self._done.set()

    def _loop(self):
        self._thread_id = kernel32.GetCurrentThreadId()
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)  # crea la cola de mensajes del hilo
        self._ready.set()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_APP:
                self._apply()
            elif msg.message == WM_HOTKEY and msg.wParam in self._callbacks:
                try:
                    self._callbacks[msg.wParam]()
                except Exception:
                    pass
        for hid in list(self._callbacks):
            user32.UnregisterHotKey(None, hid)
