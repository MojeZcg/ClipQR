@echo off
rem Genera dist\ClipQR-Setup.exe: el asistente de instalacion, con ClipQR.exe dentro.
cd /d "%~dp0"
call "%~dp0build.bat" || exit /b 1
for /f %%v in ('py -c "import clipqr; print(clipqr.VERSION)"') do set VERSION=%%v
echo VERSION = "%VERSION%"> installer\_version.py
py -m PyInstaller --noconfirm --onefile --windowed --name ClipQR-Setup --icon "%~dp0assets\clipqr.ico" ^
  --add-data "%~dp0dist\ClipQR.exe;." --add-data "%~dp0assets\logo.png;." --add-data "%~dp0assets\logo-white.png;." ^
  --distpath "%~dp0dist" --workpath "%~dp0build\setup-work" --specpath "%~dp0build" "%~dp0installer\setup.py" || exit /b 1
echo.
echo Listo: %~dp0dist\ClipQR-Setup.exe
