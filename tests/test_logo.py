"""El QR del logo tiene que llevar al repositorio, en sus dos variantes."""
import os

from PIL import Image

from clipqr.decode import decode_image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://github.com/MojeZcg/ClipQR"


def flatten(path, bg):
    logo = Image.open(os.path.join(ROOT, "assets", path)).convert("RGBA")
    out = Image.new("RGBA", logo.size, bg)
    out.alpha_composite(logo)
    return out.convert("RGB")


def test_logo_qr_points_to_repo():
    assert URL in [r["text"] for r in decode_image(flatten("logo.png", "white"))]


def test_white_logo_qr_points_to_repo():
    assert URL in [r["text"] for r in decode_image(flatten("logo-white.png", (32, 32, 32)))]
