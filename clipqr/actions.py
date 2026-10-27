"""Acciones que se ejecutan al pulsar un botón: Wi-Fi, abrir archivos, buscar la captura guardada."""
import hashlib
import os
import time

from PIL import Image

from clipqr.platform import connect_wifi, current_wifi, open_path, screenshots_folder
from clipqr.platform.common import parse_wifi_profile

__all__ = ["connect_wifi", "current_wifi", "parse_wifi_profile", "find_saved_capture", "open_with_default_app"]


def find_saved_capture(img, since, timeout=5.0):
    """Busca en la carpeta de capturas el archivo de esta captura: creado desde `since` y con
    exactamente los mismos píxeles (así nunca se confunde con otra imagen). Recortes guarda el
    archivo un momento después de copiarla, por eso se reintenta durante `timeout` segundos."""
    folder = screenshots_folder()
    if not folder or not os.path.isdir(folder):
        return None
    want = hashlib.md5(img.convert("RGB").tobytes()).digest()
    checked = set()
    end = time.time() + timeout
    while time.time() < end:
        try:
            entries = [e for e in os.scandir(folder) if e.is_file()
                       and os.path.splitext(e.name)[1].lower() in (".png", ".jpg", ".jpeg")
                       and max(e.stat().st_mtime, e.stat().st_ctime) >= since - 2]  # ctime = creación en Windows
        except OSError:
            entries = []
        for e in entries:
            key = (e.path, e.stat().st_size)
            if key in checked:
                continue
            checked.add(key)
            try:
                with Image.open(e.path) as f:
                    if f.size == img.size and hashlib.md5(f.convert("RGB").tobytes()).digest() == want:
                        return e.path
            except OSError:
                pass  # aún se está escribiendo
        time.sleep(0.15)
    return None

def open_with_default_app(content, ext):
    """Guarda el contenido en un archivo temporal y lo abre con la app predeterminada."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=ext, prefix="clipqr_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    open_path(path)
