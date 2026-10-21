"""Escanear una zona de la pantalla: congela la pantalla, se arrastra un rectángulo y se lee lo que hay
dentro. No pasa por el portapapeles ni guarda ningún archivo."""
import tkinter as tk

from PIL import ImageEnhance, ImageGrab, ImageTk

from clipqr.ui.theme import KINDS
from clipqr.winplatform import force_foreground, monitor_area, user32, virtual_screen, work_area

MIN_DRAG = 8  # px: menos que esto es un clic (escanea el monitor entero)


def selection_box(x0, y0, x1, y1, min_size=MIN_DRAG):
    """Rectángulo normalizado (izq, arr, der, ab) o None si es un clic sin arrastrar."""
    left, right = sorted((x0, x1))
    top, bottom = sorted((y0, y1))
    if right - left < min_size or bottom - top < min_size:
        return None
    return left, top, right, bottom


def to_image_box(box, origin):
    """Coordenadas de pantalla -> coordenadas de la imagen de todo el escritorio (que empieza en origin)."""
    ox, oy = origin
    return box[0] - ox, box[1] - oy, box[2] - ox, box[3] - oy


class RegionMixin:
    def scan_region(self):
        if getattr(self, "_region_win", None) is not None and self._region_win.winfo_exists():
            return
        self._close_popup()
        vs = virtual_screen()
        shot = ImageGrab.grab(all_screens=True)
        dim = ImageEnhance.Brightness(shot).enhance(0.45)

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
        text = "Arrastra alrededor del código  ·  Clic: toda la pantalla  ·  Esc: cancelar"
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
                box = to_image_box(m, (vs.left, vs.top))
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
        force_foreground(user32.GetParent(win.winfo_id()))
        win.focus_force()
