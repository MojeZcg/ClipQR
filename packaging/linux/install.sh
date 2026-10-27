#!/bin/sh
# Instala ClipQR para el usuario actual (sin sudo):
#   ~/.local/share/ClipQR          el programa
#   ~/.local/bin/clipqr            enlace para abrirlo desde la terminal
#   ~/.local/share/applications    lanzador en el menú de aplicaciones (con su icono)
# Para quitarlo: ./uninstall.sh (o ~/.local/share/ClipQR/uninstall.sh).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
DATA=${XDG_DATA_HOME:-$HOME/.local/share}
DEST=$DATA/ClipQR
BIN=$HOME/.local/bin
ICONS=$DATA/icons/hicolor/256x256/apps

# si está abierto, se cierra antes de reemplazarlo
pkill -x ClipQR 2>/dev/null || true

rm -rf "$DEST"
mkdir -p "$DEST" "$BIN" "$DATA/applications" "$ICONS"
cp -R "$HERE/ClipQR/." "$DEST/"
cp "$HERE/uninstall.sh" "$DEST/uninstall.sh"
cp "$HERE/clipqr.png" "$ICONS/clipqr.png"
chmod +x "$DEST/ClipQR" "$DEST/uninstall.sh"
ln -sf "$DEST/ClipQR" "$BIN/clipqr"

cat > "$DATA/applications/clipqr.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=ClipQR
Comment=QR codes from your clipboard
Comment[es]=Códigos QR del portapapeles
Exec="$DEST/ClipQR"
Icon=clipqr
Terminal=false
Categories=Utility;
StartupNotify=false
DESKTOP

if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$DATA/applications" || true; fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q "$DATA/icons/hicolor" || true; fi

echo "ClipQR instalado en $DEST"
case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "Nota: $BIN no está en el PATH; ábrelo desde el menú de aplicaciones o con $DEST/ClipQR" ;;
esac
if [ -z "$WAYLAND_DISPLAY" ] && ! command -v xclip >/dev/null 2>&1; then
  echo "Aviso: instala xclip para leer el portapapeles (por ejemplo: sudo apt install xclip)"
fi
if [ -n "$WAYLAND_DISPLAY" ] && ! command -v wl-paste >/dev/null 2>&1; then
  echo "Aviso: instala wl-clipboard para leer el portapapeles (por ejemplo: sudo apt install wl-clipboard)"
fi
if [ "$1" != "--no-launch" ]; then
  nohup "$DEST/ClipQR" >/dev/null 2>&1 &
fi
