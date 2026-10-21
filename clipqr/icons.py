"""Logo de ClipQR en sus variantes (claro, oscuro, con contorno, en pausa)."""
import os
import sys

from PIL import Image, ImageFilter, ImageOps

_LOGOS = {}

def _resource(*parts):
    """Ruta a un archivo del proyecto, también dentro del .exe de PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
