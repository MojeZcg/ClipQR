"""Acciones que se ejecutan al pulsar un botón: Wi-Fi, abrir archivos, buscar la captura guardada."""
import hashlib
import os
import re
import time

from PIL import Image

from clipqr.winplatform import screenshots_folder

def _xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))

def connect_wifi(ssid, password, auth, hidden=False):
    """Crea un perfil Wi-Fi para el usuario actual y conecta. Devuelve (ok, mensaje)."""
    import subprocess
    import tempfile
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
    profile = f"""<?xml version="1.0"?>
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
    def run(*args):
        r = subprocess.run(["netsh", "wlan", *args], capture_output=True,
                           creationflags=0x08000000)  # CREATE_NO_WINDOW
        raw = r.stdout or r.stderr
        try:  # netsh escribe en UTF-8 o en la página OEM según el equipo
            out = raw.decode("utf-8")
        except UnicodeDecodeError:
            out = raw.decode("oem", errors="replace")
        return r.returncode, out.strip()

    def connected():
        _, out = run("show", "interfaces")
        return any(re.match(r"^\s*SSID\s*:\s*(.*)$", l) and l.split(":", 1)[1].strip() == ssid
                   for l in out.splitlines())

    fd, path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(profile)
        # 1) perfil para todos los usuarios (actualiza el que ya exista, que es lo normal);
        # 2) si no hay permiso, perfil solo para este usuario;
        # 3) si ninguno se puede escribir pero ya hay un perfil con ese nombre, se usa ese.
        code, err = run("add", "profile", f"filename={path}", "user=all")
        if code != 0:
            code, err2 = run("add", "profile", f"filename={path}", "user=current")
            if code != 0:
                exists, _ = run("show", "profile", f"name={ssid}")
                if exists != 0:
                    return False, err2 or err or "No se pudo crear el perfil Wi-Fi."
    finally:
        os.remove(path)

    if connected():
        return True, f"Ya estás conectado a «{ssid}»."
    code, out = run("connect", f"name={ssid}", f"ssid={ssid}")
    if code != 0:
        return False, out or "No se pudo conectar."
    for _ in range(20):  # esperar hasta ~10 s a que Windows confirme la conexión
        time.sleep(0.5)
        if connected():
            return True, f"Conectado a «{ssid}»."
    return False, (f"Windows no confirmó la conexión a «{ssid}».\n"
                   "Comprueba que la red está al alcance y que la contraseña es correcta.")

def _netsh(*args):
    import subprocess
    r = subprocess.run(["netsh", "wlan", *args], capture_output=True, creationflags=0x08000000)
    raw = r.stdout or r.stderr
    try:  # netsh escribe en UTF-8 o en la página OEM según el equipo
        return r.returncode, raw.decode("utf-8")
    except UnicodeDecodeError:
        return r.returncode, raw.decode("oem", errors="replace")


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


def current_wifi():
    """(red, contraseña, seguridad) de la Wi‑Fi a la que está conectado el equipo, o None.
    Windows solo da la contraseña de redes cuyo perfil está guardado en este equipo."""
    _, out = _netsh("show", "interfaces")
    ssid = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                 if re.match(r"^\s*SSID\s*:", l)), None)
    if not ssid:
        return None
    _, profile = _netsh("show", "profile", f"name={ssid}", "key=clear")
    password, security = parse_wifi_profile(profile)
    return ssid, password, security


def find_saved_capture(img, since, timeout=5.0):
    """Busca en la carpeta de capturas el archivo de esta captura: creado desde `since` y con
    exactamente los mismos píxeles (así nunca se confunde con otra imagen). Recortes guarda el
    archivo un momento después de copiarla, por eso se reintenta durante `timeout` segundos."""
    folder = screenshots_folder()
    if not folder or not os.path.isdir(folder):
        return None
    want = hashlib.md5(img.convert("RGB").tobytes()).digest()
    checked = set()
    end = time.time() + timeout
    while time.time() < end:
        try:
            entries = [e for e in os.scandir(folder) if e.is_file()
                       and os.path.splitext(e.name)[1].lower() in (".png", ".jpg", ".jpeg")
                       and max(e.stat().st_mtime, e.stat().st_ctime) >= since - 2]  # ctime = creación en Windows
        except OSError:
            entries = []
        for e in entries:
            key = (e.path, e.stat().st_size)
            if key in checked:
                continue
            checked.add(key)
            try:
                with Image.open(e.path) as f:
                    if f.size == img.size and hashlib.md5(f.convert("RGB").tobytes()).digest() == want:
                        return e.path
            except OSError:
                pass  # aún se está escribiendo
        time.sleep(0.4)
    return None

def open_with_default_app(content, ext):
    """Guarda el contenido en un archivo temporal y lo abre con la app predeterminada."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=ext, prefix="clipqr_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    os.startfile(path)
