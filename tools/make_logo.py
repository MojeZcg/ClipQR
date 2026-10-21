"""Genera assets/logo.png (1024×1024, fondo transparente) a partir de assets/logo-source.jpg.

    py tools/make_logo.py

  1. De la imagen original se quedan solo los trazos negros: trae dibujada la cuadrícula
     gris/blanca de "transparencia", que se descarta.
  2. El QR decorativo se sustituye por uno real que apunta al repositorio (corrección de
     errores H, para que la esquina doblada que lo tapa no impida leerlo).
  3. Lo que está fuera del dibujo pasa a ser transparente y el interior de la hoja se rellena
     de blanco, para que el logo se vea también sobre fondos oscuros.
  4. Se comprueba que el QR del logo final se puede escanear.
"""
import os
import sys

import numpy as np
import zxingcpp
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "logo-source.jpg")
OUT = os.path.join(ROOT, "assets", "logo.png")
SIZE = 1024
URL = "https://github.com/MojeZcg/ClipQR"

# Coordenadas en logo-source.jpg (2000×1493)
QR_ORIGIN, QR_MODULE = (439, 144), 33          # esquina del QR original y tamaño de módulo
OLD_QR = (430, 135, 1540, 1285)                # zona del QR decorativo que se borra
FOLD = [(1528, 840), (1120, 1290)]             # recta paralela al doblez: el QR se corta antes
SEALS = [[(1110, 1372), (1265, 1372)],         # entre el borde inferior y el extremo del clip
         [(1400, 1105), (1285, 1255)]]         # donde el clip corta el borde doblado de la hoja


def side_of_fold(size, shift=0):
    """Máscara de la parte de arriba a la izquierda de FOLD (desplazada `shift` px hacia allí)."""
    (x1, y1), (x2, y2) = FOLD
    w, h = size
    nx, ny = y1 - y2, x2 - x1  # normal que apunta hacia arriba a la izquierda
    norm = (nx * nx + ny * ny) ** 0.5
    ys, xs = np.mgrid[0:h, 0:w]
    d = ((xs - x1) * nx + (ys - y1) * ny) / norm
    return Image.fromarray(((d > shift) * 255).astype(np.uint8), "L")


def real_qr(size):
    """Tinta (255 = negro) del QR real, colocado donde estaba el decorativo y cortado antes del doblez."""
    bc = zxingcpp.create_barcode(URL, zxingcpp.BarcodeFormat.QRCode, ec_level="H")
    modules = np.array(bc.to_image(scale=1, add_quiet_zones=False)) < 128
    n = modules.shape[0]
    qr = Image.fromarray((modules * 255).astype(np.uint8), "L").resize((n * QR_MODULE,) * 2, Image.NEAREST)
    layer = Image.new("L", size, 0)
    layer.paste(qr, QR_ORIGIN)
    box = Image.new("L", size, 0)
    x0, y0 = QR_ORIGIN
    ImageDraw.Draw(box).rectangle((x0, y0, x0 + n * QR_MODULE - 1, y0 + n * QR_MODULE - 1), fill=255)
    return layer, box


def main():
    gray = Image.open(SRC).convert("L")
    ink = gray.point(lambda v: 255 if v < 128 else 0)  # trazos negros
    ink = ink.filter(ImageFilter.MedianFilter(3))  # quitar ruido de compresión JPEG

    # QR: se borra el decorativo (hasta el doblez) y se pone el real
    qr, box = real_qr(ink.size)
    erase = Image.new("L", ink.size, 0)
    ImageDraw.Draw(erase).rectangle(OLD_QR, fill=255)
    zone = ImageChops.multiply(ImageChops.lighter(erase, box), side_of_fold(ink.size))
    ink = ImageChops.subtract(ink, zone)
    ink = ImageChops.lighter(ink, ImageChops.multiply(qr, side_of_fold(ink.size, shift=14)))

    # fuera = zona sin tinta conectada con el borde (relleno por inundación desde las esquinas).
    # La esquina doblada y el clip dejan la hoja abierta por dos sitios: se tapan solo para
    # calcular el relleno (no se dibujan).
    seals = Image.new("L", ink.size, 0)
    for seal in SEALS:
        ImageDraw.Draw(seals).line(seal, fill=255, width=14)
    # engordar 2 px cierra las rendijas de 1-2 px que deja la compresión entre trazos
    region = ImageChops.lighter(ink, seals).filter(ImageFilter.MaxFilter(5))
    w, h = region.size
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if region.getpixel(seed) == 0:
            ImageDraw.floodfill(region, seed, 128)
    outside = region.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(5))
    shape = ImageChops.lighter(ImageChops.invert(outside), ink)  # interior + toda la tinta
    shape = ImageChops.subtract(shape, ImageChops.subtract(seals, ink))  # los tapones no se ven

    # antialias: el borde exterior se suaviza un poco
    alpha = shape.filter(ImageFilter.GaussianBlur(1.2))
    rgb = Image.merge("RGB", [ImageChops.invert(ink.filter(ImageFilter.GaussianBlur(0.8)))] * 3)
    logo = Image.merge("RGBA", (*rgb.split(), alpha))

    # recortar al dibujo y centrar en un cuadrado con un pequeño margen
    logo = logo.crop(shape.getbbox())
    side = round(max(logo.size) * 1.04)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(logo, ((side - logo.width) // 2, (side - logo.height) // 2))
    canvas = canvas.resize((SIZE, SIZE), Image.LANCZOS)

    # el QR del logo tiene que leerse
    for bg in ("white", (32, 32, 32)):
        test = Image.new("RGB", canvas.size, bg)
        test.paste(canvas, (0, 0), canvas)
        found = [r.text for r in zxingcpp.read_barcodes(test)]
        if URL not in found:
            sys.exit(f"El QR del logo no se lee sobre fondo {bg} (leído: {found})")
    canvas.save(OUT, optimize=True)
    print("Logo:", OUT, "· QR verificado ->", URL)


if __name__ == "__main__":
    main()
