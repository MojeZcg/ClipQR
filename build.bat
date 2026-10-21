@echo off
rem Genera dist\ClipQR.exe (un solo archivo, no necesita Python en la maquina destino).
rem Usa el Python de la variable PY si existe (en GitHub Actions: python); si no, el lanzador py.
cd /d "%~dp0"
if not defined PY set PY=py
%PY% -m pip install -q -r requirements.txt pyinstaller || exit /b 1
%PY% -c "from clipqr.icons import make_icon; make_icon(size=256, outline=True).save('assets/clipqr.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])" || exit /b 1
%PY% -m PyInstaller --noconfirm --onefile --windowed --name ClipQR --exclude-module numpy --icon assets\clipqr.ico --add-data "assets\logo.png;assets" --add-data "assets\logo-white.png;assets" main.py || exit /b 1
echo.
echo Listo: %~dp0dist\ClipQR.exe
