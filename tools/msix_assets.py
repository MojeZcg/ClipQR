"""Genera los iconos del paquete MSIX (con calificadores de escala) a partir del logo de clipqr.py.

    py tools/msix_assets.py <carpeta_destino>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

import clipqr  # noqa: E402

SCALES = (100, 125, 150, 200, 400)


def tile(w, h, logo_ratio):
    """Lienzo transparente w×h con el logo centrado ocupando logo_ratio del lado menor."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s = round(min(w, h) * logo_ratio)
    logo = clipqr.make_icon(size=s)
    img.alpha_composite(logo, ((w - s) // 2, (h - s) // 2))
    return img


def main(out):
    os.makedirs(out, exist_ok=True)
    save = lambda img, name: img.save(os.path.join(out, name))
    for sc in SCALES:
        f = sc / 100
        save(clipqr.make_icon(size=round(44 * f)), f"Square44x44Logo.scale-{sc}.png")
        save(tile(round(150 * f), round(150 * f), 0.62), f"Square150x150Logo.scale-{sc}.png")
        save(tile(round(310 * f), round(150 * f), 0.62), f"Wide310x150Logo.scale-{sc}.png")
        save(tile(round(71 * f), round(71 * f), 0.7), f"SmallTile.scale-{sc}.png")
        save(tile(round(310 * f), round(310 * f), 0.5), f"LargeTile.scale-{sc}.png")
        save(clipqr.make_icon(size=round(50 * f)), f"StoreLogo.scale-{sc}.png")
    # iconos de barra de tareas / menú Inicio a tamaño exacto (con y sin placa de color)
    for ts in (16, 24, 32, 48, 256):
        icon = clipqr.make_icon(size=ts)
        save(icon, f"Square44x44Logo.targetsize-{ts}.png")
        save(icon, f"Square44x44Logo.targetsize-{ts}_altform-unplated.png")
        save(icon, f"Square44x44Logo.targetsize-{ts}_altform-lightunplated.png")
    print("Iconos MSIX en", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build/msix-layout/Assets")
