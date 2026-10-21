"""Asistente de instalación de ClipQR (se compila como ClipQR-Setup.exe con build_setup.bat).

Una sola pantalla: opciones (inicio con Windows, acceso directo en el escritorio) y «Instalar».
Instala para el usuario actual, sin permisos de administrador, en %LOCALAPPDATA%\\Programs\\ClipQR,
y registra ClipQR en «Aplicaciones instaladas» para poder desinstalarlo desde Windows.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import winreg

try:
    from _version import VERSION  # lo genera build_setup.bat
except ImportError:
    VERSION = "dev"

APP = "ClipQR"
PUBLISHER = "MojeZcg"
URL = "https://github.com/MojeZcg/ClipQR"
INSTALL_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Programs", APP)
EXE = os.path.join(INSTALL_DIR, f"{APP}.exe")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipQR"
NO_WINDOW = 0x08000000

THEMES = {
    "dark": dict(bg="#202020", fg="#f3f3f3", muted="#a3a3a3", btn="#383838", btn_hover="#454545"),
    "light": dict(bg="#f3f3f3", fg="#1b1b1b", muted="#5f5f5f", btn="#e2e2e2", btn_hover="#d4d4d4"),
}
ACCENT, ACCENT_HOVER = "#4f8cff", "#3f74d8"


def resource(name):
    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), name)


def windows_theme():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
    except OSError:
        return "dark"


def special_folder(csidl):
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
    return buf.value


def make_shortcut(lnk, target):
    q = lambda s: s.replace("'", "''")
    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{q(lnk)}');"
          f"$s.TargetPath='{q(target)}';$s.WorkingDirectory='{q(os.path.dirname(target))}';"
          f"$s.IconLocation='{q(target)},0';$s.Description='Lector de QR para el portapapeles';$s.Save()")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                   capture_output=True, creationflags=NO_WINDOW, check=True)


def install(autostart, desktop):
    # cerrar ClipQR si está abierto (actualización)
    subprocess.run(["taskkill", "/F", "/IM", f"{APP}.exe"], capture_output=True, creationflags=NO_WINDOW)
    # se instala la versión en carpeta (ClipQR.exe + _internal): arranca al momento, porque no tiene
    # que descomprimirse en cada inicio como el .exe portátil de un solo archivo
    for attempt in range(10):  # el proceso cerrado puede tardar un momento en soltar los archivos
        try:
            if os.path.isdir(INSTALL_DIR):
                shutil.rmtree(INSTALL_DIR)  # quitar la versión anterior (incluida una de un solo archivo)
            shutil.copytree(resource("app"), INSTALL_DIR)
            break
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(0.5)

    start_menu = os.path.join(special_folder(0x02), f"{APP}.lnk")       # CSIDL_PROGRAMS
    desktop_lnk = os.path.join(special_folder(0x10), f"{APP}.lnk")      # CSIDL_DESKTOPDIRECTORY
    make_shortcut(start_menu, EXE)
    if desktop:
        make_shortcut(desktop_lnk, EXE)
    elif os.path.exists(desktop_lnk):
        os.remove(desktop_lnk)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
        if autostart:
            winreg.SetValueEx(k, APP, 0, winreg.REG_SZ, f'"{EXE}"')
        else:
            try:
                winreg.DeleteValue(k, APP)
            except OSError:
                pass

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as k:
        for name, value in (("DisplayName", APP), ("DisplayVersion", VERSION), ("Publisher", PUBLISHER),
                            ("DisplayIcon", EXE), ("InstallLocation", INSTALL_DIR),
                            ("UninstallString", f'"{EXE}" --uninstall'),
                            ("QuietUninstallString", f'"{EXE}" --uninstall /silent'), ("URLInfoAbout", URL)):
            winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
        winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)
        size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(INSTALL_DIR) for f in files)
        winreg.SetValueEx(k, "EstimatedSize", 0, winreg.REG_DWORD, size // 1024)


def parse_args(argv):
    """Opciones de línea de órdenes (sin distinguir mayúsculas; acepta / o -):
    /silent      instala sin ventanas (para winget y despliegues)
    /noautostart sin inicio con Windows (por defecto se activa)
    /desktop     crea el acceso directo en el escritorio
    /launch      abre ClipQR al terminar"""
    flags = {a.lower().lstrip("/-") for a in argv}
    unknown = flags - {"silent", "noautostart", "desktop", "launch"}
    if unknown:
        raise ValueError(f"Opción desconocida: {', '.join(sorted(unknown))}")
    return {"silent": "silent" in flags, "autostart": "noautostart" not in flags,
            "desktop": "desktop" in flags, "launch": "launch" in flags}


def silent_install(opts):
    """Instalación sin interfaz. Devuelve el código de salida y deja un registro en %TEMP%."""
    import tempfile
    log = os.path.join(tempfile.gettempdir(), "ClipQR-Setup.log")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ClipQR {VERSION} instalación silenciosa {opts}\n")
        try:
            install(opts["autostart"], opts["desktop"])
            f.write(f"  instalado en {INSTALL_DIR}\n")
        except Exception as e:
            f.write(f"  ERROR: {e!r}\n")
            return 1
    if opts["launch"]:
        subprocess.Popen([EXE], cwd=INSTALL_DIR, creationflags=0x00000008)  # DETACHED_PROCESS
    return 0


class Wizard:
    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        self.root = tk.Tk()
        self.dpi = self.root.winfo_fpixels("1i") / 96
        self.c = THEMES[windows_theme()]
        c = self.c
        r = self.root
        r.title(f"Instalar {APP}")
        r.configure(bg=c["bg"])
        r.resizable(False, False)
        try:
            self.logo = tk.PhotoImage(file=resource("logo-white.png" if windows_theme() == "dark" else "logo.png"))
            r.iconphoto(True, self.logo)
            f = max(1, self.logo.width() // self.px(72))
            self.logo_small = self.logo.subsample(f, f)
        except tk.TclError:
            self.logo_small = None
        self._dark_titlebar()
        self.body = tk.Frame(r, bg=c["bg"])
        self.body.pack(fill="both", expand=True, padx=self.px(28), pady=self.px(24))
        self.page_options()
        r.update_idletasks()
        w, h = self.px(470), r.winfo_reqheight()
        r.geometry(f"{w}x{h}+{(r.winfo_screenwidth() - w) // 2}+{(r.winfo_screenheight() - h) // 2}")
        # al abrirse desde el navegador o el Explorador puede quedar detrás: traerlo al frente
        r.attributes("-topmost", True)
        r.after(300, lambda: (r.attributes("-topmost", False), r.focus_force()))

    def px(self, n):
        return int(n * self.dpi)

    def font(self, size, weight="normal"):
        return ("Segoe UI", size, weight)

    def _dark_titlebar(self):
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            v = ctypes.c_int(1 if windows_theme() == "dark" else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(v), ctypes.sizeof(v))
        except Exception:
            pass

    def button(self, parent, text, cmd, primary=False):
        c = self.c
        bg, hover = (ACCENT, ACCENT_HOVER) if primary else (c["btn"], c["btn_hover"])
        fg = "white" if primary else c["fg"]
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                      relief="flat", bd=0, padx=self.px(18), pady=self.px(6), cursor="hand2",
                      font=self.font(10, "bold" if primary else "normal"), highlightthickness=0)
        b.bind("<Enter>", lambda e: b.cget("state") != "disabled" and b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def check(self, parent, text, var):
        c = self.c
        return tk.Checkbutton(parent, text=text, variable=var, bg=c["bg"], fg=c["fg"], activebackground=c["bg"],
                              activeforeground=c["fg"], selectcolor=c["btn"], font=self.font(10),
                              highlightthickness=0, bd=0, anchor="w", cursor="hand2")

    def header(self, title, subtitle):
        c = self.c
        top = tk.Frame(self.body, bg=c["bg"])
        top.pack(fill="x")
        if self.logo_small:
            tk.Label(top, image=self.logo_small, bg=c["bg"]).pack(side="left", padx=(0, self.px(16)))
        txt = tk.Frame(top, bg=c["bg"])
        txt.pack(side="left", fill="x")
        tk.Label(txt, text=title, bg=c["bg"], fg=c["fg"], font=self.font(16, "bold"), anchor="w").pack(anchor="w")
        tk.Label(txt, text=subtitle, bg=c["bg"], fg=c["muted"], font=self.font(9), anchor="w", justify="left",
                 wraplength=self.px(300)).pack(anchor="w")

    def text(self, parent, msg):
        """Párrafo que se ajusta al ancho de la ventana (en vez de cortarse por los lados)."""
        c = self.c
        tk.Label(parent, text=msg, bg=c["bg"], fg=c["fg"], font=self.font(10), justify="left", anchor="w",
                 wraplength=self.px(470 - 56)).pack(fill="x", anchor="w", pady=(self.px(18), self.px(12)))

    def clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def page_options(self):
        c = self.c
        self.clear()
        self.header(f"Instalar {APP}", f"Versión {VERSION} · lector de QR para el portapapeles")
        self.text(self.body, "Detecta códigos QR y de barras en tus capturas e imágenes copiadas. "
                             "Se instala solo para tu usuario, sin permisos de administrador.")
        self.autostart = tk.BooleanVar(value=True)
        self.desktop = tk.BooleanVar(value=False)
        self.check(self.body, "  Iniciar ClipQR con Windows", self.autostart).pack(anchor="w", pady=self.px(2))
        self.check(self.body, "  Crear acceso directo en el escritorio", self.desktop).pack(anchor="w", pady=self.px(2))
        self.status = tk.Label(self.body, text="", bg=c["bg"], fg=c["muted"], font=self.font(9), justify="left")
        self.status.pack(anchor="w", pady=(self.px(10), 0))
        bar = tk.Frame(self.body, bg=c["bg"])
        bar.pack(fill="x", pady=(self.px(10), 0))
        self.install_btn = self.button(bar, "Instalar", self.do_install, primary=True)
        self.install_btn.pack(side="right")
        self.button(bar, "Cancelar", self.root.destroy).pack(side="right", padx=(0, self.px(8)))
        self.install_btn.focus_set()
        self.root.bind("<Return>", lambda e: self.do_install())

    def do_install(self):
        if str(self.install_btn.cget("state")) == "disabled":
            return
        self.install_btn.config(state="disabled", text="Instalando…")
        self.status.config(text="Copiando archivos…", fg=self.c["muted"])
        result = {}

        def work():  # en segundo plano: la ventana sigue respondiendo mientras se copia
            try:
                install(self.autostart.get(), self.desktop.get())
            except Exception as e:
                result["error"] = e
            result["done"] = True

        def check():
            if not result.get("done"):
                self.root.after(100, check)
            elif "error" in result:
                self.install_btn.config(state="normal", text="Reintentar")
                self.status.config(text=f"No se pudo instalar: {result['error']}", fg="#e5484d")
            else:
                self.page_done()

        threading.Thread(target=work, daemon=True).start()
        check()

    def page_done(self):
        c = self.c
        self.clear()
        self.header("ClipQR está instalado ✓", f"En {INSTALL_DIR}")
        self.text(self.body, "Lo encontrarás en el menú Inicio. Cuando está abierto vive en la bandeja, junto al "
                             "reloj: haz una captura de un QR y aparecerá el aviso.\n\n"
                             "Para desinstalarlo: Configuración de Windows › Aplicaciones › ClipQR.")
        self.launch = tk.BooleanVar(value=True)
        self.check(self.body, "  Abrir ClipQR ahora", self.launch).pack(anchor="w")
        bar = tk.Frame(self.body, bg=c["bg"])
        bar.pack(fill="x", pady=(self.px(16), 0))
        self.button(bar, "Finalizar", self.finish, primary=True).pack(side="right")
        self.root.bind("<Return>", lambda e: self.finish())
        self.root.update_idletasks()
        self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_reqheight()}")

    def finish(self):
        if self.launch.get():
            subprocess.Popen([EXE], cwd=INSTALL_DIR, creationflags=0x00000008)  # DETACHED_PROCESS
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        options = parse_args(sys.argv[1:])
    except ValueError as err:
        sys.exit(f"{err}\n{parse_args.__doc__}")
    if options["silent"]:
        sys.exit(silent_install(options))
    Wizard().run()
