"""Todo lo específico de Windows: registro, DWM, rutas, papelera, StartupTask (MSIX)."""
import ctypes
import os
import sys
from ctypes import wintypes

from clipqr import APP_NAME

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipQR"  # lo crea ClipQR-Setup.exe

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
dwmapi = ctypes.windll.dwmapi
user32.GetClipboardSequenceNumber.restype = wintypes.DWORD
user32.GetParent.restype = wintypes.HWND


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


def work_area():
    """Área de trabajo de la pantalla principal (sin la barra de tareas)."""
    rect = wintypes.RECT()
    user32.SystemParametersInfoW(0x30, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA
    return rect


FROZEN = getattr(sys, "frozen", False)  # empaquetado con PyInstaller

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
        return False, f"No se pudo cambiar el inicio con Windows.\n{e}"
    if state.startswith("enabled"):
        return True, ""
    if state == "disabled_by_user":
        return False, ("Lo desactivaste desde Windows. Actívalo en\n"
                       "Configuración de Windows › Aplicaciones › Inicio.")
    return False, "Windows no permite el inicio automático (directiva del equipo)."

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

def single_instance():
    kernel32.CreateMutexW(None, False, "Local\\ClipQR_single_instance")
    return kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS

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
