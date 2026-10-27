"""Genera el GIF de demostración del README (español e inglés) y la imagen para redes sociales.

    py tools/demo_gif.py

Abre el aviso real de ClipQR con datos de ejemplo (nada personal), lo captura y lo monta sobre un fondo:
capturar un QR → aparece el aviso → copiar. Cierra ClipQR antes de ejecutarlo: los avisos se ven unos
segundos en la pantalla mientras se capturan.
"""
import ctypes
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tests")]
ctypes.windll.shcore.SetProcessDpiAwareness(1)

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageGrab  # noqa: E402

import clipqr.app as app  # noqa: E402
from clipqr import i18n  # noqa: E402
from clipqr.generate import make_qr  # noqa: E402
from clipqr.icons import make_icon  # noqa: E402
from screenshots import FakeTray  # noqa: E402
from test_fiscal_ar import qr as arca_qr  # noqa: E402

OUT = os.path.join(ROOT, "docs", "screenshots")
FONTS = r"C:\Windows\Fonts"
W, H = 1280, 720
LINK = "https://github.com/MojeZcg/ClipQR"
WIFI = "WIFI:T:WPA;S:Cafeteria Central;P:cafe-con-leche-2026;;"
INVOICE = arca_qr(tipoCmp=6, importe=48750.5)

CAPTIONS = {
    "es": ["Haz una captura de un QR  ·  Win + Shift + S", "ClipQR lo lee al momento",
           "Copia todo o solo la parte que quieras", "Wi‑Fi: conéctate con un clic",
           "Facturas, pagos, productos… en 10 idiomas"],
    "en": ["Screenshot a QR code  ·  Win + Shift + S", "ClipQR reads it instantly",
           "Copy all of it, or just the part you need", "Wi‑Fi: connect with one click",
           "Invoices, payments, products… in 10 languages"],
}


def font(size, bold=False):
    return ImageFont.truetype(os.path.join(FONTS, "seguisb.ttf" if bold else "segoeui.ttf"), size)


def backdrop():
    """Escritorio oscuro con una «página» que muestra un QR (lo que el usuario captura)."""
    bg = Image.new("RGB", (W, H), "#0f172a")
    d = ImageDraw.Draw(bg)
    for y in range(H):  # degradado suave
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * t), int(23 + 25 * t), int(42 + 40 * t)))
    card = (110, 110, 610, 600)
    d.rounded_rectangle(card, 18, fill="#f8fafc")
    d.rounded_rectangle((card[0], card[1], card[2], card[1] + 44), 18, fill="#e2e8f0")
    d.rectangle((card[0], card[1] + 26, card[2], card[1] + 44), fill="#e2e8f0")
    for i, col in enumerate(("#ef4444", "#f59e0b", "#22c55e")):
        d.ellipse((card[0] + 18 + i * 22, card[1] + 15, card[0] + 32 + i * 22, card[1] + 29), fill=col)
    d.text((card[0] + 40, card[1] + 70), "ClipQR", font=font(34, True), fill="#0f172a")
    d.text((card[0] + 40, card[1] + 118), "github.com/MojeZcg/ClipQR", font=font(18), fill="#475569")
    code = make_qr(LINK, module=8).convert("RGB").resize((280, 280), Image.NEAREST)
    bg.paste(code, (card[0] + 110, card[1] + 170))
    return bg, (card[0] + 100, card[1] + 160, card[0] + 400, card[1] + 460)


def caption(img, text):
    img = img.copy()
    d = ImageDraw.Draw(img)
    f = font(30, True)
    w = d.textlength(text, font=f)
    x, y = (W - w) / 2, H - 78
    d.rounded_rectangle((x - 26, y - 14, x + w + 26, y + 50), 14, fill="#1d4ed8")
    d.text((x, y), text, font=f, fill="white")
    return img


def capture_popups(lang):
    """Captura el aviso real para cada código, más el aviso del enlace con «✓ Copiado»."""
    app.ClipQR._build_tray = lambda self: FakeTray()
    app.ClipQR.first_run = lambda self: None
    app.ClipQR.startup_notice = lambda self: None
    a = app.ClipQR()
    a.hotkeys.stop()
    a.settings["theme"] = "dark"
    i18n.set_language(lang)
    thumb = make_qr(LINK, module=4).convert("RGB")
    jobs = [("link", [LINK], False), ("copied", [LINK], True), ("wifi", [WIFI], False), ("invoice", [INVOICE], False)]
    shots = {}

    def grab(name):
        win = a.popup
        win.attributes("-alpha", 1.0)  # opaco del todo: si no, se cuela lo que haya detrás en la pantalla
        win.update()
        x, y = win.winfo_rootx(), win.winfo_rooty()
        shots[name] = ImageGrab.grab((x, y, x + win.winfo_width(), y + win.winfo_height()), all_screens=True)

    def step(i=0):
        if i == len(jobs):
            a._close_popup()
            a.root.destroy()
            return
        name, texts, copy = jobs[i]
        a.show_popup([{"format": "QRCode", "text": t, "thumb": thumb} for t in texts])
        if copy:
            a.root.after(1200, lambda: (a.popup._kbd_copy[0].invoke(), a.root.after(150, lambda: (grab(name), step(i + 1)))))
        else:
            a.root.after(1300, lambda: (grab(name), step(i + 1)))

    a.root.after(600, step)
    a.root.mainloop()
    return shots


def place(base, popup, scale=0.82):
    img = base.copy()
    p = popup.resize((int(popup.width * scale), int(popup.height * scale)), Image.LANCZOS)
    p = p.crop((0, 0, p.width, min(p.height, H - 120)))
    shadow = Image.new("RGBA", (p.width + 40, p.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((20, 24, p.width + 20, p.height + 24), 12, fill=(0, 0, 0, 140))
    x, y = W - p.width - 40, 30
    img.paste(shadow.filter(ImageFilter.GaussianBlur(10)), (x - 20, y - 20), shadow.filter(ImageFilter.GaussianBlur(10)))
    img.paste(p, (x, y))
    return img


def make_gif(lang, shots):
    base, qr_box = backdrop()
    cap = CAPTIONS[lang]
    snip = base.copy()
    dim = Image.new("RGB", (W, H), "black")
    snip = Image.blend(snip, dim, 0.45)
    snip.paste(base.crop(qr_box), qr_box[:2])
    ImageDraw.Draw(snip).rectangle(qr_box, outline="white", width=3)
    frames = [(caption(base, cap[0]), 1600), (caption(snip, cap[0]), 1100),
              (caption(place(base, shots["link"]), cap[1]), 2200),
              (caption(place(base, shots["copied"]), cap[2]), 1800),
              (caption(place(base, shots["wifi"]), cap[3]), 2200),
              (caption(place(base, shots["invoice"]), cap[4]), 2600)]
    small = [f.resize((960, 540), Image.LANCZOS).quantize(colors=160, method=Image.Quantize.MEDIANCUT,
                                                           dither=Image.Dither.NONE) for f, _ in frames]
    path = os.path.join(OUT, f"demo-{lang}.gif")
    small[0].save(path, save_all=True, append_images=small[1:], duration=[d for _, d in frames], loop=0,
                  optimize=True)
    return path


def social_preview(shots):
    """1280×640 para GitHub › Settings › Social preview."""
    img = Image.new("RGB", (1280, 640), "#0f172a")
    d = ImageDraw.Draw(img)
    for y in range(640):
        t = y / 640
        d.line([(0, y), (1280, y)], fill=(int(15 + 25 * t), int(23 + 30 * t), int(42 + 50 * t)))
    logo = make_icon(size=150, dark_bg=True)
    img.paste(logo, (80, 150), logo)
    d.text((80, 320), "ClipQR", font=font(84, True), fill="white")
    d.text((84, 425), "Screenshot a QR code.", font=font(32), fill="#cbd5e1")
    d.text((84, 467), "Use it instantly.", font=font(32), fill="#cbd5e1")
    d.text((84, 530), "Windows · 10 languages · open source", font=font(24), fill="#93c5fd")
    p = shots["invoice"]
    scale = min(560 / p.height, 600 / p.width)
    p = p.resize((int(p.width * scale), int(p.height * scale)), Image.LANCZOS)
    img.paste(p, (1280 - p.width - 50, (640 - p.height) // 2))
    path = os.path.join(ROOT, "build", "social-preview.png")  # se sube a mano en GitHub › Settings
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


if __name__ == "__main__":
    for lang in ("es", "en"):
        shots = capture_popups(lang)
        print(make_gif(lang, shots), os.path.getsize(os.path.join(OUT, f"demo-{lang}.gif")) // 1024, "KB")
    print(social_preview(shots))
