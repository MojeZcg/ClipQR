"""Lectura de códigos en imágenes (zxing-cpp) y obtención de imágenes del portapapeles."""
import os

import zxingcpp
from PIL import Image, ImageFilter, ImageGrab, ImageOps

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"}

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
