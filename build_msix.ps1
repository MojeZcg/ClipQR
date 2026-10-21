<#
.SYNOPSIS
  Genera dist\ClipQR-<version>.msix para la Microsoft Store.

.DESCRIPTION
  1. Compila ClipQR con PyInstaller en modo carpeta (arranca más rápido que el .exe de un solo archivo).
  2. Monta la estructura del paquete: ClipQR\ (programa), Assets\ (iconos) y AppxManifest.xml.
  3. Genera resources.pri (iconos por escala) y empaqueta con makeappx.

  Para la Store, pasa los valores de Partner Center › tu app › Identidad del producto:
    .\build_msix.ps1 -IdentityName "12345MojeZcg.ClipQR" -Publisher "CN=XXXXXXXX-XXXX-..." -PublisherDisplayName "MojeZcg"
  La Store firma el paquete al publicarlo, no hace falta certificado.

  Para probarlo en este equipo sin certificado (requiere el Modo de desarrollador de Windows):
    .\build_msix.ps1 -Register
  Y para quitarlo:
    Get-AppxPackage *ClipQR* | Remove-AppxPackage
#>
param(
  [string]$IdentityName = "MojeZcg.ClipQR",
  [string]$Publisher = "CN=MojeZcg",
  [string]$PublisherDisplayName = "MojeZcg",
  [switch]$Register
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$sdk = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.*\x64" -Directory -ErrorAction SilentlyContinue |
  Sort-Object Name -Descending | Where-Object { Test-Path "$($_.FullName)\makeappx.exe" } | Select-Object -First 1
if (-not $sdk) { throw "No se encontró makeappx.exe. Instala el Windows SDK (https://developer.microsoft.com/windows/downloads/windows-sdk/)." }
$makeappx = "$($sdk.FullName)\makeappx.exe"
$makepri = "$($sdk.FullName)\makepri.exe"

$appVersion = (py -c "import clipqr; print(clipqr.VERSION)").Trim()
$version = "$appVersion.0"  # MSIX exige 4 partes; la última debe ser 0 para la Store
Write-Host "ClipQR $version  ($IdentityName / $Publisher)"

# 1) programa
py -m pip install --user -q -r requirements.txt pyinstaller
py -c "import clipqr; clipqr.make_icon(size=256).save('assets/clipqr.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
py -m PyInstaller --noconfirm --windowed --name ClipQR --icon "$PSScriptRoot\assets\clipqr.ico" `
  --add-data "$PSScriptRoot\assets\logo.png;assets" `
  --distpath build\msix-dist --workpath build\msix-work --specpath build clipqr.py
if ($LASTEXITCODE) { throw "PyInstaller falló" }

# 2) estructura del paquete
$layout = "build\msix-layout"
if (Test-Path $layout) { Remove-Item $layout -Recurse -Force }
New-Item -ItemType Directory -Force $layout | Out-Null
Copy-Item build\msix-dist\ClipQR "$layout\ClipQR" -Recurse
py tools\msix_assets.py "$layout\Assets"
(Get-Content msix\AppxManifest.xml -Raw -Encoding utf8) `
  -replace '\{\{IDENTITY_NAME\}\}', $IdentityName `
  -replace '\{\{PUBLISHER\}\}', [Security.SecurityElement]::Escape($Publisher) `
  -replace '\{\{PUBLISHER_DISPLAY_NAME\}\}', [Security.SecurityElement]::Escape($PublisherDisplayName) `
  -replace '\{\{VERSION\}\}', $version |
  Set-Content "$layout\AppxManifest.xml" -Encoding utf8

# 3) recursos y paquete
& $makepri createconfig /cf build\priconfig.xml /dq es-ES /pv 10.0.0 /o | Out-Null
& $makepri new /pr $layout /cf build\priconfig.xml /mn "$layout\AppxManifest.xml" /of "$layout\resources.pri" /o | Out-Null
if ($LASTEXITCODE) { throw "makepri falló" }

if ($Register) {
  Get-AppxPackage -Name $IdentityName | Remove-AppxPackage
  Add-AppxPackage -Register "$layout\AppxManifest.xml"
  Write-Host "Registrado. Búscalo en el menú Inicio como 'ClipQR'."
}

New-Item -ItemType Directory -Force dist | Out-Null
$out = "dist\ClipQR-$appVersion.msix"
& $makeappx pack /d $layout /p $out /o | Out-Null
if ($LASTEXITCODE) { throw "makeappx falló" }
Write-Host "Listo: $PSScriptRoot\$out"
