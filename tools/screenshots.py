"""Genera las capturas de presentación en docs/screenshots/ (para el README de GitHub).

    py tools/screenshots.py

Monta un fondo a pantalla completa, abre encima las ventanas reales de ClipQR con datos
de ejemplo (nada personal) y captura cada escena. Cierra ClipQR antes de ejecutarlo.
"""
import ctypes
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
ctypes.windll.shcore.SetProcessDpiAwareness(1)

import tkinter as tk  # noqa: E402

import zxingcpp  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageGrab, ImageTk  # noqa: E402

import clipqr  # noqa: E402

OUT = os.path.join(ROOT, "docs", "screenshots")
FONTS = r"C:\Windows\Fonts"

SAMPLES = [
    ("QRCode", "WIFI:T:WPA;S:Cafeteria Central;P:cafe-con-leche-2026;;"),
    ("QRCode", "https://github.com/topics/qr-code"),
    ("QRCode", "BEGIN:VCARD\nVERSION:3.0\nFN:Ana Pérez\nORG:Estudio Norte\nTEL:+34 600 111 222\n"
               "EMAIL:ana@example.com\nURL:example.com\nEND:VCARD"),
    ("QRCode", "BEGIN:VEVENT\nSUMMARY:Presentación del proyecto\nDTSTART:20261105T100000\n"
               "LOCATION:Sala 2\nEND:VEVENT"),
    ("QRCode", "geo:40.4168,-3.7038"),
    ("EAN13", "8410000810004"),
    ("QRCode", "mailto:hola@example.com?subject=Hola"),
]


class FakeTray:
    icon = title = None

    def run_detached(self):
        pass

    def update_menu(self):
        pass

    def stop(self):
        pass


def qr_image(fmt, text):
    f = zxingcpp.BarcodeFormat.EAN13 if fmt == "EAN13" else zxingcpp.BarcodeFormat.QRCode
    bc = zxingcpp.create_barcode(text, f)
    img = bc.to_image(scale=6)
    return Image.fromarray(__import__("numpy").array(img)).convert("RGB")


def code(fmt, text, minutes_ago=0):
    return {"format": fmt, "text": text, "thumb": clipqr.make_thumb(qr_image(fmt, text), None),
            "time": time.time() - minutes_ago * 60}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def backdrop(w, h, hero=False):
    """Fondo con degradado oscuro y manchas de color; en la escena principal, logo y textos."""
    img = Image.linear_gradient("L").resize((w, h)).rotate(0)
    base = Image.composite(Image.new("RGB", (w, h), (24, 20, 48)), Image.new("RGB", (w, h), (12, 16, 32)), img)
    blobs = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(blobs)
    d.ellipse((int(w * .55), int(-h * .25), int(w * 1.15), int(h * .55)), fill=(60, 90, 220))
    d.ellipse((int(-w * .15), int(h * .55), int(w * .45), int(h * 1.3)), fill=(120, 60, 200))
    blobs = blobs.filter(ImageFilter.GaussianBlur(h // 5))
    base = Image.blend(base, Image.composite(blobs, base, blobs.convert("L")), .55)
    if hero:
        d = ImageDraw.Draw(base)
        s = h / 1080
        x, y = int(130 * s), int(300 * s)
        logo = clipqr.make_icon(size=int(150 * s), dark_bg=True)
        base.paste(logo, (x, y), logo)
        d.text((x, y + int(165 * s)), "ClipQR", font=font("segoeuib.ttf", int(96 * s)), fill="white")
        d.text((x + int(4 * s), y + int(290 * s)), "Haz una captura de un QR y úsalo al instante.",
               font=font("segoeui.ttf", int(34 * s)), fill=(205, 212, 235))
        feats = ["Detecta QR y códigos de barras en el portapapeles",
                 "Conecta al Wi-Fi, guarda contactos, abre enlaces",
                 "Copia cualquier dato con un clic · nada se ejecuta solo",
                 "Un solo .exe para Windows, sin instalar nada"]
        fy = y + int(370 * s)
        for f in feats:
            d.ellipse((x + int(6 * s), fy + int(15 * s), x + int(16 * s), fy + int(25 * s)), fill=(125, 249, 255))
            d.text((x + int(34 * s), fy), f, font=font("segoeui.ttf", int(26 * s)), fill=(225, 230, 245))
            fy += int(46 * s)
    return base


class Stage:
    def __init__(self):
        clipqr.ClipQR._build_tray = lambda self: FakeTray()
        clipqr.ClipQR.first_run = lambda self: None
        clipqr.ClipQR.save_settings = lambda self: None
        clipqr.ClipQR.autostart_enabled = lambda self: True
        self.app = clipqr.ClipQR()
        self.app.settings = dict(clipqr.DEFAULT_SETTINGS, animation=False, autoclose=False, theme="dark")
        self.root = self.app.root
        self.W, self.H = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.bg = tk.Toplevel(self.root)
        self.bg.overrideredirect(True)
        self.bg.geometry(f"{self.W}x{self.H}+0+0")
        self.bg.attributes("-topmost", True)
        self.bg_label = tk.Label(self.bg, bd=0)
        self.bg_label.pack()
        os.makedirs(OUT, exist_ok=True)

    def set_backdrop(self, hero=False):
        self._bg_photo = ImageTk.PhotoImage(backdrop(self.W, self.H, hero))
        self.bg_label.config(image=self._bg_photo)
        self.settle()

    def settle(self, seconds=0.6):
        end = time.time() + seconds
        while time.time() < end:
            self.root.update()
            time.sleep(0.02)

    def grab(self, name, box):
        x0, y0, x1, y1 = (int(v) for v in box)
        img = ImageGrab.grab(bbox=(max(0, x0), max(0, y0), min(self.W, x1), min(self.H, y1)))
        img.save(os.path.join(OUT, name), optimize=True)
        print("  ", name, img.size)

    def grab_window(self, name, win, margin=56):
        win.update_idletasks()
        x, y = win.winfo_rootx(), win.winfo_rooty()
        w, h = win.winfo_width(), win.winfo_height()
        if not win.overrideredirect():  # incluir la barra de título del sistema
            hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
            r = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))
            x, y, w, h = r.left, r.top, r.right - r.left, r.bottom - r.top
        self.grab(name, (x - margin, y - margin, x + w + margin, y + h + margin))

    def popup(self, codes, x, y, theme="dark"):
        self.app.settings.update(position="custom", x=x, y=y, theme=theme)
        self.app.show_popup(codes)
        self.settle()
        return self.app.popup

    def window(self, opener, x, y, w, h, theme="dark"):
        self.app.settings.update(theme=theme)
        opener()
        win = self.app.settings_win if opener == self.app.show_settings else self.app.history_win
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.attributes("-topmost", True)
        win.lift()
        self.settle(0.8)
        return win


def main():
    st = Stage()
    app, W, H = st.app, st.W, st.H
    wifi, link, contact, event, geo, ean, mail = [code(f, t, i * 7) for i, (f, t) in enumerate(SAMPLES)]

    print("Escena principal")
    st.set_backdrop(hero=True)
    pop = st.popup([wifi, link], 0, 0)
    pop.update_idletasks()
    st.popup([wifi, link], int(W * .60), (H - pop.winfo_height()) // 2)
    st.grab("hero.png", (0, 0, W, H))
    app._close_popup()

    st.set_backdrop()
    for name, codes in (("popup-wifi.png", [wifi]), ("popup-contact.png", [contact]),
                        ("popup-event.png", [event]), ("popup-multi.png", [link, ean])):
        st.grab_window(name, st.popup(codes, W // 3, H // 6))
        app._close_popup()
    st.grab_window("popup-light.png", st.popup([contact], W // 3, H // 6, theme="light"))
    app._close_popup()

    app.history = [[c] for c in (wifi, link, contact, event, geo, ean, mail)]
    win = st.window(app.show_history, W // 3, H // 10, app.px(520), app.px(640))
    st.grab_window("history.png", win)
    win.destroy()

    app.settings = dict(clipqr.DEFAULT_SETTINGS)  # la configuración se muestra con los valores por defecto
    for theme in ("dark", "light"):
        win = st.window(app.show_settings, W // 3, H // 14, app.px(500), app.px(700), theme=theme)
        st.grab_window(f"settings-{theme}.png", win)
        win.destroy()

    st.root.destroy()
    print("Listo:", OUT)


if __name__ == "__main__":
    main()
