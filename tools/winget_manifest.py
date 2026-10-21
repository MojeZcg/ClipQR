"""Genera los manifiestos de winget (formato 1.6.0) de una versión de ClipQR.

    py tools/winget_manifest.py <versión> <ruta a ClipQR-Setup.exe> [carpeta de salida]

Crea winget/manifests/m/MojeZcg/ClipQR/<versión>/ con los tres archivos que pide
microsoft/winget-pkgs (version, installer, defaultLocale). El instalador se descarga desde
la release de GitHub de esa versión; su SHA-256 se calcula del archivo local.
"""
import hashlib
import os
import sys

ID = "MojeZcg.ClipQR"
REPO = "https://github.com/MojeZcg/ClipQR"
MANIFEST_VERSION = "1.6.0"
LOCALE = "es-ES"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def manifests(version, installer_sha256):
    url = f"{REPO}/releases/download/v{version}/ClipQR-Setup.exe"
    head = f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.{{}}.{MANIFEST_VERSION}.schema.json\n\n"
    return {
        f"{ID}.yaml": head.format("version") + f"""PackageIdentifier: {ID}
PackageVersion: {version}
DefaultLocale: {LOCALE}
ManifestType: version
ManifestVersion: {MANIFEST_VERSION}
""",
        f"{ID}.installer.yaml": head.format("installer") + f"""PackageIdentifier: {ID}
PackageVersion: {version}
InstallerType: exe
Scope: user
InstallModes:
- interactive
- silent
- silentWithProgress
InstallerSwitches:
  Silent: /silent
  SilentWithProgress: /silent
UpgradeBehavior: install
AppsAndFeaturesEntries:
- DisplayName: ClipQR
  Publisher: MojeZcg
  DisplayVersion: {version}
Installers:
- Architecture: x64
  InstallerUrl: {url}
  InstallerSha256: {installer_sha256}
ManifestType: installer
ManifestVersion: {MANIFEST_VERSION}
""",
        f"{ID}.locale.{LOCALE}.yaml": head.format("defaultLocale") + f"""PackageIdentifier: {ID}
PackageVersion: {version}
PackageLocale: {LOCALE}
Publisher: MojeZcg
PublisherUrl: https://github.com/MojeZcg
PublisherSupportUrl: {REPO}/issues
PrivacyUrl: {REPO}/blob/main/PRIVACY.md
PackageName: ClipQR
PackageUrl: {REPO}
License: MIT
LicenseUrl: {REPO}/blob/main/LICENSE
ShortDescription: Haz una captura de un QR y úsalo al instante.
Description: |-
  ClipQR detecta códigos QR y de barras en lo que copias o capturas en Windows y muestra un aviso para
  copiar cada dato o usar botones de acción: conectarse al Wi-Fi, guardar el contacto, abrir el enlace…
  Nada se ejecuta sin que lo pulses y todo se procesa en tu equipo.
Moniker: clipqr
Tags:
- qr
- qr-code
- barcode
- clipboard
- screenshot
- scanner
ReleaseNotesUrl: {REPO}/releases/tag/v{version}
ManifestType: defaultLocale
ManifestVersion: {MANIFEST_VERSION}
""",
    }


def write(version, installer_path, out_root="winget"):
    folder = os.path.join(out_root, "manifests", "m", "MojeZcg", "ClipQR", version)
    os.makedirs(folder, exist_ok=True)
    for name, text in manifests(version, sha256(installer_path)).items():
        with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return folder


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    print(write(sys.argv[1], sys.argv[2], *sys.argv[3:4]))
