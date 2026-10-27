#!/usr/bin/env bash
# Genera dist/ClipQR-Linux-x86_64.tar.gz: ClipQR en modo carpeta (PyInstaller, no necesita Python en la
# máquina destino) + install.sh / uninstall.sh (instalación para el usuario, sin sudo) + icono.
# Usa el Python de la variable PY si existe; si no, python3. Compilar en la distribución más antigua que se
# quiera admitir (glibc): el resultado funciona en esa y en las posteriores.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)  # rutas absolutas: con --specpath, PyInstaller resuelve las relativas desde build/
PY=${PY:-python3}
$PY -m pip install -q -r requirements.txt pyinstaller
# atajos globales (X11): opcional, pynput compila evdev y necesita gcc y las cabeceras del kernel
$PY -m pip install -q pynput || echo "Aviso: no se pudo instalar pynput; el paquete saldrá sin atajos globales"

mkdir -p build dist
$PY -c "from clipqr.icons import make_icon; make_icon(size=256, outline=True).save('build/clipqr.png')"
$PY -m PyInstaller --noconfirm --windowed --name ClipQR --exclude-module numpy \
  --add-data "$ROOT/assets/logo.png:assets" --add-data "$ROOT/assets/logo-white.png:assets" \
  --hidden-import PIL._tkinter_finder --hidden-import pystray._xorg --hidden-import pystray._appindicator --hidden-import pystray._gtk \
  --hidden-import pynput.keyboard._xorg --hidden-import pynput.mouse._xorg \
  --distpath build/linux-dist --workpath build/linux-work --specpath build "$ROOT/main.py"
# zonas horarias de Tcl: Tk no las usa y son ~600 archivos
rm -rf build/linux-dist/ClipQR/_internal/_tcl_data/tzdata

PKG=build/ClipQR-Linux-x86_64
rm -rf "$PKG"
mkdir -p "$PKG"
cp -R build/linux-dist/ClipQR "$PKG/ClipQR"
cp build/clipqr.png packaging/linux/install.sh packaging/linux/uninstall.sh LICENSE "$PKG/"
chmod +x "$PKG/install.sh" "$PKG/uninstall.sh" "$PKG/ClipQR/ClipQR"
tar -C build -czf dist/ClipQR-Linux-x86_64.tar.gz ClipQR-Linux-x86_64
echo
echo "Listo: $(pwd)/dist/ClipQR-Linux-x86_64.tar.gz"
