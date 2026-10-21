@echo off
rem Genera dist\ClipQR-Setup.exe: el asistente de instalacion. Lleva dentro ClipQR en modo carpeta
rem (arranca al momento). Tambien genera dist\ClipQR.exe, la version portatil de un solo archivo.
cd /d "%~dp0"
if not defined PY set PY=py
call "%~dp0build.bat" || exit /b 1
for /f %%v in ('%PY% -c "import clipqr; print(clipqr.VERSION)"') do set VERSION=%%v
echo VERSION = "%VERSION%"> installer\_version.py
%PY% -m PyInstaller --noconfirm --windowed --name ClipQR --exclude-module numpy --icon "%~dp0assets\clipqr.ico" ^
  --add-data "%~dp0assets\logo.png;assets" --add-data "%~dp0assets\logo-white.png;assets" ^
  --distpath "%~dp0build\app-dist" --workpath "%~dp0build\app-work" --specpath "%~dp0build" "%~dp0main.py" || exit /b 1
rem zonas horarias de Tcl: Tk no las usa y son ~600 archivos (instalacion mas lenta)
if exist "%~dp0build\app-dist\ClipQR\_internal\_tcl_data\tzdata" rmdir /s /q "%~dp0build\app-dist\ClipQR\_internal\_tcl_data\tzdata"
%PY% -m PyInstaller --noconfirm --onefile --windowed --name ClipQR-Setup --icon "%~dp0assets\clipqr.ico" ^
  --add-data "%~dp0build\app-dist\ClipQR;app" --add-data "%~dp0assets\logo.png;." --add-data "%~dp0assets\logo-white.png;." ^
  --distpath "%~dp0dist" --workpath "%~dp0build\setup-work" --specpath "%~dp0build" "%~dp0installer\setup.py" || exit /b 1
echo.
echo Listo: %~dp0dist\ClipQR-Setup.exe
