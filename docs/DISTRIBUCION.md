# Distribución de ClipQR

Cómo llevar ClipQR a la gente con la menor fricción posible. Orden recomendado:

1. [Compilación y releases automáticas (GitHub Actions)](#1-compilación-y-releases-automáticas-github-actions): ahorra trabajo en todo lo demás.
2. [Tests automáticos](#2-tests-automáticos): para publicar sin miedo a romper nada.
3. [Firma de código](#3-firma-de-código): quita (o reduce) el aviso de SmartScreen.
4. [winget](#4-winget): `winget install ClipQR`.
5. [Microsoft Store](#5-microsoft-store).

> Las condiciones de servicios externos (precios, países admitidos, requisitos) cambian con frecuencia.
> Antes de pagar o registrarte en algo, compruébalas en la página oficial enlazada.

---

## 1. Compilación y releases automáticas (GitHub Actions)

**Objetivo:** al crear una etiqueta `v1.x.y` y subirla, GitHub compila `ClipQR.exe`, `ClipQR-Setup.exe` y `ClipQR-x.y.z.msix` en una máquina Windows limpia y publica la release con sus sumas SHA-256. Nada se compila en tu PC.

Los runners `windows-latest` de GitHub ya traen Python, el Windows SDK (`makeappx`, `makepri`, `signtool`) y PowerShell.

Archivo `.github/workflows/release.yml` (lo añade el PR 1.0.2 de la [hoja de ruta](ROADMAP.md)):

```yaml
name: Release
on:
  push:
    tags: ["v*"]

permissions:
  contents: write   # para crear la release

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - name: Dependencias
        run: py -m pip install -r requirements.txt pyinstaller pytest
      - name: Tests
        run: py -m pytest -q
      - name: Comprobar que la etiqueta coincide con VERSION
        shell: pwsh
        run: |
          $v = (py -c "import clipqr; print(clipqr.VERSION)").Trim()
          if ("v$v" -ne "${{ github.ref_name }}") { throw "VERSION=$v no coincide con ${{ github.ref_name }}" }
      - name: Compilar exe portátil e instalador
        run: cmd /c build_setup.bat
      - name: Compilar MSIX
        shell: pwsh
        run: ./build_msix.ps1 -IdentityName "${{ vars.MSIX_IDENTITY_NAME }}" -Publisher "${{ vars.MSIX_PUBLISHER }}" -PublisherDisplayName "MojeZcg"
      - name: Sumas SHA-256
        shell: pwsh
        run: Get-FileHash dist/*.exe, dist/*.msix -Algorithm SHA256 | ForEach-Object { "$($_.Hash.ToLower())  $(Split-Path $_.Path -Leaf)" } | Set-Content dist/SHA256SUMS.txt
      - name: Publicar release
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release create ${{ github.ref_name }} dist/ClipQR-Setup.exe dist/ClipQR.exe dist/*.msix dist/SHA256SUMS.txt --title "ClipQR ${{ github.ref_name }}" --notes-file docs/release-notes/${{ github.ref_name }}.md
```

**Qué tienes que hacer tú una vez:**
- En GitHub › *Settings › Secrets and variables › Actions › Variables*, crea `MSIX_IDENTITY_NAME` y `MSIX_PUBLISHER` con los valores de Partner Center (paso 5). Hasta tenerlos, quita el paso «Compilar MSIX».

**Cómo publicar una versión a partir de entonces:**
1. Sube `VERSION` en `clipqr/__init__.py` (por ejemplo `1.1.0`).
2. Escribe las notas en `docs/release-notes/v1.1.0.md`.
3. Haz commit, y luego:
   ```bash
   git tag v1.1.0
   git push origin main v1.1.0
   ```
4. En unos minutos la release está publicada. Su progreso se ve en la pestaña *Actions* del repo.

---

## 2. Tests automáticos

**Objetivo:** que cada cambio se compruebe solo antes de unirse a `main`.

- `pytest` con imágenes de ejemplo generadas por código (QR de Wi‑Fi, vCard, MeCard, evento, enlace, EAN…) y las imágenes reales difíciles que ya han fallado alguna vez (la foto borrosa de un QR impreso).
- Un segundo workflow, `.github/workflows/tests.yml`, ejecuta los tests en cada PR (`on: pull_request`).
- En GitHub › *Settings › Branches*, añade una regla para `main`: *Require status checks to pass* → `tests`. Así no se puede unir un PR que rompa algo.

Detalle en el PR 1.0.1 de la [hoja de ruta](ROADMAP.md).

---

## 3. Firma de código

**Por qué:** sin firma, Windows SmartScreen muestra «Windows protegió su PC» y mucha gente no se atreve a seguir. Firmar demuestra quién publica el programa y que nadie lo ha modificado.

**Qué esperar:** desde 2024 ningún certificado (tampoco los EV) quita el aviso al instante. La reputación se gana con descargas firmadas por la misma identidad, pero con firma el aviso desaparece mucho antes y muestra tu nombre como editor.

### Opciones

| Opción | Coste aprox. | Para quién | Notas |
|---|---|---|---|
| [SignPath Foundation](https://signpath.org) | Gratis | Proyectos de código abierto | Firma desde GitHub Actions. Hay que solicitarlo y cumplir sus requisitos (licencia OSI, como MIT, compilación reproducible en CI). **La más recomendable para ClipQR.** |
| [Azure Trusted Signing](https://learn.microsoft.com/azure/trusted-signing/) | ~10 USD/mes | Empresas y, en algunos países, particulares | Integración oficial con GitHub Actions (`azure/trusted-signing-action`). Comprueba si está disponible para particulares en tu país. |
| Certificado OV clásico (Certum Open Source, Sectigo…) | 30–300 €/año | Cualquiera | Certum tiene un certificado barato para desarrolladores de código abierto. La clave va en una tarjeta física o en su nube (SimplySign); es más incómodo de usar en CI. |

### Cómo integrarlo
1. Consigue el método de firma (por ejemplo, solicita SignPath con el repo público y el workflow del paso 1 ya funcionando).
2. Añade al workflow un paso **después de compilar y antes de publicar** que firme `ClipQR.exe`, el `ClipQR.exe` de la carpeta del instalador (`build/app-dist/ClipQR/ClipQR.exe`, *antes* de empaquetar el instalador) y `ClipQR-Setup.exe`.
3. Comprueba la firma con:
   ```bash
   signtool verify /pa /v dist\ClipQR-Setup.exe
   ```
4. El paquete MSIX **no** hace falta firmarlo: la Microsoft Store lo firma al publicarlo.

---

## 4. winget

**Objetivo:** que se pueda instalar con:

```bash
winget install MojeZcg.ClipQR
```

y actualizar con `winget upgrade`.

**Ya está hecho:**
- El instalador acepta `/silent` (PR 1.0.3).
- Cada release genera los tres manifiestos con `tools/winget_manifest.py`, validados con `winget validate`. Están en el artefacto del workflow, carpeta `winget/`.
- El workflow ya tiene el paso **«Enviar a winget»**, que abre el PR en [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs) con `wingetcreate submit`.

**Lo que tienes que hacer tú (una vez):**
1. En GitHub › *Settings (de tu cuenta) › Developer settings › Personal access tokens › Tokens (classic)*, crea un token con el permiso `public_repo`.
2. En el repo de ClipQR › *Settings › Secrets and variables › Actions › Secrets*, guárdalo como `WINGET_TOKEN`.

Desde la siguiente release, cada versión se envía sola. Microsoft revisa el PR automáticamente y luego lo revisa una persona; suele tardar de unas horas a pocos días.

**Envío manual** (si prefieres no guardar el token), con los manifiestos del artefacto:

```bash
winget install Microsoft.WingetCreate
```

```bash
wingetcreate submit --token <tu token> winget\manifests\m\MojeZcg\ClipQR\<versión>
```

Con firma de código (paso 3), las validaciones automáticas de winget dan menos problemas.

---

## 5. Microsoft Store

Todo lo técnico está hecho: `build_msix.ps1`, el manifiesto en `msix/` y los textos de la ficha en [store-listing.md](store-listing.md).

1. Crea la cuenta de desarrollador en [Partner Center](https://partner.microsoft.com/dashboard) como particular.
2. *Apps y juegos › Nueva aplicación* y reserva el nombre **ClipQR**.
3. En *Administración de productos › Identidad del producto*, copia `Package/Identity/Name`, `Package/Identity/Publisher` y `PublisherDisplayName`.
4. Compila con esos valores (o guárdalos como variables del workflow, paso 1):
   ```powershell
   .\build_msix.ps1 -IdentityName "<Name>" -Publisher "<Publisher>" -PublisherDisplayName "<PublisherDisplayName>"
   ```
5. Antes de enviarlo, pásale el **Windows App Certification Kit**, que viene con el Windows SDK. Detecta casi todo lo que haría rechazar el paquete:
   ```powershell
   & "${env:ProgramFiles(x86)}\Windows Kits\10\App Certification Kit\appcert.exe" test -appxpackagepath dist\ClipQR-1.1.0.msix -reportoutputpath build\wack.xml
   ```
6. En el envío:
   - **Paquetes:** sube el `.msix`.
   - **Propiedades:** categoría *Utilidades y herramientas* y política de privacidad `https://github.com/MojeZcg/ClipQR/blob/main/PRIVACY.md`.
   - **Clasificación por edades:** cuestionario IARC.
   - **Listados de Store:** copia los textos de [store-listing.md](store-listing.md). Las capturas tienen que ser de al menos 1366×768.
   - **Capacidad restringida `runFullTrust`:** pega la justificación de store-listing.md.
7. Envía a certificación. Si lo rechazan, el informe dice exactamente qué corregir.

**El `.msix` en cada release:** con las variables `MSIX_IDENTITY_NAME` y `MSIX_PUBLISHER` del repositorio (ya configuradas), cada etiqueta `vX.Y.Z` compila el `.msix` y lo adjunta a la release. Si falta, la release falla.

**Versiones siguientes, automáticas.** Después de la primera entrega manual, el workflow puede enviar cada versión a la Store:
1. En Partner Center: *Configuración de la cuenta › Administración de usuarios › Aplicaciones de Microsoft Entra*. Crea o asocia una aplicación con el rol **Administrador** y genera una **clave** (client secret).
2. Apunta cuatro valores:
   - el **ID de inquilino** (tenant ID);
   - el **ID de cliente** de esa aplicación (client ID);
   - la **clave** (client secret);
   - el **ID de vendedor** (*Configuración de la cuenta › Información legal › Seller ID*).
3. Guárdalos como secrets, y el ID de la app en la Store (*Identidad del producto › ID de la Store*, p. ej. `9N…`) como variable:
   ```bash
   gh secret set MSSTORE_TENANT_ID
   ```
   ```bash
   gh secret set MSSTORE_SELLER_ID
   ```
   ```bash
   gh secret set MSSTORE_CLIENT_ID
   ```
   ```bash
   gh secret set MSSTORE_CLIENT_SECRET
   ```
   ```bash
   gh variable set MSSTORE_PRODUCT_ID --body "9N…"
   ```
4. Desde entonces, el trabajo `store` de `release.yml` sube el `.msix` de cada release como una entrega nueva, con la [CLI de la Microsoft Store](https://learn.microsoft.com/windows/apps/publish/msstore-dev-cli/overview) (`msstore publish`). La certificación de Microsoft sigue siendo manual por su parte (suele tardar de horas a unos días). Si cambias la ficha o las capturas, hazlo en Partner Center.

La versión del MSIX tiene que ser mayor que la anterior (`build_msix.ps1` la toma de `VERSION`).
