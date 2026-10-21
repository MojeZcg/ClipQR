"""Genera el logo a partir de assets/logo-source.jpg:

    assets/logo.png        trazos negros sobre fondo transparente (fondos claros)
    assets/logo-white.png  el mismo logo en blanco (fondos oscuros)

    py tools/make_logo.py

  1. Solo se conservan los trazos. La imagen original trae dibujada la cuadrícula gris/blanca
     de "transparencia": todo lo que no es trazo (fondo e interior de la hoja) queda transparente.
     La opacidad sale del gris original, así los bordes conservan su suavizado.
  2. El QR decorativo se sustituye por uno real que apunta al repositorio (corrección de
     errores H). Igual que en el original, el QR se corta siguiendo la curva de la esquina
     doblada, con el mismo margen hasta el borde de la hoja.
  3. Se comprueba que el QR del logo se lee, en negro sobre blanco y en blanco sobre oscuro.
"""
import os
import sys

import numpy as np
import zxingcpp
from PIL import Image, ImageChops, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "logo-source.jpg")
OUT_DARK_INK = os.path.join(ROOT, "assets", "logo.png")
OUT_WHITE_INK = os.path.join(ROOT, "assets", "logo-white.png")
SIZE = 1024
URL = "https://github.com/MojeZcg/ClipQR"

# Coordenadas en logo-source.jpg (2000×1493)
QR_ORIGIN, QR_MODULE = (439, 144), 33     # esquina del QR original y tamaño de módulo
OLD_QR = (420, 125, 1560, 1300)           # zona del QR decorativo que se borra
# borde interior del trazo de la esquina doblada (medido sobre la imagen), de arriba abajo
CURL_EDGE = [(1623, 780), (1600, 880), (1561, 950), (1520, 1000), (1471, 1050), (1422, 1100),
             (1376, 1150), (1330, 1200), (1285, 1250), (1240, 1300), (1190, 1350), (1120, 1395)]
KEEP_MARGIN = 12   # px hacia el QR que se conservan del trazo (su suavizado)
QR_GAP = 50        # px (en horizontal) entre el borde doblado y el QR, como en el original
INK, PAPER = 70, 150   # gris ≤ INK: trazo opaco; ≥ PAPER: transparente


def beyond_curl(size, shift):
    """Máscara de la zona de la esquina doblada: a la derecha/abajo de CURL_EDGE desplazado `shift` px."""
    w, h = size
    pts = [(x - shift, y) for x, y in CURL_EDGE]
    poly = pts + [(w, pts[-1][1]), (w, pts[0][1])]
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    return mask


def real_qr(size):
    """Opacidad del QR real (255 = módulo), colocado donde estaba el decorativo."""
    bc = zxingcpp.create_barcode(URL, zxingcpp.BarcodeFormat.QRCode, ec_level="H")
    modules = np.array(bc.to_image(scale=1, add_quiet_zones=False)) < 128
    n = modules.shape[0]
    qr = Image.fromarray((modules * 255).astype(np.uint8), "L").resize((n * QR_MODULE,) * 2, Image.NEAREST)
    layer = Image.new("L", size, 0)
    layer.paste(qr, QR_ORIGIN)
    return layer


def readable(logo, ink, bg):
    test = Image.new("RGB", logo.size, bg)
    test.paste(Image.new("RGB", logo.size, ink), (0, 0), logo.getchannel("A"))
    return URL in [r.text for r in zxingcpp.read_barcodes(test)]


def main():
    gray = Image.open(SRC).convert("L")
    # opacidad desde el gris: negro = opaco, blanco y gris de la cuadrícula (≈200) = transparente
    alpha = gray.point(lambda v: 255 if v <= INK else 0 if v >= PAPER else round(255 * (PAPER - v) / (PAPER - INK)))

    # borrar el QR decorativo, conservando el trazo de la esquina doblada y el clip
    erase = Image.new("L", alpha.size, 0)
    ImageDraw.Draw(erase).rectangle(OLD_QR, fill=255)
    erase = ImageChops.subtract(erase, beyond_curl(alpha.size, KEEP_MARGIN))
    alpha = ImageChops.subtract(alpha, erase)

    # QR real, recortado con el mismo margen hasta el borde doblado que tenía el original
    qr = ImageChops.subtract(real_qr(alpha.size), beyond_curl(alpha.size, QR_GAP))
    alpha = ImageChops.lighter(alpha, qr)

    # recortar al dibujo, centrar en un cuadrado con un pequeño margen y reducir con antialias
    alpha = alpha.crop(alpha.point(lambda v: 255 if v > 8 else 0).getbbox())
    side = round(max(alpha.size) * 1.04)
    square = Image.new("L", (side, side), 0)
    square.paste(alpha, ((side - alpha.width) // 2, (side - alpha.height) // 2))
    alpha = square.resize((SIZE, SIZE), Image.LANCZOS)

    dark_ink = Image.merge("RGBA", (*Image.new("RGB", alpha.size, (0, 0, 0)).split(), alpha))
    white_ink = Image.merge("RGBA", (*Image.new("RGB", alpha.size, (255, 255, 255)).split(), alpha))
    if not readable(dark_ink, "black", "white") or not readable(white_ink, "white", (32, 32, 32)):
        dark_ink.save(OUT_DARK_INK.replace(".png", "-fallido.png"))
        sys.exit("El QR del logo no se puede leer (guardado logo-fallido.png para revisarlo)")
    dark_ink.save(OUT_DARK_INK, optimize=True)
    white_ink.save(OUT_WHITE_INK, optimize=True)
    print("Logos:", OUT_DARK_INK, OUT_WHITE_INK, "· QR verificado ->", URL)


if __name__ == "__main__":
    main()
