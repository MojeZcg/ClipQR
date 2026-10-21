"""ClipQR - vigila el portapapeles y, si aparece una imagen con un QR / código de barras,
lo decodifica y muestra un popup para elegir qué copiar o qué hacer con él.

Nada se ejecuta solo: abrir enlaces, conectar al Wi-Fi, guardar contactos... son botones.

Ejecutar sin consola:  pythonw clipqr.py
Probar una imagen:     python clipqr.py imagen.png
"""
import ctypes
import hashlib
import os
import re
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.parse
from ctypes import wintypes

import zxingcpp
from PIL import Image, ImageDraw, ImageFilter, ImageGrab, ImageOps, ImageTk
import pystray

APP_NAME = "ClipQR"
VERSION = "1.0.0"
POLL_MS = 150  # GetClipboardSequenceNumber es casi gratis: se puede mirar a menudo
MAX_CARDS = 4
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\ClipQR"  # lo crea ClipQR-Setup.exe

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
dwmapi = ctypes.windll.dwmapi
user32.GetClipboardSequenceNumber.restype = wintypes.DWORD
user32.GetParent.restype = wintypes.HWND


# --------------------------------------------------------------------------- tema

THEMES = {
    "dark": dict(bg="#202020", card="#2b2b2b", border="#3d3d3d", fg="#f3f3f3", muted="#a3a3a3",
                 textbg="#1c1c1c", btn="#383838", btn_hover="#454545", ok="#2e7d32"),
    "light": dict(bg="#f3f3f3", card="#ffffff", border="#d6d6d6", fg="#1b1b1b", muted="#5f5f5f",
                  textbg="#f7f7f7", btn="#e8e8e8", btn_hover="#dadada", ok="#2e7d32"),
}

# tipo -> (glifo Segoe Fluent Icons, emoji de reserva, color de acento)
KINDS = {
    "link": ("", "🔗", "#4f8cff"),
    "wifi": ("", "📶", "#22a06b"),
    "contact": ("", "👤", "#a66cff"),
    "otp": ("", "🔑", "#e8a317"),
    "email": ("", "✉", "#e5484d"),
    "phone": ("", "📞", "#12a594"),
    "sms": ("", "💬", "#12a594"),
    "geo": ("", "📍", "#f76b15"),
    "event": ("", "📅", "#e54666"),
    "text": ("", "📄", "#8b8d98"),
    "product": ("", "🛒", "#0ea5e9"),
}


def windows_theme():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
    except OSError:
        return "dark"


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


# --------------------------------------------------------------------------- decode

def decode_image(img: Image.Image, qr_only=False):
    """Devuelve lista de dicts {format, text, box} sin duplicados (box en coords de `img`)."""
    if img.mode in ("RGBA", "LA", "P"):  # transparencia -> fondo blanco
        bg = Image.new("RGB", img.size, "white")
        bg.paste(img, mask=img.convert("RGBA").split()[-1])
        img = bg
    gray = ImageOps.grayscale(img)
    margin = max(20, min(img.size) // 10)
    pad = lambda im: ImageOps.expand(im, border=margin, fill=255)  # zona de silencio

    # (imagen, factor, desplazamiento): punto_original = (p - desplazamiento) * factor
    attempts = [(gray, 1, 0), (pad(ImageOps.autocontrast(gray, cutoff=2)), 1, margin)]
    if max(img.size) < 1200:  # QRs pequeños en capturas: ampliar ayuda
        attempts.append((gray.resize((img.width * 2, img.height * 2), Image.NEAREST), 0.5, 0))
    if min(img.size) > 300:  # fotos borrosas: reducir y suavizar ayuda
        attempts.append((pad(gray.resize((img.width // 2, img.height // 2), Image.LANCZOS)), 2, margin))
        attempts.append((pad(gray.filter(ImageFilter.MedianFilter(5))), 1, margin))
    attempts.append((ImageOps.invert(gray), 1, 0))  # QR claro sobre fondo oscuro

    # LocalAverage (por defecto) falla con fotos de QR impresos / poco contraste;
    # GlobalHistogram suele resolverlas.
    binarizers = (zxingcpp.Binarizer.LocalAverage, zxingcpp.Binarizer.GlobalHistogram)
    F = zxingcpp.BarcodeFormat
    formats = (F.QRCode, F.MicroQRCode, F.RMQRCode) if qr_only else ()

    seen, out = set(), []
    for candidate, factor, offset in attempts:
        for binarizer in binarizers:
            try:
                results = zxingcpp.read_barcodes(candidate, binarizer=binarizer, formats=formats)
            except Exception:
                continue
            for r in results:
                if r.valid and r.text and r.text not in seen:
                    seen.add(r.text)
                    box = None
                    try:
                        p = r.position
                        pts = [p.top_left, p.top_right, p.bottom_left, p.bottom_right]
                        xs = [(q.x - offset) * factor for q in pts]
                        ys = [(q.y - offset) * factor for q in pts]
                        box = (min(xs), min(ys), max(xs), max(ys))
                    except Exception:
                        pass
                    out.append({"format": r.format.name if hasattr(r.format, "name") else str(r.format),
                                "text": r.text, "box": box})
            if out:
                return out
    return out


def make_thumb(img, box, size=128):
    img = img.convert("RGB")
    if box:
        x0, y0, x1, y1 = box
        m = max(x1 - x0, y1 - y0) * 0.12
        x0, y0 = max(0, int(x0 - m)), max(0, int(y0 - m))
        x1, y1 = min(img.width, int(x1 + m)), min(img.height, int(y1 + m))
        if x1 - x0 > 4 and y1 - y0 > 4:
            img = img.crop((x0, y0, x1, y1))
    img.thumbnail((size, size), Image.LANCZOS)
    return img


def grab_clipboard_images(include_files=True):
    try:
        data = ImageGrab.grabclipboard()
    except Exception:
        return []
    if isinstance(data, Image.Image):
        return [data]
    if isinstance(data, list) and include_files:  # archivos copiados desde el Explorador
        imgs = []
        for path in data[:10]:
            if os.path.splitext(path)[1].lower() in IMAGE_EXTS:
                try:
                    imgs.append(Image.open(path))
                except Exception:
                    pass
        return imgs
    return []


# --------------------------------------------------------------------------- parse

def _unescape(s):
    return re.sub(r"\\([\\;,:\"])", r"\1", s)


def _split_fields(body):
    """Separa 'K:V;K:V;' respetando escapes con backslash."""
    parts = re.split(r"(?<!\\);", body)
    fields = []
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            fields.append((k.upper(), _unescape(v)))
    return fields


FORMAT_NAMES = {"QRCode": "Código QR", "MicroQRCode": "Micro QR", "RMQRCode": "rMQR", "DataMatrix": "DataMatrix",
                "Aztec": "Aztec", "PDF417": "PDF417", "EAN13": "EAN-13", "EAN8": "EAN-8", "UPCA": "UPC-A",
                "UPCE": "UPC-E", "Code128": "Code 128", "Code39": "Code 39", "Code93": "Code 93",
                "ITF": "ITF", "Codabar": "Codabar"}


def headline(kind, items, text):
    """(etiqueta, valor) del dato que se muestra en grande en el aviso."""
    want = {"wifi": ("Red (SSID)",), "contact": ("Nombre", "Empresa", "Teléfono", "Email"),
            "email": ("Email",), "phone": ("Número",), "sms": ("Número",), "geo": ("Coordenadas",),
            "event": ("Evento",), "product": ("Código",), "otp": ("Emisor", "Cuenta"), "link": ("Dominio",)}
    for label in want.get(kind, ()):
        for l, v in items:
            if l == label and v:
                return l, v
    first = text.strip().splitlines()[0] if text.strip() else text
    return None, first


def shorten(s, n, middle=False):
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    if middle:
        k = (n - 1) // 2
        return s[:k] + "…" + s[-k:]
    return s[:n - 1] + "…"


def format_name(fmt):
    return FORMAT_NAMES.get(fmt, fmt)


def _vcard_from(items):
    """vCard mínima a partir de [(etiqueta, valor)] (para MeCard)."""
    keys = {"Nombre": "FN", "Teléfono": "TEL", "Email": "EMAIL", "Web": "URL",
            "Dirección": "ADR", "Nota": "NOTE", "Empresa": "ORG"}
    lines = ["BEGIN:VCARD", "VERSION:3.0"] + [f"{keys[l]}:{v}" for l, v in items if l in keys]
    return "\r\n".join(lines + ["END:VCARD"]) + "\r\n"


def _contact_actions(items, card_text):
    actions = [("Guardar contacto", "file", (card_text, ".vcf"))]
    first = lambda label: next((v for l, v in items if l == label), None)
    if first("Teléfono"):
        actions.append(("Llamar", "open", "tel:" + re.sub(r"[^\d+]", "", first("Teléfono"))))
    if first("Email"):
        actions.append(("Escribir email", "open", "mailto:" + first("Email")))
    if first("Web"):
        web = first("Web")
        actions.append(("Abrir web ↗", "open", web if "://" in web else "https://" + web))
    return actions


def parse_payload(text):
    """Devuelve (tipo, titulo, [(etiqueta, valor)], [(texto_boton, accion, arg)]).

    Las acciones son siempre botones: nada se ejecuta sin que el usuario lo pulse.
    accion: "open" (abrir URI), "wifi" (conectar), "file" (guardar y abrir (contenido, extensión)).
    """
    t = text.strip()
    low = t.lower()

    if low.startswith("wifi:"):
        f = dict(_split_fields(t[5:]))
        items = [(l, f[k]) for k, l in (("S", "Red (SSID)"), ("P", "Contraseña"), ("T", "Seguridad")) if f.get(k)]
        wifi = {"ssid": f.get("S", ""), "password": f.get("P", ""), "auth": f.get("T", ""),
                "hidden": f.get("H", "").lower() == "true"}
        return "wifi", "Wi-Fi", items, [("Conectar a la red", "wifi", wifi)] if wifi["ssid"] else []

    if low.startswith("begin:vcard"):
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.split(";")[0].upper()
            val = val.replace("\\,", ",").replace("\\;", ";").strip()
            label = {"FN": "Nombre", "TEL": "Teléfono", "EMAIL": "Email", "ORG": "Empresa",
                     "TITLE": "Cargo", "URL": "Web", "ADR": "Dirección", "NOTE": "Nota"}.get(key)
            if label and val:
                if key == "ADR":
                    val = ", ".join(p for p in val.split(";") if p)
                items.append((label, val))
        return "contact", "Contacto", items, _contact_actions(items, t)

    if low.startswith("mecard:"):
        labels = {"N": "Nombre", "TEL": "Teléfono", "EMAIL": "Email", "URL": "Web",
                  "ADR": "Dirección", "NOTE": "Nota", "ORG": "Empresa"}
        items = [(labels[k], " ".join(reversed(v.split(","))) if k == "N" else v)
                 for k, v in _split_fields(t[7:]) if k in labels and v]
        return "contact", "Contacto", items, _contact_actions(items, _vcard_from(items))

    if "begin:vevent" in low:
        labels = {"SUMMARY": "Evento", "DTSTART": "Inicio", "DTEND": "Fin",
                  "LOCATION": "Lugar", "DESCRIPTION": "Descripción"}
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.split(";")[0].upper()
                if key in labels and val.strip():
                    items.append((labels[key], val.strip()))
        ics = t if low.startswith("begin:vcalendar") else f"BEGIN:VCALENDAR\r\nVERSION:2.0\r\n{t}\r\nEND:VCALENDAR\r\n"
        return "event", "Evento", items, [("Añadir al calendario", "file", (ics, ".ics"))]

    if low.startswith("otpauth://"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [("Cuenta", urllib.parse.unquote(u.path.lstrip("/")))]
        if q.get("secret"):
            items.append(("Secreto", q["secret"]))
        if q.get("issuer"):
            items.append(("Emisor", q["issuer"]))
        return "otp", "2FA (OTP)", items, []

    if low.startswith("mailto:"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [("Email", urllib.parse.unquote(u.path))]
        if q.get("subject"):
            items.append(("Asunto", q["subject"]))
        if q.get("body"):
            items.append(("Mensaje", q["body"]))
        return "email", "Email", items, [("Escribir email", "open", t)]

    if low.startswith("matmsg:"):
        f = dict(_split_fields(t[7:]))
        items = [(l, f[k]) for k, l in (("TO", "Email"), ("SUB", "Asunto"), ("BODY", "Mensaje")) if f.get(k)]
        q = urllib.parse.urlencode({k: v for k, v in (("subject", f.get("SUB")), ("body", f.get("BODY"))) if v},
                                   quote_via=urllib.parse.quote)
        mailto = f"mailto:{f.get('TO', '')}" + (f"?{q}" if q else "")
        return "email", "Email", items, [("Escribir email", "open", mailto)]

    if low.startswith("tel:"):
        return "phone", "Teléfono", [("Número", t[4:])], [("Llamar", "open", t)]

    if low.startswith(("smsto:", "sms:")):
        parts = t.split(":", 2)
        items = [("Número", parts[1])] if len(parts) > 1 else []
        if len(parts) > 2 and parts[2]:
            items.append(("Mensaje", parts[2]))
        actions = []
        if len(parts) > 1 and parts[1]:
            body = f"?body={urllib.parse.quote(parts[2])}" if len(parts) > 2 and parts[2] else ""
            actions.append(("Enviar SMS", "open", f"sms:{parts[1]}{body}"))
        return "sms", "SMS", items, actions

    if low.startswith("geo:"):
        lat_lon = t[4:].split("?")[0].split(",")[:2]
        actions = []
        if len(lat_lon) == 2:
            actions.append(("Ver en el mapa ↗", "open", f"https://www.google.com/maps?q={','.join(lat_lon)}"))
        return "geo", "Ubicación", [("Coordenadas", ",".join(lat_lon))], actions

    if re.match(r"^https?://", t, re.I):
        u = urllib.parse.urlparse(t)
        return "link", "Enlace", [("Dominio", u.netloc)], [("Abrir enlace ↗", "open", t)]

    if re.match(r"^(\d{8}|\d{12,14})$", t):  # EAN / UPC / GTIN de un producto
        return "product", "Producto", [("Código", t)], [
            ("Buscar producto ↗", "open", "https://www.google.com/search?q=" + t)]

    if re.match(r"^www\.\S+$", t, re.I):
        return "link", "Enlace", [], [("Abrir enlace ↗", "open", "https://" + t)]

    # texto libre: extraer emails / urls sueltos
    items, actions = [], []
    for m in re.findall(r"https?://\S+", t):
        items.append(("URL", m))
        if not actions:
            actions.append(("Abrir enlace ↗", "open", m))
    for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", t):
        items.append(("Email", m))
    if not actions and len(t) <= 200:
        actions.append(("Buscar en Google ↗", "open", "https://www.google.com/search?q=" + urllib.parse.quote(t)))
    return "text", "Texto", items, actions


# --------------------------------------------------------------------------- acciones

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


def open_with_default_app(content, ext):
    """Guarda el contenido en un archivo temporal y lo abre con la app predeterminada."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=ext, prefix="clipqr_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    os.startfile(path)


# --------------------------------------------------------------------------- app

_LOGOS = {}


def _resource(*parts):
    """Ruta a un archivo del proyecto, también dentro del .exe de PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def make_icon(paused=False, size=64, dark_bg=False, outline=False):
    """Logo de ClipQR (assets/logo*.png, generados con tools/make_logo.py) al tamaño pedido.

    Es transparente: trazos negros para fondos claros, blancos si dark_bg. Con outline, trazos
    negros con un fino contorno blanco, para iconos que se ven sobre cualquier fondo (.ico).
    En pausa se muestra gris y atenuado."""
    name = "logo-white.png" if dark_bg else "logo.png"
    if name not in _LOGOS:
        _LOGOS[name] = Image.open(_resource("assets", name)).convert("RGBA")
    img = _LOGOS[name].resize((size, size), Image.LANCZOS)
    if outline:
        a = img.getchannel("A")
        halo = a.filter(ImageFilter.MaxFilter(3 if size <= 48 else 5))
        img = Image.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", img.size, "white").split(), halo)), img)
    if paused:
        r, g, b, a = img.split()
        gray = ImageOps.grayscale(img.convert("RGB")).point(lambda v: 110 + v * 145 // 255)
        img = Image.merge("RGBA", (gray, gray, gray, a.point(lambda v: v * 3 // 4)))
    return img


def taskbar_is_dark():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            return not winreg.QueryValueEx(k, "SystemUsesLightTheme")[0]
    except OSError:
        return True


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


class ClipQR:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title(APP_NAME)
        self.root.report_callback_exception = log_exception
        self.dpi = self.root.winfo_fpixels("1i") / 96
        families = set(tkfont.families(self.root))
        self.icon_font = next((f for f in ("Segoe Fluent Icons", "Segoe MDL2 Assets") if f in families), None)
        self.ui_font = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
        self.paused = False
        self.settings = load_settings()
        self.c = THEMES[self.theme_name()]
        self.last_seq = user32.GetClipboardSequenceNumber()
        self.last_hash = None
        self.clip_time = time.time()
        self.history = []  # lista de escaneos; cada uno es una lista de dicts {format, text, thumb, time}
        self.popup = None
        self.popup_job = None
        self.history_win = None
        self.settings_win = None
        self._photos = []  # referencias a PhotoImage para que Tk no las libere
        self.tray = self._build_tray()
        self.tray.run_detached()
        self.root.after(POLL_MS, self._poll)
        self.root.after(300, self._warm_up)
        self.root.after(500, self.first_run)

    def px(self, n):
        return int(n * self.dpi)

    def font(self, size, weight="normal"):
        return (self.ui_font, size, weight)

    def glyph(self, kind_or_char):
        """(texto, fuente) para un icono: glifo de Segoe Fluent Icons o emoji de reserva."""
        if kind_or_char in KINDS:
            g, emoji, _ = KINDS[kind_or_char]
            return (g, (self.icon_font, 12)) if self.icon_font else (emoji, self.font(11))
        return kind_or_char, (self.icon_font or self.ui_font, 10)

    # ---- tray
    def _icon_image(self, paused=False):
        return make_icon(paused, dark_bg=taskbar_is_dark())

    def _build_tray(self):
        def ui(fn):
            return lambda icon, item: self.root.after(0, fn)

        def last_label(item):
            if not self.history:
                return "Último: (nada todavía)"
            text = self.history[0][0]["text"].replace("\n", " ")
            return "Último: " + ((text[:40] + "…") if len(text) > 40 else text)

        menu = pystray.Menu(
            pystray.MenuItem(last_label, ui(lambda: self.history and self.show_popup(self.history[0])),
                             enabled=lambda item: bool(self.history)),
            pystray.MenuItem("Abrir historial", ui(self.show_history), default=True),
            pystray.MenuItem("Escanear portapapeles ahora", ui(lambda: self.scan(force=True))),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Configuración…", ui(self.show_settings)),
            pystray.MenuItem("Pausar", ui(self.toggle_pause), checked=lambda item: self.paused),
            pystray.MenuItem("Iniciar con Windows", ui(self.toggle_autostart), checked=lambda item: self.autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", ui(self.quit)),
        )
        return pystray.Icon(APP_NAME, self._icon_image(), f"{APP_NAME} - vigilando portapapeles", menu)

    def save_settings(self):
        import json
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except OSError:
            pass

    def set_setting(self, **kw):
        self.settings.update(kw)
        self.save_settings()
        self.tray.update_menu()

    def theme_name(self):
        t = self.settings["theme"]
        return t if t in THEMES else windows_theme()

    def toggle_pause(self):
        self.paused = not self.paused
        self.tray.icon = self._icon_image(self.paused)
        self.tray.title = f"{APP_NAME} - {'en pausa' if self.paused else 'vigilando portapapeles'}"
        self.tray.update_menu()

    def _autostart_cmd(self):
        if FROZEN:
            return f'"{sys.executable}"'
        exe = sys.executable
        pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
        if os.path.exists(pyw):
            exe = pyw
        return f'"{exe}" "{os.path.abspath(__file__)}"'

    def _autostart_value(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
                return winreg.QueryValueEx(k, APP_NAME)[0]
        except OSError:
            return None

    def autostart_enabled(self):
        if PACKAGED:
            return msix_startup_state() in ("enabled", "enabled_by_policy")
        return self._autostart_value() is not None

    def _set_autostart(self):
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, self._autostart_cmd())

    def first_run(self):
        """Primer arranque: activar inicio con Windows y avisar de que está en la bandeja.
        Si el programa se movió de carpeta, corrige la ruta de autoarranque."""
        if not os.path.exists(FIRST_RUN_MARK):
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(FIRST_RUN_MARK, "w") as f:
                f.write("1")
            if PACKAGED:  # en la Store el inicio con Windows lo activa el usuario
                self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                           "Haz una captura de un QR y aparecerá aquí.\n"
                           "Puedes hacer que se inicie con Windows en Configuración (⚙).", seconds=10)
                return
            if installed_by_setup():  # el asistente ya preguntó por el inicio con Windows
                self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                           "Haz una captura de un QR y aparecerá aquí.", seconds=8)
                return
            self._set_autostart()
            self.tray.update_menu()
            self.toast("ClipQR está activo en la bandeja (junto al reloj).\n"
                       "Haz una captura de un QR y aparecerá aquí.\n"
                       "Se iniciará solo con Windows.", seconds=8)
        elif not PACKAGED and self.autostart_enabled() and self._autostart_value() != self._autostart_cmd():
            self._set_autostart()

    def toggle_autostart(self):
        if PACKAGED:
            ok, msg = msix_set_startup(not self.autostart_enabled())
            if not ok:
                self.toast(msg, seconds=8)
            self.tray.update_menu()
            return
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if self.autostart_enabled():
                winreg.DeleteValue(k, APP_NAME)
            else:
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, self._autostart_cmd())
        self.tray.update_menu()

    def quit(self):
        self.tray.stop()
        self.root.destroy()

    # ---- clipboard polling
    def _poll(self):
        try:
            seq = user32.GetClipboardSequenceNumber()
            if seq != self.last_seq:
                self.last_seq = seq
                self.clip_time = time.time()
                if not self.paused:
                    self.scan()
                    # reintento: algunas herramientas de captura escriben la imagen con retraso
                    self.root.after(800, lambda s=seq: s == self.last_seq and self.scan())
        finally:
            self.root.after(POLL_MS, self._poll)

    def scan(self, force=False):
        imgs = grab_clipboard_images(self.settings["explorer_files"])
        if not imgs:
            if force:
                self.toast("No hay ninguna imagen en el portapapeles.")
            return
        h = hashlib.md5(b"".join(i.convert("RGB").tobytes()[:2_000_000] for i in imgs)).hexdigest()
        if h == self.last_hash and not force:
            return
        self.last_hash = h

        def work():
            codes, texts = [], set()
            for img in imgs:
                for c in decode_image(img, self.settings["qr_only"]):
                    if c["text"] not in texts:
                        texts.add(c["text"])
                        codes.append({"format": c["format"], "text": c["text"],
                                      "thumb": make_thumb(img, c["box"]), "time": time.time()})
            self.root.after(0, lambda: self._on_result(codes, force))
            # captura de pantalla (no un archivo copiado): buscar el archivo que guarda Windows
            if codes and len(imgs) == 1 and not getattr(imgs[0], "filename", None):
                path = find_saved_capture(imgs[0], since)
                if path:
                    self.root.after(0, lambda: self._on_capture(codes, path))

        since = self.clip_time
        threading.Thread(target=work, daemon=True).start()

    def _on_capture(self, codes, path):
        for c in codes:
            c["capture"] = path
        if self.settings["delete_capture"]:
            deleted = send_to_recycle_bin(path)
            for c in codes:
                c["capture_deleted"] = deleted
        self._paint_capture_slot(codes)

    def _paint_capture_slot(self, codes):
        """Línea del aviso sobre el archivo de la captura: ya borrado, o botón para borrarlo."""
        win = self.popup
        if win is None or not win.winfo_exists() or getattr(win, "_codes", None) is not codes:
            return
        path = codes[0].get("capture")
        slot = win._capture_slot
        for w in slot.winfo_children():
            w.destroy()
        if not path:
            return
        c = self.c
        g = "\ue74d" if self.icon_font else "🗑"
        gf = (self.icon_font, 9) if self.icon_font else self.font(9)
        tk.Label(slot, text=g, font=gf, bg=c["bg"], fg=c["muted"]).pack(side="left", padx=(0, self.px(6)))
        msg = tk.Label(slot, bg=c["bg"], fg=c["muted"], font=self.font(9), anchor="w")
        msg.pack(side="left", fill="x", expand=True)
        if codes[0].get("capture_deleted"):
            msg.config(text="Captura enviada a la Papelera")
        elif os.path.exists(path):
            msg.config(text=f"Captura guardada: {shorten(os.path.basename(path), 34, middle=True)}")
            b = self._button(slot, "Borrar captura")

            def delete():
                ok = send_to_recycle_bin(path)
                for code in codes:
                    code["capture_deleted"] = ok
                if ok:
                    self._paint_capture_slot(codes)
                else:
                    self._flash(b, "No se pudo borrar", ok=False)

            b.config(command=delete)
            b.pack(side="right")
        else:
            msg.config(text="La captura ya no está en la carpeta")
        slot.pack(fill="x", padx=self.px(14), pady=(0, self.px(8)), before=win._hint)
        self._refit_popup()

    def _on_result(self, codes, force):
        if not codes:
            if force:
                self.toast("No se encontró ningún QR en la imagen.")
            return
        self.history.insert(0, codes)
        del self.history[self.settings["history_max"]:]
        if self.settings["sound"]:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        self.tray.update_menu()
        self.show_popup(codes)
        if self.history_win is not None and self.history_win.winfo_exists():
            self._fill_history()

    # ---- acciones
    def copy(self, text, btn=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.last_seq = user32.GetClipboardSequenceNumber()  # no re-escanear lo que copiamos
        if btn is not None:
            self._flash(btn, "✓ Copiado")

    def _flash(self, btn, text, ok=True):
        if not btn.winfo_exists():
            return
        old_text, old_bg = btn.cget("text"), btn._base_bg
        btn._base_bg = self.c["ok"] if ok else "#c62828"
        btn.config(text=text, bg=btn._base_bg, fg="white")
        def restore():
            if btn.winfo_exists():
                btn._base_bg = old_bg
                btn.config(text=old_text, bg=old_bg, fg=btn._base_fg)
        btn.after(1300, restore)

    def run_action(self, kind, arg, btn):
        """Solo se llama al pulsar un botón."""
        try:
            if kind == "open":
                os.startfile(arg)
                self._close_popup()
            elif kind == "file":
                open_with_default_app(*arg)
                self._close_popup()
            elif kind == "wifi":
                btn.config(text="Conectando…", state="disabled")

                def work():
                    ok, msg = connect_wifi(arg["ssid"], arg["password"], arg["auth"], arg["hidden"])
                    self.root.after(0, lambda: self.toast(("✓ " if ok else "✕ ") + msg, seconds=6))

                threading.Thread(target=work, daemon=True).start()
        except OSError as e:
            self.toast(f"No hay ninguna aplicación para abrir esto.\n{e.strerror or e}", seconds=6)

    # ---- widgets
    def _button(self, parent, text, cmd=None, color=None, bg=None):
        """Botón plano con efecto hover. `color` = botón principal con ese acento."""
        c = self.c
        base = color or c["btn"]
        fg = "white" if color else c["fg"]
        hover = _shade(color, 0.85) if color else c["btn_hover"]
        b = tk.Button(parent, text=text, command=cmd, bg=base, fg=fg, activebackground=hover,
                      activeforeground=fg, relief="flat", bd=0, padx=self.px(10), pady=self.px(4),
                      font=self.font(9, "bold" if color else "normal"), cursor="hand2", highlightthickness=0)
        b._base_bg, b._base_fg = base, fg
        b.bind("<Enter>", lambda e: b.cget("state") != "disabled" and b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=b._base_bg))
        return b

    def _row(self, parent, label, value):
        c = self.c
        row = tk.Frame(parent, bg=c["card"])
        row.pack(fill="x", pady=1)
        tk.Label(row, text=label, bg=c["card"], fg=c["muted"], font=self.font(8), width=11,
                 anchor="w").pack(side="left")
        shown = value if len(value) <= 60 else value[:60] + "…"
        if label.lower().startswith("contraseña") or label == "Secreto":
            hidden = "•" * min(len(value), 14)
            var = tk.StringVar(value=hidden)
            lbl = tk.Label(row, textvariable=var, bg=c["card"], fg=c["fg"], font=("Consolas", 10),
                           anchor="w", cursor="hand2")
            toggle = self._button(row, self.glyph("")[0] if self.icon_font else "👁")
            toggle.config(font=self.glyph("")[1], padx=self.px(6),
                          command=lambda: var.set(shown if var.get() == hidden else hidden))
        else:
            lbl = tk.Label(row, text=shown, bg=c["card"], fg=c["fg"], font=self.font(10), anchor="w",
                           justify="left", wraplength=self.px(230))
            toggle = None
        lbl.pack(side="left", fill="x", expand=True)
        b = self._button(row, "Copiar")
        b.config(command=lambda: self.copy(value, b))
        b.pack(side="right")
        if toggle:
            toggle.pack(side="right", padx=(0, self.px(4)))

    def _photo(self, pil_img, size):
        img = pil_img.copy()
        img.thumbnail((size, size), Image.LANCZOS)
        p = ImageTk.PhotoImage(img)
        self._photos.append(p)
        del self._photos[:-200]
        return p

    def _card(self, parent, code):
        """Tarjeta de un código, pensada para leerse de un vistazo: el dato principal en grande,
        la acción principal justo debajo, el resto de datos compactos y el texto crudo plegado."""
        c = self.c
        kind, title, items, actions = parse_payload(code["text"])
        accent = KINDS[kind][2]
        text = code["text"]
        head_label, head_value = headline(kind, items, text)
        rows = [(l, v) for l, v in items if (l, v) != (head_label, head_value)]

        card = tk.Frame(parent, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
        card.pack(fill="x", padx=self.px(12), pady=(0, self.px(8)))
        inner = tk.Frame(card, bg=c["card"])
        inner.pack(fill="both", padx=self.px(12), pady=self.px(10))

        # tipo (pequeño, en color) + dato principal (grande)
        top = tk.Frame(inner, bg=c["card"])
        top.pack(fill="x")
        if code.get("thumb") is not None:
            tk.Label(top, image=self._photo(code["thumb"], self.px(46)), bg=c["card"], bd=0).pack(
                side="left", anchor="n", padx=(0, self.px(12)))
        b_head = self._button(top, "Copiar")
        b_head.config(command=lambda: self.copy(head_value, b_head))
        b_head.pack(side="right", anchor="n")
        head = tk.Frame(top, bg=c["card"])
        head.pack(side="left", fill="x", expand=True)
        meta = tk.Frame(head, bg=c["card"])
        meta.pack(anchor="w")
        g, gf = self.glyph(kind)
        tk.Label(meta, text=g, font=(gf[0], 10), bg=c["card"], fg=accent).pack(side="left", padx=(0, self.px(5)))
        tk.Label(meta, text=title.upper(), bg=c["card"], fg=accent, font=self.font(8, "bold")).pack(side="left")
        tk.Label(meta, text=f"  ·  {format_name(code['format'])}", bg=c["card"], fg=c["muted"],
                 font=self.font(8)).pack(side="left")
        tk.Label(head, text=shorten(head_value, 70), bg=c["card"], fg=c["fg"], font=self.font(15, "bold"),
                 anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")
        if kind == "link":  # el dominio no basta: la URL completa, en pequeño
            tk.Label(head, text=shorten(text, 90, middle=True), bg=c["card"], fg=c["muted"], font=self.font(9),
                     anchor="w", justify="left", wraplength=self.px(300)).pack(anchor="w", fill="x")

        # acción principal en grande, las demás al lado
        if actions:
            bar = tk.Frame(inner, bg=c["card"])
            bar.pack(fill="x", pady=(self.px(10), 0))
            for i, (label, kind_a, arg) in enumerate(actions):
                b = self._button(bar, label, color=accent)
                if i == 0:
                    b.config(font=self.font(10, "bold"), padx=self.px(16), pady=self.px(6))
                b.config(command=lambda k=kind_a, a=arg, b=b: self.run_action(k, a, b))
                b.pack(side="left", padx=(0, self.px(6)), pady=(0, self.px(2)))

        # resto de datos, compactos
        if rows:
            box = tk.Frame(inner, bg=c["card"])
            box.pack(fill="x", pady=(self.px(10), 0))
            for label, value in rows:
                self._row(box, label, value)

        # texto completo plegado (en «Texto» se ve desde el principio si es largo)
        foot = tk.Frame(inner, bg=c["card"])
        foot.pack(fill="x", pady=(self.px(8), 0))
        raw = tk.Frame(inner, bg=c["card"])
        toggle = tk.Label(foot, bg=c["card"], fg=c["muted"], font=self.font(9), cursor="hand2")
        toggle.pack(side="left")
        b_all = self._button(foot, "Copiar todo")
        b_all.config(command=lambda: self.copy(text, b_all))
        b_all.pack(side="right")
        state = {"open": False, "built": False}

        def build_raw():
            lines = min(max(text.count("\n") + 1, len(text) // 50 + 1), 6)
            txt = tk.Text(raw, height=lines, width=50, wrap="word", bg=c["textbg"], fg=c["fg"], relief="flat",
                          font=("Consolas", 9), padx=self.px(6), pady=self.px(4), selectbackground=accent,
                          selectforeground="white", highlightthickness=0, bd=0, cursor="xterm")
            txt.insert("1.0", text)
            txt.config(state="disabled")
            txt.pack(fill="x", pady=(self.px(6), self.px(4)))
            b_sel = self._button(raw, "Copiar selección")

            def copy_sel():
                try:
                    self.copy(txt.get("sel.first", "sel.last"), b_sel)
                except tk.TclError:
                    self._flash(b_sel, "Selecciona texto arriba", ok=False)

            b_sel.config(command=copy_sel)
            b_sel.pack(anchor="e")

        def flip(e=None):
            state["open"] = not state["open"]
            if state["open"]:
                if not state["built"]:
                    build_raw()
                    state["built"] = True
                raw.pack(fill="x", after=foot)
            else:
                raw.pack_forget()
            toggle.config(text=("▾ Ocultar texto completo" if state["open"] else "▸ Ver texto completo"))
            if e is not None and self.popup is not None:
                self._refit_popup()

        toggle.config(text="▸ Ver texto completo")
        toggle.bind("<Button-1>", flip)
        toggle.bind("<Enter>", lambda e: toggle.config(fg=c["fg"]))
        toggle.bind("<Leave>", lambda e: toggle.config(fg=c["muted"]))
        if kind == "text" and (len(text) > 70 or "\n" in text):
            flip()

    def _warm_up(self):
        """Muestra un aviso de ejemplo fuera de la pantalla y transparente para que Tk cargue fuentes y
        recursos al arrancar; si no, el primer aviso real tarda casi un segundo en aparecer."""
        win = tk.Toplevel(self.root, bg=self.c["bg"])
        win.overrideredirect(True)
        win.attributes("-alpha", 0.0)
        win.attributes("-topmost", True)
        win.geometry("+-4000+-4000")
        sample = {"format": "QRCode", "text": "WIFI:T:WPA;S:ClipQR;P:clipqr;;\nhttps://example.com",
                  "thumb": make_icon(size=64).convert("RGB")}
        self._card(win, sample)
        tk.Label(win, image=self._logo(18)).pack()
        tk.Canvas(win, height=3).pack()
        tk.Entry(win, font=self.font(10)).pack()
        style_window(win, border=self.c["border"])
        win.update()
        win.destroy()

    def _refit_popup(self):
        """Reajusta el alto del aviso al desplegar/plegar contenido, sin moverlo de sitio."""
        win = self.popup
        if win is None or not win.winfo_exists():
            return
        win.update_idletasks()
        rect = self._work_area()
        h = min(win.winfo_reqheight(), rect.bottom - rect.top - self.px(24))
        x, y = win.winfo_x(), win.winfo_y()
        if y + h > rect.bottom:
            y = max(rect.top, rect.bottom - h - self.px(16))
        win.geometry(f"{win.winfo_width()}x{h}+{x}+{y}")
        if getattr(win, "_countdown", None) is not None:
            win._countdown.coords("fill", 0, 0, win.winfo_width(), self.px(3))

    # ---- popup
    def _close_popup(self):
        win, job = self.popup, self.popup_job
        self.popup, self.popup_job = None, None
        if win is not None and win.winfo_exists():
            if job:
                win.after_cancel(job)  # cancelar con el mismo widget que lo programó
            win.destroy()

    def _work_area(self):
        rect = wintypes.RECT()
        user32.SystemParametersInfoW(0x30, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA
        return rect

    def _new_popup(self):
        self._close_popup()
        self.c = THEMES[self.theme_name()]  # sigue el tema elegido / de Windows
        win = tk.Toplevel(self.root, bg=self.c["bg"])
        self.popup = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.0)
        return win

    def _popup_xy(self, w, h):
        """Posición según ajustes. Por defecto arriba a la derecha: abajo es donde salen
        las notificaciones de Windows (p. ej. la de Recortes) y lo taparían."""
        rect, m = self._work_area(), self.px(16)
        pos = self.settings["position"]
        if pos == "custom" and self.settings.get("x") is not None:
            x = min(max(self.settings["x"], rect.left), rect.right - w)
            y = min(max(self.settings["y"], rect.top), rect.bottom - h)
            return x, y, 0
        if pos == "bottom-right":
            return rect.right - w - m, rect.bottom - h - m, self.px(36)
        if pos == "center":
            return (rect.left + rect.right - w) // 2, (rect.top + rect.bottom - h) // 2, self.px(24)
        return rect.right - w - m, rect.top + m, -self.px(36)  # top-right

    def _show_animated(self, win, seconds, can_stay_open=False):
        """Coloca el popup, entra deslizando + fundido, y cuenta atrás con barra."""
        win.update_idletasks()
        rect = self._work_area()
        w = win.winfo_reqwidth()
        h = min(win.winfo_reqheight(), rect.bottom - rect.top - self.px(24))
        x, y, dy = self._popup_xy(w, h)
        style_window(win, border=self.c["border"])
        steps = 8 if self.settings["animation"] else 0
        win._pinned = can_stay_open and not self.settings["autoclose"]

        def frame(i=0):
            if not win.winfo_exists():
                return
            t = 1 - (1 - i / steps) ** 3 if steps else 1  # ease-out
            win.geometry(f"{w}x{h}+{x}+{int(y + dy * (1 - t))}")
            win.attributes("-alpha", 0.98 * t)
            if i < steps:
                win.after(15, frame, i + 1)

        frame()

        bar = getattr(win, "_countdown", None)
        total = seconds * 1000
        state = {"left": total}

        def tick():
            if not win.winfo_exists():
                return
            px_, py_ = win.winfo_pointerxy()
            inside = win.winfo_rootx() <= px_ < win.winfo_rootx() + w and win.winfo_rooty() <= py_ < win.winfo_rooty() + h
            if win._pinned:  # fijado: no se cierra solo
                state["left"] = total
            elif not (inside and self.settings["pause_on_hover"]):  # se pausa con el ratón encima
                state["left"] -= 50
            if state["left"] <= 0:
                self._close_popup()
                return
            if bar is not None:
                bar.coords("fill", 0, 0, 0 if win._pinned else w * state["left"] / total, self.px(3))
            self.popup_job = win.after(50, tick)

        self.popup_job = win.after(50, tick)

    def show_popup(self, codes):
        win = self._new_popup()
        c = self.c

        head = tk.Frame(win, bg=c["bg"])
        head.pack(fill="x", padx=self.px(12), pady=(self.px(10), self.px(8)))
        tk.Label(head, image=self._logo(18), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(8)))
        n = len(codes)
        tk.Label(head, text=f"{n} código{'s' if n > 1 else ''} detectado{'s' if n > 1 else ''}",
                 bg=c["bg"], fg=c["fg"], font=self.font(11, "bold")).pack(side="left")
        x = tk.Label(head, text="" if self.icon_font else "✕", bg=c["bg"], fg=c["muted"],
                     font=(self.icon_font, 9) if self.icon_font else self.font(11), cursor="hand2",
                     padx=self.px(6), pady=self.px(4))
        x.pack(side="right")
        x.bind("<Button-1>", lambda e: self.root.after(0, self._close_popup))
        x.bind("<Enter>", lambda e: x.config(fg=c["fg"]))
        x.bind("<Leave>", lambda e: x.config(fg=c["muted"]))
        hist = tk.Label(head, text="" if self.icon_font else "Historial", bg=c["bg"], fg=c["muted"],
                        font=(self.icon_font, 10) if self.icon_font else self.font(8), cursor="hand2",
                        padx=self.px(6), pady=self.px(4))
        hist.pack(side="right", padx=(0, self.px(4)))
        hist.bind("<Button-1>", lambda e: self.root.after(0, lambda: (self._close_popup(), self.show_history())))
        hist.bind("<Enter>", lambda e: hist.config(fg=c["fg"]))
        hist.bind("<Leave>", lambda e: hist.config(fg=c["muted"]))
        gear = tk.Label(head, text="\ue713" if self.icon_font else "⚙", bg=c["bg"], fg=c["muted"],
                        font=(self.icon_font, 10) if self.icon_font else self.font(9), cursor="hand2",
                        padx=self.px(6), pady=self.px(4))
        gear.pack(side="right", padx=(0, self.px(2)))
        gear.bind("<Button-1>", lambda e: self.root.after(0, self.show_settings))
        gear.bind("<Enter>", lambda e: gear.config(fg=c["fg"]))
        gear.bind("<Leave>", lambda e: gear.config(fg=c["muted"]))
        accent = KINDS[parse_payload(codes[0]["text"])[0]][2]
        pin = tk.Label(head, text="" if self.icon_font else "📌", bg=c["bg"], fg=c["muted"],
                       font=(self.icon_font, 10) if self.icon_font else self.font(9), cursor="hand2",
                       padx=self.px(6), pady=self.px(4))
        pin.pack(side="right", padx=(0, self.px(2)))

        def paint_pin():
            pinned = getattr(win, "_pinned", False)
            pin.config(text=("" if pinned else "") if self.icon_font else "📌",
                       fg=accent if pinned else c["muted"])

        def toggle_pin(e):
            win._pinned = not getattr(win, "_pinned", False)
            paint_pin()

        pin.bind("<Button-1>", toggle_pin)
        win.after(10, paint_pin)

        # arrastrar desde la cabecera; la posición se recuerda
        drag = {}

        def press(e):
            drag.update(x=e.x_root - win.winfo_x(), y=e.y_root - win.winfo_y(), moved=False)

        def motion(e):
            if drag:
                drag["moved"] = True
                win.geometry(f"+{e.x_root - drag['x']}+{e.y_root - drag['y']}")

        def release(e):
            if drag.get("moved"):
                self.settings.update(position="custom", x=win.winfo_x(), y=win.winfo_y())
                self.save_settings()
                self.tray.update_menu()
            drag.clear()

        for wdg in (head, *[w for w in head.winfo_children() if w not in (x, hist, pin, gear)]):
            wdg.config(cursor="fleur")
            wdg.bind("<ButtonPress-1>", press)
            wdg.bind("<B1-Motion>", motion)
            wdg.bind("<ButtonRelease-1>", release)

        win._codes = codes
        for code in codes[:MAX_CARDS]:
            self._card(win, code)
        win._capture_slot = tk.Frame(win, bg=c["bg"])
        if n > MAX_CARDS:
            tk.Label(win, text=f"+{n - MAX_CARDS} más en el historial", bg=c["bg"], fg=c["muted"],
                     font=self.font(8)).pack()

        win._hint = tk.Label(win, text="Arrástralo desde arriba · 📌 para fijarlo · Esc para cerrar", bg=c["bg"],
                             fg=c["muted"], font=self.font(8))
        win._hint.pack(pady=(0, self.px(6)))
        cd = tk.Canvas(win, height=self.px(3), bg=c["bg"], highlightthickness=0, bd=0)
        cd.pack(fill="x", side="bottom")
        cd.create_rectangle(0, 0, 9999, self.px(3), fill=accent, width=0, tags="fill")
        win._countdown = cd

        win.bind("<Escape>", lambda e: self._close_popup())
        self._show_animated(win, self.settings["seconds"], can_stay_open=True)
        self._paint_capture_slot(codes)  # al reabrir desde el historial

    def toast(self, msg, seconds=3):
        win = self._new_popup()
        c = self.c
        tk.Label(win, text=msg, bg=c["bg"], fg=c["fg"], font=self.font(10), padx=self.px(16),
                 pady=self.px(12), justify="left").pack()
        cd = tk.Canvas(win, height=self.px(3), bg=c["bg"], highlightthickness=0, bd=0)
        cd.pack(fill="x", side="bottom")
        cd.create_rectangle(0, 0, 9999, self.px(3), fill=KINDS["link"][2], width=0, tags="fill")
        win._countdown = cd
        win.bind("<Button-1>", lambda e: self._close_popup())
        self._show_animated(win, seconds)

    def _logo(self, size):
        return self._photo(make_icon(size=self.px(size), dark_bg=self.theme_name() == "dark"), self.px(size))

    def _window_header(self, win, title, subtitle):
        c = self.c
        top = tk.Frame(win, bg=c["bg"])
        top.pack(fill="x", padx=self.px(16), pady=(self.px(14), self.px(6)))
        tk.Label(top, image=self._logo(36), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(12)))
        txt = tk.Frame(top, bg=c["bg"])
        txt.pack(side="left")
        tk.Label(txt, text=title, bg=c["bg"], fg=c["fg"], font=self.font(14, "bold")).pack(anchor="w")
        tk.Label(txt, text=subtitle, bg=c["bg"], fg=c["muted"], font=self.font(8)).pack(anchor="w")
        return top

    # ---- configuración
    def _switch(self, parent, value, on_change):
        """Interruptor tipo Windows 11 dibujado en un Canvas."""
        c, w, h = self.c, self.px(40), self.px(20)
        cv = tk.Canvas(parent, width=w, height=h, bg=parent.cget("bg"), highlightthickness=0, bd=0, cursor="hand2")
        state = {"on": bool(value)}

        def draw():
            cv.delete("all")
            on = state["on"]
            fill = KINDS["link"][2] if on else c["btn"]
            r = h // 2
            cv.create_oval(0, 0, h, h, fill=fill, width=0)
            cv.create_oval(w - h, 0, w, h, fill=fill, width=0)
            cv.create_rectangle(r, 0, w - r, h, fill=fill, width=0)
            k = self.px(4)
            cx = w - r if on else r
            cv.create_oval(cx - r + k, k, cx + r - k, h - k, fill="white" if on else c["muted"], width=0)

        def click(e):
            state["on"] = not state["on"]
            draw()
            on_change(state["on"])

        cv.bind("<Button-1>", click)
        draw()
        return cv

    def _segmented(self, parent, options, value, on_change):
        """Fila de botones donde solo uno está activo."""
        box = tk.Frame(parent, bg=parent.cget("bg"))
        buttons = {}
        state = {"v": value}

        def paint():
            for key, b in buttons.items():
                sel = key == state["v"]
                b._base_bg = KINDS["link"][2] if sel else self.c["btn"]
                b._base_fg = "white" if sel else self.c["fg"]
                b.config(bg=b._base_bg, fg=b._base_fg)

        def pick(key):
            state["v"] = key
            paint()
            on_change(key)

        for key, label, enabled in options:
            b = self._button(box, label, cmd=lambda k=key: pick(k))
            if not enabled:
                b.config(state="disabled", cursor="arrow")
            b.pack(side="left", padx=(0, self.px(4)), pady=self.px(2))
            buttons[key] = b
        paint()
        return box

    def _stepper(self, parent, choices, value, fmt, on_change):
        """[−] valor [+] sobre una lista de valores permitidos."""
        box = tk.Frame(parent, bg=parent.cget("bg"))
        idx = {"i": min(range(len(choices)), key=lambda i: abs(choices[i] - value))}
        lbl = tk.Label(box, text=fmt(choices[idx["i"]]), width=7, bg=parent.cget("bg"), fg=self.c["fg"],
                       font=self.font(10, "bold"))

        def move(d):
            idx["i"] = min(max(idx["i"] + d, 0), len(choices) - 1)
            lbl.config(text=fmt(choices[idx["i"]]))
            on_change(choices[idx["i"]])

        self._button(box, "−", cmd=lambda: move(-1)).pack(side="left")
        lbl.pack(side="left")
        self._button(box, "+", cmd=lambda: move(1)).pack(side="left")
        return box

    def show_settings(self):
        if self.settings_win is not None and self.settings_win.winfo_exists():
            self.settings_win.deiconify()
            self.settings_win.lift()
            self.settings_win.focus_force()
            return
        self.c = THEMES[self.theme_name()]
        c, st = self.c, self.settings
        win = tk.Toplevel(self.root, bg=c["bg"])
        self.settings_win = win
        win.title(f"{APP_NAME} · Configuración")
        win.geometry(f"{self.px(500)}x{self.px(680)}")
        win.minsize(self.px(420), self.px(360))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")

        self._window_header(win, "Configuración", f"{APP_NAME} {VERSION} · los cambios se guardan al momento")

        wrap = tk.Frame(win, bg=c["bg"])
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        body = tk.Frame(canvas, bg=c["bg"])
        wid = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(wid, width=e.width))
        win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        win.bind("<Escape>", lambda e: win.destroy())

        def section(title):
            tk.Label(body, text=title, bg=c["bg"], fg=c["muted"], font=self.font(9, "bold")).pack(
                anchor="w", padx=self.px(18), pady=(self.px(10), self.px(4)))
            card = tk.Frame(body, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
            card.pack(fill="x", padx=self.px(16))
            return card

        def row(card, title, hint=None, control=None, stacked=False):
            """Fila: texto a la izquierda y control a la derecha (o debajo si stacked)."""
            if card.winfo_children():
                tk.Frame(card, bg=c["border"], height=1).pack(fill="x")
            r = tk.Frame(card, bg=c["card"])
            r.pack(fill="x", padx=self.px(12), pady=self.px(8))
            if control and not stacked:  # el control se coloca antes para que el texto no lo empuje fuera
                control(r).pack(side="right", anchor="e", padx=(self.px(8), 0))
            txt = tk.Frame(r, bg=c["card"])
            txt.pack(side="top" if stacked else "left", fill="x", expand=True, anchor="w")
            tk.Label(txt, text=title, bg=c["card"], fg=c["fg"], font=self.font(10), anchor="w").pack(anchor="w")
            if hint:
                tk.Label(txt, text=hint, bg=c["card"], fg=c["muted"], font=self.font(8), anchor="w",
                         justify="left", wraplength=self.px(260)).pack(anchor="w")
            if control and stacked:
                control(r).pack(side="top", anchor="w", pady=(self.px(6), 0))

        save = lambda **kw: self.set_setting(**kw)

        def fmt_seconds(v):
            if v < 60:
                return f"{v} s"
            return f"{v // 60} min" if v % 60 == 0 else f"{v / 60:.1f} min"

        card = section("AVISO")
        row(card, "Tiempo visible", "Cuánto tarda en cerrarse solo.",
            lambda p: self._stepper(p, [5, 10, 15, 20, 25, 30, 45, 60, 90, 120, 180, 300], st["seconds"],
                                    fmt_seconds, lambda v: save(seconds=v)))
        row(card, "Cerrar solo", "Si lo desactivas, el aviso queda abierto hasta que lo cierres.",
            lambda p: self._switch(p, st["autoclose"], lambda v: save(autoclose=v)))
        row(card, "Pausar con el ratón encima", "La cuenta atrás se detiene mientras lo señalas.",
            lambda p: self._switch(p, st["pause_on_hover"], lambda v: save(pause_on_hover=v)))
        row(card, "Animación de entrada", None,
            lambda p: self._switch(p, st["animation"], lambda v: save(animation=v)))
        row(card, "Posición", "También puedes arrastrarlo desde su cabecera.",
            lambda p: self._segmented(p, [("top-right", "Arriba dcha.", True), ("bottom-right", "Abajo dcha.", True),
                                          ("center", "Centro", True),
                                          ("custom", "Donde lo dejé", st.get("x") is not None)],
                                      st["position"], lambda v: save(position=v)), stacked=True)
        row(card, "Probar", "Muestra un aviso de ejemplo con estos ajustes.",
            lambda p: self._button(p, "Ver aviso de prueba", cmd=lambda: self.show_popup([{
                "format": "QRCode", "text": "https://github.com/zxing-cpp/zxing-cpp",
                "thumb": Image.alpha_composite(Image.new("RGBA", (96, 96), "white"), make_icon(size=96)).convert("RGB"),
                "time": time.time()}])))

        card = section("APARIENCIA")

        def set_theme(v):
            save(theme=v)
            win.destroy()
            self.root.after(50, self.show_settings)  # se redibuja con el tema nuevo

        row(card, "Tema", None,
            lambda p: self._segmented(p, [("auto", "Como Windows", True), ("light", "Claro", True),
                                          ("dark", "Oscuro", True)], st["theme"], set_theme), stacked=True)

        card = section("DETECCIÓN")
        row(card, "Solo códigos QR", "Desactivado: también lee códigos de barras (EAN, Code 128, DataMatrix…).",
            lambda p: self._switch(p, st["qr_only"], lambda v: save(qr_only=v)))
        row(card, "Leer archivos copiados", "Imágenes copiadas desde el Explorador de archivos.",
            lambda p: self._switch(p, st["explorer_files"], lambda v: save(explorer_files=v)))
        row(card, "Borrar las capturas con QR",
            "Envía a la Papelera la captura que Windows guarda en Imágenes › Capturas de pantalla. "
            "Si está desactivado, el aviso muestra un botón para hacerlo.",
            lambda p: self._switch(p, st["delete_capture"], lambda v: save(delete_capture=v)))
        row(card, "Sonido al detectar", None,
            lambda p: self._switch(p, st["sound"], lambda v: save(sound=v)))
        row(card, "Pausar la detección", "No se escanea el portapapeles hasta que lo reactives.",
            lambda p: self._switch(p, self.paused, lambda v: self.paused != v and self.toggle_pause()))

        card = section("HISTORIAL")

        def set_max(v):
            save(history_max=v)
            del self.history[v:]
            self.tray.update_menu()

        row(card, "Guardar hasta", "Escaneos que se recuerdan mientras ClipQR está abierto.",
            lambda p: self._stepper(p, [10, 25, 50, 100, 200], st["history_max"], str, set_max))

        def clear_button(p):
            b = self._button(p, "Borrar historial")

            def clear():
                self.history.clear()
                self.tray.update_menu()
                if self.history_win is not None and self.history_win.winfo_exists():
                    self._fill_history()
                self._flash(b, "✓ Borrado")

            b.config(command=clear)
            return b

        row(card, "Borrar todo el historial", None, clear_button)

        card = section("GENERAL")
        row(card, "Iniciar con Windows", None,
            lambda p: self._switch(p, self.autostart_enabled(),
                                   lambda v: self.autostart_enabled() != v and self.toggle_autostart()))

        tk.Label(body, text="Los cambios se guardan al momento.", bg=c["bg"], fg=c["muted"],
                 font=self.font(8)).pack(pady=self.px(14))

    # ---- historial
    def show_history(self):
        if self.history_win is not None and self.history_win.winfo_exists():
            self.history_win.deiconify()
            self.history_win.lift()
            self.history_win.focus_force()
            return
        self.c = THEMES[self.theme_name()]
        c = self.c
        win = tk.Toplevel(self.root, bg=c["bg"])
        self.history_win = win
        win.title(f"{APP_NAME} · Historial")
        win.geometry(f"{self.px(520)}x{self.px(600)}")
        win.minsize(self.px(380), self.px(300))
        try:
            ico = ImageTk.PhotoImage(make_icon(size=32, dark_bg=self.theme_name() == "dark"))
            self._photos.append(ico)
            win.iconphoto(False, ico)
        except Exception:
            pass
        style_window(win, dark=self.theme_name() == "dark")

        top = tk.Frame(win, bg=c["bg"])
        top.pack(fill="x", padx=self.px(14), pady=(self.px(14), self.px(8)))
        tk.Label(top, image=self._logo(28), bg=c["bg"], bd=0).pack(side="left", padx=(0, self.px(10)))
        tk.Label(top, text="Historial", bg=c["bg"], fg=c["fg"], font=self.font(14, "bold")).pack(side="left")
        self._button(top, "Escanear ahora", cmd=lambda: self.scan(force=True)).pack(side="right")

        sbox = tk.Frame(win, bg=c["card"], highlightthickness=1, highlightbackground=c["border"])
        sbox.pack(fill="x", padx=self.px(14), pady=(0, self.px(8)))
        if self.icon_font:
            tk.Label(sbox, text="", font=(self.icon_font, 10), bg=c["card"], fg=c["muted"]).pack(side="left", padx=(self.px(8), 0))
        self.search_var = tk.StringVar()
        entry = tk.Entry(sbox, textvariable=self.search_var, bg=c["card"], fg=c["fg"], insertbackground=c["fg"],
                         relief="flat", font=self.font(10), highlightthickness=0)
        entry.pack(fill="x", padx=self.px(8), pady=self.px(6))
        self.search_var.trace_add("write", lambda *a: self._fill_history())

        wrap = tk.Frame(win, bg=c["bg"])
        wrap.pack(fill="both", expand=True, padx=(self.px(14), 0), pady=(0, self.px(14)))
        canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)
        self.hist_list = tk.Frame(canvas, bg=c["bg"])
        wid = canvas.create_window((0, 0), window=self.hist_list, anchor="nw")
        self.hist_list.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(wid, width=e.width - self.px(10)))
        win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        win.bind("<Escape>", lambda e: win.destroy())
        self._fill_history()
        entry.focus_set()

    def _fill_history(self):
        c = self.c
        for w in self.hist_list.winfo_children():
            w.destroy()
        q = self.search_var.get().strip().lower()
        entries = [code for scan in self.history for code in scan if not q or q in code["text"].lower()]
        if not entries:
            tk.Label(self.hist_list, text="Sin resultados." if q else "Aún no se ha detectado ningún código.\n"
                     "Haz una captura de un QR (Win+Shift+S o Impr Pant).", bg=c["bg"], fg=c["muted"],
                     font=self.font(10), justify="center").pack(pady=self.px(40))
            return
        for code in entries:
            kind, title, items, _ = parse_payload(code["text"])
            row = tk.Frame(self.hist_list, bg=c["card"], highlightthickness=1, highlightbackground=c["border"],
                           cursor="hand2")
            row.pack(fill="x", pady=(0, self.px(6)))
            # el botón se coloca primero para que un texto largo no lo saque de la fila
            b = self._button(row, "Copiar")
            b.config(command=lambda t=code["text"], b=b: self.copy(t, b))
            b.pack(side="right", padx=self.px(8))
            if code.get("thumb") is not None:
                tk.Label(row, image=self._photo(code["thumb"], self.px(44)), bg=c["card"], bd=0).pack(side="left", padx=self.px(8), pady=self.px(8))
            mid = tk.Frame(row, bg=c["card"])
            mid.pack(side="left", fill="x", expand=True, pady=self.px(6))
            line = tk.Frame(mid, bg=c["card"])
            line.pack(anchor="w")
            g, gf = self.glyph(kind)
            tk.Label(line, text=g, font=gf, bg=c["card"], fg=KINDS[kind][2]).pack(side="left", padx=(0, self.px(6)))
            tk.Label(line, text=title, bg=c["card"], fg=c["fg"], font=self.font(10, "bold")).pack(side="left")
            tk.Label(line, text="  " + time.strftime("%H:%M", time.localtime(code["time"])), bg=c["card"],
                     fg=c["muted"], font=self.font(8)).pack(side="left")
            # resumen legible (Ana Pérez · +34 600…) en vez del texto crudo de vCard / Wi-Fi
            summary = [v for l, v in items if l not in ("Contraseña", "Secreto", "Dominio")][:3]
            preview = " · ".join(summary) if kind not in ("link", "text", "product") and summary else \
                code["text"].replace("\r", "").replace("\n", " · ")
            tk.Label(mid, text=(preview[:52] + "…") if len(preview) > 52 else preview, bg=c["card"],
                     fg=c["muted"], font=self.font(9), anchor="w").pack(anchor="w", fill="x")
            open_it = lambda e, cd=code: self.show_popup([cd])
            for w in (row, mid, line, *mid.winfo_children(), *line.winfo_children(), *row.winfo_children()):
                if w is not b:
                    w.bind("<Button-1>", open_it)

    def run(self):
        self.root.mainloop()


def _shade(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


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


def uninstall():
    """Desinstalación (instalado con ClipQR-Setup.exe): cierra ClipQR, quita accesos directos,
    inicio con Windows, la entrada de «Aplicaciones instaladas», los ajustes y el propio programa."""
    import shutil
    import subprocess
    import winreg
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    if not messagebox.askyesno("Desinstalar ClipQR", "¿Quieres desinstalar ClipQR de este equipo?"):
        return
    no_window = 0x08000000
    subprocess.run(["taskkill", "/F", "/IM", "ClipQR.exe", "/FI", f"PID ne {os.getpid()}",
                    "/FI", f"PID ne {os.getppid()}"], capture_output=True, creationflags=no_window)
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
    shutil.rmtree(CONFIG_DIR, ignore_errors=True)
    messagebox.showinfo("ClipQR", "ClipQR se ha desinstalado.")
    root.destroy()
    if FROZEN:  # el programa no puede borrarse a sí mismo mientras se ejecuta: cmd lo reintenta al salir
        exe, folder = sys.executable, os.path.dirname(sys.executable)
        setup_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", APP_NAME)
        if os.path.normcase(folder) == os.path.normcase(setup_dir):  # carpeta del asistente: entera
            remove = f'rmdir /s /q "{folder}" 2>nul & if not exist "{folder}" exit'
        else:  # en cualquier otro sitio solo el propio .exe (y la carpeta si queda vacía)
            remove = f'del /f /q "{exe}" 2>nul & if not exist "{exe}" (rmdir "{folder}" 2>nul & exit)'
        subprocess.Popen(f'cmd /c for /l %i in (1,1,30) do (ping -n 2 127.0.0.1 >nul & {remove})',
                         creationflags=no_window)


def shortcut_paths():
    """Accesos directos que puede crear el asistente: menú Inicio y escritorio."""
    def folder(csidl):  # rutas reales (el escritorio puede estar en OneDrive)
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf)
        return buf.value

    return [os.path.join(folder(0x02), f"{APP_NAME}.lnk"),   # CSIDL_PROGRAMS (menú Inicio)
            os.path.join(folder(0x10), f"{APP_NAME}.lnk")]   # CSIDL_DESKTOPDIRECTORY


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if sys.argv[1:] == ["--uninstall"]:  # lo lanza Windows desde «Aplicaciones instaladas»
        uninstall()
        return
    if len(sys.argv) > 1:  # modo prueba: python clipqr.py imagen.png
        sys.stdout.reconfigure(encoding="utf-8")
        for path in sys.argv[1:]:
            for c in decode_image(Image.open(path)):
                print(c["format"], "|", c["text"], "|", parse_payload(c["text"]))
        return
    if not single_instance():
        return
    ClipQR().run()


if __name__ == "__main__":
    main()
