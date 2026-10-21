"""Crear códigos QR: armar el contenido de cada tipo (lo inverso de payloads.py) y dibujar la imagen.

Cada QR generado se vuelve a leer con decode_image antes de entregarlo (verify) para no dar nunca un
código que no se pueda escanear (por ejemplo, con un logo demasiado grande o poco contraste)."""
import re
import urllib.parse

import zxingcpp
from PIL import Image, ImageDraw, ImageOps

EC_LEVELS = ("L", "M", "Q", "H")  # corrección de errores: ~7 %, 15 %, 25 %, 30 %


# ---------------------------------------------------------------- contenido de cada tipo

def _esc(value):
    """Escapa los separadores de los formatos WIFI:/MECARD: (\\ ; , : ")."""
    return re.sub(r'([\\;,:"])', r"\\\1", value)


def _vesc(value):
    """Escapa texto de vCard (RFC 6350): \\, coma, punto y coma y saltos de línea."""
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def build_wifi(ssid, password="", security="WPA", hidden=False):
    security = "nopass" if not password else security
    out = f"WIFI:T:{security};S:{_esc(ssid)};"
    if password:
        out += f"P:{_esc(password)};"
    if hidden:
        out += "H:true;"
    return out + ";"


def build_vcard(name="", phone="", email="", org="", url="", title="", note=""):
    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    if name:
        parts = name.strip().split()
        last, first = (parts[-1], " ".join(parts[:-1])) if len(parts) > 1 else (name.strip(), "")
        lines += [f"N:{_vesc(last)};{_vesc(first)};;;", f"FN:{_vesc(name.strip())}"]
    for key, value in (("ORG", org), ("TITLE", title), ("TEL", phone), ("EMAIL", email), ("URL", url),
                       ("NOTE", note)):
        if value:
            lines.append(f"{key}:{_vesc(value.strip())}")
    return "\n".join(lines + ["END:VCARD"])


def build_email(to, subject="", body=""):
    q = urllib.parse.urlencode({k: v for k, v in (("subject", subject), ("body", body)) if v},
                               quote_via=urllib.parse.quote)
    return f"mailto:{to}" + (f"?{q}" if q else "")


def build_tel(number):
    return "tel:" + re.sub(r"[^\d+]", "", number)


def build_sms(number, message=""):
    digits = re.sub(r"[^\d+]", "", number)
    return f"SMSTO:{digits}:{message}"


def build_geo(lat, lon):
    return f"geo:{float(lat):.6f},{float(lon):.6f}".replace(".000000", "")


def build_whatsapp(number, message=""):
    digits = re.sub(r"\D", "", number)
    return f"https://wa.me/{digits}" + (f"?text={urllib.parse.quote(message)}" if message else "")


def build_url(text):
    t = text.strip()
    if re.match(r"^www\.\S+$", t, re.I):
        return "https://" + t
    return t


# ---------------------------------------------------------------- imagen

def _matrix(text, ec_level):
    bc = zxingcpp.create_barcode(text, zxingcpp.BarcodeFormat.QRCode, ec_level=ec_level)
    m = memoryview(bc.to_image(scale=1, add_quiet_zones=False))
    h, w = m.shape
    return bc, Image.frombuffer("L", (w, h), m.tobytes(), "raw", "L", 0, 1)


def make_qr(text, ec_level="M", module=10, margin=4, fg="#000000", bg="#ffffff", logo=None):
    """Imagen RGB del QR. module = píxeles por módulo; margin = módulos de zona de silencio (mín. 4 recomendado).
    logo: imagen RGBA que se pone en el centro (fuerza la corrección H y ocupa ~20 % del lado)."""
    if logo is not None:
        ec_level = "H"
    _, m = _matrix(text, ec_level)
    m = m.resize((m.width * module, m.height * module), Image.NEAREST)
    m = ImageOps.expand(m, border=margin * module, fill=255)
    img = ImageOps.colorize(m, black=fg, white=bg).convert("RGB")
    if logo is not None:
        side = img.width
        size = int(side * 0.20)
        pad = max(4, size // 10)
        box = (side - size) // 2
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((box - pad, box - pad, box + size + pad, box + size + pad), radius=pad * 2, fill=bg)
        mark = logo.convert("RGBA").resize((size, size), Image.LANCZOS)
        img.paste(mark, (box, box), mark)
    return img


def make_svg(text, ec_level="M"):
    bc, _ = _matrix(text, ec_level)
    return bc.to_svg(add_quiet_zones=True)


def contrast_ratio(fg, bg):
    """Contraste WCAG entre dos colores «#rrggbb» (1 a 21). Para leer bien un QR conviene ≥ 4."""
    def lum(hex_color):
        h = hex_color.lstrip("#")
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def verify(img, text):
    """True si el QR generado se lee y dice exactamente `text`."""
    from clipqr.decode import decode_image
    return any(r["text"] == text for r in decode_image(img))
