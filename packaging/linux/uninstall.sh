#!/bin/sh
# Quita ClipQR instalado con install.sh: programa, enlace, lanzador, icono e inicio al iniciar sesión.
# Los ajustes (~/.config/ClipQR) se conservan; con --purge se borran también.
DATA=${XDG_DATA_HOME:-$HOME/.local/share}
CONFIG=${XDG_CONFIG_HOME:-$HOME/.config}
pkill -x ClipQR 2>/dev/null || true
rm -f "$HOME/.local/bin/clipqr" "$DATA/applications/clipqr.desktop" \
      "$DATA/icons/hicolor/256x256/apps/clipqr.png" "$CONFIG/autostart/clipqr.desktop"
rm -rf "$DATA/ClipQR"
if [ "$1" = "--purge" ]; then
  rm -rf "$CONFIG/ClipQR"
fi
echo "ClipQR desinstalado."
