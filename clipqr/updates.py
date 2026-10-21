"""Buscar e instalar actualizaciones desde las releases de GitHub.

Solo se conecta a api.github.com y a las descargas de la release, una vez al día y si el usuario no lo
desactiva. El instalador descargado se comprueba con el SHA-256 publicado en SHA256SUMS.txt de la
misma release antes de ejecutarse; si no coincide (o falta), no se instala nada.
"""
import hashlib
import json
import os
import re
import tempfile
import urllib.request

from clipqr import VERSION

REPO = "MojeZcg/ClipQR"
API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"
SETUP_NAME = "ClipQR-Setup.exe"
SUMS_NAME = "SHA256SUMS.txt"
CHECK_EVERY = 24 * 3600  # segundos


def parse_version(text):
    """«v1.2.3» o «1.2.3» -> (1, 2, 3). Lo que no sea número se ignora («1.2.0-beta» -> (1, 2, 0))."""
    nums = re.findall(r"\d+", text.lstrip("vV").split("-")[0])
    return tuple(int(n) for n in nums[:3]) + (0,) * (3 - len(nums[:3]))


def is_newer(latest, current=VERSION):
    return parse_version(latest) > parse_version(current)


def parse_sums(text):
    """Contenido de SHA256SUMS.txt («hash  nombre» por línea) -> {nombre: hash en minúsculas}."""
    sums = {}
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            sums[parts[-1].lstrip("*")] = parts[0].lower()
    return sums


def setup_args(autostart, desktop):
    """Opciones del instalador para actualizar sin preguntar y conservar lo que el usuario tenía."""
    args = ["/silent", "/launch"]
    if not autostart:
        args.append("/noautostart")
    if desktop:
        args.append("/desktop")
    return args


def _get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": f"ClipQR/{VERSION}",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_latest():
    """Última release publicada: {version, page, assets: {nombre: url}}."""
    data = json.loads(_get(API_LATEST))
    return {"version": data["tag_name"].lstrip("vV"), "page": data["html_url"],
            "assets": {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}}


def download_verified(info, folder=None):
    """Descarga el instalador de la release y comprueba su SHA-256. Devuelve la ruta o lanza ValueError."""
    assets = info["assets"]
    if SETUP_NAME not in assets or SUMS_NAME not in assets:
        raise ValueError("La release no incluye el instalador o sus sumas de comprobación.")
    expected = parse_sums(_get(assets[SUMS_NAME]).decode("utf-8", "replace")).get(SETUP_NAME)
    if not expected:
        raise ValueError("SHA256SUMS.txt no tiene la suma del instalador.")
    data = _get(assets[SETUP_NAME], timeout=120)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("El instalador descargado no coincide con su suma SHA-256: no se instala.")
    folder = folder or tempfile.mkdtemp(prefix="clipqr-update-")
    path = os.path.join(folder, SETUP_NAME)
    with open(path, "wb") as f:
        f.write(data)
    return path
