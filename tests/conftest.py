"""Utilidades compartidas por los tests: generar imágenes con códigos sin depender de archivos."""
import numpy as np
import pytest
import zxingcpp
from PIL import Image, ImageFilter

from clipqr import i18n


@pytest.fixture(autouse=True)
def spanish():
    """Los tests comprueban los textos en español salvo que pidan otro idioma."""
    i18n.set_language("es")
    yield
    i18n.set_language("es")


def code_image(text, fmt="QRCode", scale=6, ec_level=None):
    """Imagen RGB con el código `text` (formato zxing por nombre: QRCode, EAN13, DataMatrix…)."""
    kwargs = {"ec_level": ec_level} if ec_level else {}
    bc = zxingcpp.create_barcode(text, getattr(zxingcpp.BarcodeFormat, fmt), **kwargs)
    return Image.fromarray(np.array(bc.to_image(scale=scale))).convert("RGB")


def on_canvas(img, size=(1280, 800), at=(400, 200), bg=(238, 240, 245)):
    """Pega la imagen en un lienzo grande, como si fuera una captura de pantalla (crece si no cabe)."""
    size = (max(size[0], at[0] + img.width + 40), max(size[1], at[1] + img.height + 40))
    canvas = Image.new("RGB", size, bg)
    canvas.paste(img, at)
    return canvas


def blurry_photo(img):
    """Simula la foto borrosa de un QR impreso: poco contraste, desenfoque, sin margen y ligeramente girada."""
    w, h = img.size
    img = img.crop((int(w * 0.04), int(h * 0.04), int(w * 0.96), int(h * 0.96)))  # sin zona de silencio
    img = img.rotate(3, resample=Image.BICUBIC, fillcolor=(200, 200, 200), expand=True)
    img = img.point(lambda v: 70 + v * 120 // 255)  # gris sobre gris
    return img.filter(ImageFilter.GaussianBlur(2.2)).resize((w * 2 // 3, h * 2 // 3), Image.BILINEAR)


@pytest.fixture
def make_code():
    return code_image
