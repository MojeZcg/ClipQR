"""Lectura de códigos en imágenes: capturas, fotos difíciles, varios códigos, sin códigos."""
from PIL import Image

from clipqr.decode import decode_image, make_thumb

from conftest import blurry_photo, code_image, on_canvas

SAMPLES = [
    ("QRCode", "WIFI:S:MiCasa;T:WPA;P:clave;;"),
    ("QRCode", "BEGIN:VCARD\nVERSION:3.0\nFN:Ana Pérez\nTEL:+34600111222\nEND:VCARD"),
    ("QRCode", "https://github.com/MojeZcg/ClipQR"),
    ("DataMatrix", "Hola DataMatrix"),
    ("EAN13", "8410000810004"),
    ("Code128", "CLIPQR-128"),
]


def texts(img, **kw):
    return [r["text"] for r in decode_image(img, **kw)]


def test_each_format_in_a_screenshot():
    for fmt, text in SAMPLES:
        assert texts(on_canvas(code_image(text, fmt))) == [text], fmt


def test_blurry_photo_of_printed_qr():
    # la foto borrosa de un QR impreso sin margen era el caso que fallaba con el binarizador por defecto
    img = blurry_photo(code_image("https://example.com/ticket/1234567890", scale=10))
    assert texts(img) == ["https://example.com/ticket/1234567890"]


def test_two_codes_in_one_image():
    canvas = on_canvas(code_image("https://example.com/a"), at=(100, 100))
    canvas.paste(code_image("WIFI:S:B;T:WPA;P:p;;"), (700, 300))
    assert sorted(texts(canvas)) == ["WIFI:S:B;T:WPA;P:p;;", "https://example.com/a"]


def test_no_code_returns_empty_list():
    assert decode_image(Image.new("RGB", (1280, 800), (30, 30, 30))) == []


def test_qr_only_ignores_barcodes():
    img = on_canvas(code_image("8410000810004", "EAN13"))
    assert texts(img, qr_only=True) == []
    assert texts(img, qr_only=False) == ["8410000810004"]


def test_transparent_png_is_read_on_white():
    qr = code_image("transparente").convert("RGBA")
    qr.putalpha(qr.convert("L").point(lambda v: 255 if v < 128 else 0))  # solo los módulos son opacos
    assert texts(qr) == ["transparente"]


def test_box_and_thumbnail_follow_the_code():
    canvas = on_canvas(code_image("https://example.com/box"), at=(600, 300))
    (result,) = decode_image(canvas)
    x0, y0, x1, y1 = result["box"]
    assert 590 <= x0 <= 640 and 290 <= y0 <= 340
    thumb = make_thumb(canvas, result["box"])
    assert max(thumb.size) <= 128 and abs(thumb.width - thumb.height) <= 2
