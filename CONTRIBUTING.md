<p align="center"><b>Español</b> · <a href="#english">English</a></p>

# Contribuir a ClipQR

¡Gracias por querer ayudar! ClipQR es un proyecto pequeño, y cualquier aporte se nota: un idioma, el formato de factura de tu país, un error o una idea.

## Formas de ayudar

- **Avisar de un error:** abre una [incidencia](https://github.com/MojeZcg/ClipQR/issues/new/choose). Pega el informe de **Configuración › Informe de errores**: no incluye tus códigos ni tus imágenes.
- **Un QR que no se lee o se interpreta mal:** adjunta el QR **anonimizado**. Es lo más útil para facturas y pagos reales, porque los formatos se probaron con los ejemplos oficiales.
- **Traducir:** ver [Añadir o mejorar un idioma](#añadir-o-mejorar-un-idioma).
- **Un formato nuevo** (factura, pago, documento de tu país): ver [Añadir un formato](#añadir-un-formato).
- **Código:** las incidencias con la etiqueta [`good first issue`](https://github.com/MojeZcg/ClipQR/labels/good%20first%20issue) están pensadas para empezar.

## Preparar el entorno

```bash
git clone https://github.com/MojeZcg/ClipQR.git
cd ClipQR
py -m pip install -r requirements.txt pytest pyflakes
py main.py          # la app (ciérrala si ya tienes ClipQR instalado y abierto)
py -m pytest -q     # tests
py -m pyflakes clipqr installer tests tools
```

`build.bat` compila `dist\ClipQR.exe` y `build_setup.bat` compila el instalador. Antes de proponer un cambio grande, prueba también el `.exe` compilado: algunos fallos solo aparecen ahí.

## Normas del código

- Comentarios, docstrings y mensajes de commit en **español**. Los textos visibles van en español dentro de `_("…")`, porque son la clave de las traducciones.
- Nada se ejecuta sin que el usuario lo pulse: ni abrir enlaces, ni conectarse a redes, ni pagar.
- Todo se interpreta en el equipo: ClipQR no envía los códigos a ningún servicio.
- Nada de imports por nombre (`importlib.import_module`): PyInstaller no los ve y el `.exe` se rompe. `tests/test_packaging.py` lo vigila.
- Cada cambio va con sus tests. `py -m pytest -q` y `pyflakes` tienen que pasar.

## Añadir o mejorar un idioma

1. Los catálogos están en `clipqr/locale/<código>_app.py`, `_formats.py` y `_fiscal.py`. Cada uno es un diccionario `TEXTS` de *texto en español → traducción*.
2. Para un idioma nuevo: copia los tres `en_*.py`, traduce los valores y añade el idioma a `LANGUAGES`, `CATALOGS` y `WINDOWS_LANGIDS` en `clipqr/i18n.py`. Para el instalador, añade `installer/texts_<código>.py`.
3. Respeta las `{llaves}`, los `\n` y los símbolos (↗ · ✓). No traduzcas las siglas oficiales (CUIT, CAE, NIF, Pix…).
4. `py -m pytest -q tests/test_i18n.py` te dice qué falta o qué sobra.

## Añadir un formato

1. Crea el módulo (por ejemplo, `clipqr/fiscal/py_sifen.py`) con una función decorada con `@register` que reciba el texto del QR y devuelva un `Result`, o `None` si no es ese formato.
2. Para facturas, usa `Comprobante` e `invoice_result` (`clipqr/fiscal/__init__.py`).
3. Impórtalo en `clipqr/formats.py`.
4. Con datos rotos nunca lanza excepciones: devuelve el resultado con un aviso («QR de factura incompleto o modificado»).
5. Tests con los ejemplos de la especificación oficial y datos ficticios con dígitos verificadores correctos. **Nunca datos personales reales.**

## Pull requests

- Una cosa por PR, con una descripción breve de qué cambia para quien usa ClipQR y cómo lo probaste.
- Las PR se revisan en unos días. Si algo no encaja, lo hablamos en la propia PR.

Al participar aceptas el [código de conducta](CODE_OF_CONDUCT.md).

---

<a id="english"></a>

# Contributing to ClipQR

Thanks for wanting to help! ClipQR is a small project, so every contribution counts: a language, your country's invoice format, a bug report or an idea.

## Ways to help

- **Report a bug:** open an [issue](https://github.com/MojeZcg/ClipQR/issues/new/choose) and paste the report from **Settings › Error report**. It doesn't include your codes or images.
- **A QR code that isn't read or is misread:** attach the QR code **anonymized**. This is the most useful thing for real invoices and payments, since the formats were tested with the official examples.
- **Translate:** see [Adding or improving a language](#adding-or-improving-a-language).
- **A new format** (invoice, payment or document from your country): see [Adding a format](#adding-a-format).
- **Code:** issues labelled [`good first issue`](https://github.com/MojeZcg/ClipQR/labels/good%20first%20issue) are meant for getting started.

## Setup

```bash
git clone https://github.com/MojeZcg/ClipQR.git
cd ClipQR
py -m pip install -r requirements.txt pytest pyflakes
py main.py          # the app (close ClipQR first if it's installed and running)
py -m pytest -q     # tests
py -m pyflakes clipqr installer tests tools
```

`build.bat` builds `dist\ClipQR.exe` and `build_setup.bat` builds the installer. Before proposing a large change, also try the compiled `.exe`: some bugs only show up there.

## Code guidelines

- Comments, docstrings and commit messages are in **Spanish**. Visible texts are written in Spanish inside `_("…")`, because they are the key for the translations.
- Nothing runs unless the user clicks it: no opening links, joining networks or paying on its own.
- Everything is parsed on the device: ClipQR never sends codes to any service.
- No imports by name (`importlib.import_module`): PyInstaller can't see them and the `.exe` breaks. `tests/test_packaging.py` checks this.
- Every change comes with tests. `py -m pytest -q` and `pyflakes` must pass.

## Adding or improving a language

1. The catalogs live in `clipqr/locale/<code>_app.py`, `_formats.py` and `_fiscal.py`. Each one is a `TEXTS` dictionary of *Spanish text → translation*.
2. For a new language: copy the three `en_*.py` files, translate the values, and add the language to `LANGUAGES`, `CATALOGS` and `WINDOWS_LANGIDS` in `clipqr/i18n.py`. For the installer, add `installer/texts_<code>.py`.
3. Keep the `{placeholders}`, `\n` and symbols (↗ · ✓). Don't translate official acronyms (CUIT, CAE, NIF, Pix…).
4. `py -m pytest -q tests/test_i18n.py` tells you what's missing or extra.

## Adding a format

1. Create the module (for example, `clipqr/fiscal/py_sifen.py`) with a function decorated with `@register` that takes the QR text and returns a `Result`, or `None` if it isn't that format.
2. For invoices, use `Comprobante` and `invoice_result` (`clipqr/fiscal/__init__.py`).
3. Import it in `clipqr/formats.py`.
4. On broken data it never raises: return the result with a warning ("Invoice QR is incomplete or has been modified").
5. Tests use the examples from the official specification and fictitious data with correct check digits. **Never real personal data.**

## Pull requests

- One thing per PR, with a short description of what changes for ClipQR users and how you tested it.
- PRs are reviewed within a few days. If something doesn't fit, we'll talk it over in the PR itself.

By taking part you agree to the [code of conduct](CODE_OF_CONDUCT.md).
