"""Escanear una zona de la pantalla: congela la pantalla, se arrastra un rectángulo y se lee lo que hay
dentro. No pasa por el portapapeles ni guarda ningún archivo."""
import tkinter as tk

from PIL import Image, ImageEnhance, ImageTk

from clipqr.i18n import _
from clipqr.platform import SYSTEM, bring_to_front, grab_screen, monitor_area, virtual_screen, work_area
from clipqr.ui.theme import KINDS

MIN_DRAG = 8  # px: menos que esto es un clic (escanea el monitor entero)


def selection_box(x0, y0, x1, y1, min_size=MIN_DRAG):
    """Rectángulo normalizado (izq, arr, der, ab) o None si es un clic sin arrastrar."""
    left, right = sorted((x0, x1))
    top, bottom = sorted((y0, y1))
    if right - left < min_size or bottom - top < min_size:
        return None
    return left, top, right, bottom


def to_image_box(box, origin, scale=1):
    """Coordenadas de pantalla -> coordenadas de la imagen de todo el escritorio (que empieza en origin).
    `scale`: píxeles de la captura por punto de pantalla (2 en una pantalla Retina de macOS)."""
    ox, oy = origin
    box = box[0] - ox, box[1] - oy, box[2] - ox, box[3] - oy
    return box if scale == 1 else tuple(round(v * scale) for v in box)


class RegionMixin:
    def scan_region(self):
        if getattr(self, "_region_win", None) is not None and self._region_win.winfo_exists():
            return
        self._close_popup()
        vs = virtual_screen()
        try:
            shot = grab_screen()
        except Exception as e:
            if SYSTEM == "linux":
                self.toast(_("No se pudo capturar la pantalla.\nEn Wayland las aplicaciones no pueden capturarla: "
                             "haz una captura con la herramienta del sistema y cópiala."), seconds=8)
            else:
                self.toast(_("No se pudo capturar la pantalla.\n{error}", error=e), seconds=8)
            return
        dim = ImageEnhance.Brightness(shot).enhance(0.45)
        # en macOS la captura viene en píxeles y Tk trabaja en puntos (Retina: 2 píxeles por punto)
        scale = shot.width / max(1, vs.right - vs.left)
        if abs(scale - 1) > 0.01:
            dim = dim.resize((vs.right - vs.left, vs.bottom - vs.top), Image.LANCZOS)
        else:
            scale = 1

        win = tk.Toplevel(self.root)
        self._region_win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.geometry(f"{vs.right - vs.left}x{vs.bottom - vs.top}+{vs.left}+{vs.top}")
        cv = tk.Canvas(win, highlightthickness=0, bd=0, cursor="crosshair")
        cv.pack(fill="both", expand=True)
        photo = ImageTk.PhotoImage(dim)
        cv.create_image(0, 0, image=photo, anchor="nw")
        win._photo = photo  # que Tk no la libere

        # instrucciones arriba, en el monitor donde está el ratón
        area = work_area()
        cx, ty = (area.left + area.right) // 2 - vs.left, area.top - vs.top + self.px(28)
        text = _("Arrastra alrededor del código  ·  Clic: toda la pantalla  ·  Esc: cancelar")
        label = cv.create_text(cx, ty, text=text, fill="white", font=self.font(12, "bold"))
        x0, y0, x1, y1 = cv.bbox(label)
        pad = self.px(10)
        bg = cv.create_rectangle(x0 - pad, y0 - pad // 2, x1 + pad, y1 + pad // 2, fill="#202020", outline="")
        cv.tag_raise(label, bg)

        accent = KINDS["link"][2]
        drag = {}

        def press(e):
            drag.update(x=e.x, y=e.y)
            cv.delete("sel")

        def motion(e):
            if not drag:
                return
            cv.delete("sel")
            cv.create_rectangle(drag["x"], drag["y"], e.x, e.y, outline=accent, width=2,
                                fill="white", stipple="gray12", tags="sel")

        def release(e):
            if not drag:
                return
            box = selection_box(drag["x"], drag["y"], e.x, e.y)
            if box is None:  # clic: el monitor entero
                m = monitor_area((e.x + vs.left, e.y + vs.top))
                box = to_image_box(m, (vs.left, vs.top), scale)
            elif scale != 1:
                box = tuple(round(v * scale) for v in box)
            close()
            self.decode_and_show([shot.crop(box)], force=True)

        def close(e=None):
            self._region_win = None
            win.destroy()

        cv.bind("<ButtonPress-1>", press)
        cv.bind("<B1-Motion>", motion)
        cv.bind("<ButtonRelease-1>", release)
        cv.bind("<ButtonPress-3>", close)
        win.bind("<Escape>", close)
        win.update_idletasks()
        bring_to_front(win)
        win.focus_force()
