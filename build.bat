@echo off
rem Genera dist\ClipQR.exe (un solo archivo, no necesita Python en la maquina destino).
cd /d "%~dp0"
py -m pip install --user -r requirements.txt pyinstaller || exit /b 1
py -c "import clipqr; clipqr.make_icon(size=256).save('assets/clipqr.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]); clipqr.make_icon(size=512).save('assets/logo.png')" || exit /b 1
py -m PyInstaller --noconfirm --onefile --windowed --name ClipQR --icon assets\clipqr.ico clipqr.py || exit /b 1
echo.
echo Listo: %~dp0dist\ClipQR.exe
