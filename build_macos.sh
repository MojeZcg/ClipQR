#!/usr/bin/env bash
# Genera dist/ClipQR.app y dist/ClipQR-macOS.zip: la app de la barra de menús (sin icono en el Dock), con
# Python incluido. Sale sin firmar con un certificado de Apple (solo firma ad hoc): la primera vez macOS pide
# abrirla con clic derecho › Abrir (o Ajustes del Sistema › Privacidad y seguridad › «Abrir igualmente»).
# Usa el Python de la variable PY si existe; si no, python3. La app es para la arquitectura de ese Python
# (Apple Silicon en los runners macos-latest de GitHub).
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)  # rutas absolutas: con --specpath, PyInstaller resuelve las relativas desde build/
PY=${PY:-python3}
$PY -m pip install -q -r requirements.txt pyinstaller

mkdir -p build dist
VERSION=$($PY -c "import clipqr; print(clipqr.VERSION)")
$PY -c "from clipqr.icons import make_icon; make_icon(size=1024, outline=True).save('build/clipqr-mac.png')"
$PY -m PyInstaller --noconfirm --windowed --name ClipQR --exclude-module numpy \
  --osx-bundle-identifier io.github.mojezcg.clipqr --icon "$ROOT/build/clipqr-mac.png" \
  --add-data "$ROOT/assets/logo.png:assets" --add-data "$ROOT/assets/logo-white.png:assets" \
  --hidden-import PIL._tkinter_finder --hidden-import pystray._darwin --hidden-import pynput.keyboard._darwin --hidden-import pynput.mouse._darwin \
  --distpath dist --workpath build/mac-work --specpath build "$ROOT/main.py"

APP=dist/ClipQR.app
PLIST=$APP/Contents/Info.plist
pb() { /usr/libexec/PlistBuddy -c "$1" "$PLIST"; }
# LSUIElement: vive en la barra de menús, sin icono en el Dock ni en Cmd+Tab
pb "Delete :LSUIElement" 2>/dev/null || true
pb "Add :LSUIElement bool true"
# Delete + Add: «Set» falla si la clave no existe (PyInstaller no siempre escribe CFBundleVersion)
pb "Delete :CFBundleShortVersionString" 2>/dev/null || true
pb "Add :CFBundleShortVersionString string $VERSION"
pb "Delete :CFBundleVersion" 2>/dev/null || true
pb "Add :CFBundleVersion string $VERSION"
pb "Delete :NSAppleEventsUsageDescription" 2>/dev/null || true
pb "Add :NSAppleEventsUsageDescription string ClipQR uses AppleScript to read images from the clipboard and move screenshots to the Trash."
pb "Delete :LSMinimumSystemVersion" 2>/dev/null || true
pb "Add :LSMinimumSystemVersion string 11.0"
# cambiar Info.plist invalida la firma ad hoc de PyInstaller: se vuelve a firmar
codesign --force --deep --sign - "$APP"

rm -f dist/ClipQR-macOS.zip
ditto -c -k --keepParent "$APP" dist/ClipQR-macOS.zip
echo
echo "Listo: $(pwd)/dist/ClipQR-macOS.zip"
