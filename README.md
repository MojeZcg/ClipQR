<p align="center">
  <img src="assets/logo.png" width="112" alt="Logo de ClipQR">
</p>

<h1 align="center">ClipQR</h1>

<p align="center">
  <b>Haz una captura de un QR y úsalo al instante.</b><br>
  Detecta QR y códigos de barras en lo que copias o capturas en Windows y te deja copiar cada dato,
  conectarte al Wi‑Fi, guardar el contacto o abrir el enlace, con un clic.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows" alt="Windows 10 | 11">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/licencia-MIT-22a06b" alt="Licencia MIT">
</p>

![ClipQR](docs/screenshots/hero.png)

## Cómo funciona

1. Haz una captura (`Win`+`Shift`+`S` o `Impr Pant`), copia una imagen o copia un archivo de imagen desde el Explorador.
2. Si contiene un QR o un código de barras, aparece un aviso arriba a la derecha.
3. Elige qué hacer: copiar un dato, copiar todo, copiar una parte o usar el botón de acción.

**Nada se ejecuta solo.** ClipQR nunca abre enlaces ni se conecta a redes por su cuenta: siempre hay un botón y lo pulsas tú.

## Qué reconoce

| Tipo | Datos que muestra | Botones |
|---|---|---|
| 📶 **Wi‑Fi** | Red, contraseña (oculta), seguridad | **Conectar a la red** |
| 👤 **Contacto** (vCard / MeCard) | Nombre, empresa, teléfono, email, web… | **Guardar contacto**, **Llamar**, **Escribir email**, **Abrir web** |
| 📅 **Evento** | Título, inicio, fin, lugar | **Añadir al calendario** |
| 🔗 **Enlace** | Dominio | **Abrir enlace** |
| ✉️ **Email** | Destinatario, asunto, mensaje | **Escribir email** |
| 📞 **Teléfono / SMS** | Número, mensaje | **Llamar**, **Enviar SMS** |
| 📍 **Ubicación** | Coordenadas | **Ver en el mapa** |
| 🔑 **2FA (otpauth)** | Cuenta, emisor, secreto (oculto) | — |
| 🛒 **Producto** (EAN / UPC) | Código | **Buscar producto** |
| 📄 **Texto** | URLs y emails que contenga | **Buscar en Google** |

También lee DataMatrix, Aztec, PDF417, Code 128, Code 39 y otros formatos, gracias a [zxing-cpp](https://github.com/zxing-cpp/zxing-cpp). Funciona con capturas de pantalla, con fotos borrosas de QR impresos y con imágenes que tienen varios códigos a la vez.

## Capturas

| Wi‑Fi | Contacto |
|---|---|
| ![Aviso de Wi‑Fi](docs/screenshots/popup-wifi.png) | ![Aviso de contacto](docs/screenshots/popup-contact.png) |
| **Varios códigos en una imagen** | **Tema claro** |
| ![Enlace y código de barras](docs/screenshots/popup-multi.png) | ![Aviso con tema claro](docs/screenshots/popup-light.png) |
| **Historial con búsqueda** | **Configuración** |
| ![Historial](docs/screenshots/history.png) | ![Configuración](docs/screenshots/settings-dark.png) |

## Instalación

1. Descarga `ClipQR.exe` desde [Releases](../../releases).
2. Guárdalo en una carpeta fija, por ejemplo `%LOCALAPPDATA%\Programs\ClipQR\`, y haz doble clic.

No necesita Python ni permisos de administrador. La primera vez aparece un aviso de bienvenida y se activa el inicio con Windows (se puede desactivar en Configuración). ClipQR queda en la bandeja del sistema, junto al reloj.

> Si aparece Windows SmartScreen («Windows protegió su PC»), pulsa **Más información → Ejecutar de todas formas**. Aparece porque el `.exe` no está firmado digitalmente.

## Configuración

Desde el icono ⚙ del aviso o desde **Configuración…** en el menú de la bandeja:

- **Aviso:** tiempo visible (de 5 s a 5 min), cerrar solo o no, pausa con el ratón encima, animación y posición. El aviso también se puede arrastrar y fijar con 📌.
- **Apariencia:** tema claro, oscuro o el mismo que Windows.
- **Detección:** solo QR o también códigos de barras, leer archivos copiados desde el Explorador, sonido al detectar y pausar la detección.
- **Historial:** cuántos escaneos se guardan y borrar el historial.
- **General:** iniciar con Windows.

Los ajustes se guardan en `%APPDATA%\ClipQR\settings.json`.

## Privacidad

Todo se procesa en tu equipo. ClipQR no envía imágenes ni datos a ningún servidor. Solo se usa la red cuando pulsas un botón que la necesita, como abrir un enlace o buscar un producto. El historial se guarda solo en memoria y se borra al cerrar la aplicación.

## Desde el código

```bash
py -m pip install -r requirements.txt
pythonw clipqr.py                   # ejecutar sin consola
py clipqr.py imagen.png             # decodificar una imagen y mostrar el resultado
build.bat                           # generar dist\ClipQR.exe con PyInstaller
py tools\screenshots.py             # regenerar las capturas de docs/screenshots
```

| Archivo | Qué contiene |
|---|---|
| `clipqr.py` | Toda la aplicación: vigilancia del portapapeles, decodificación, interpretación de cada tipo, interfaz y bandeja del sistema |
| `tools/screenshots.py` | Monta escenas con datos de ejemplo y genera las capturas del README |
| `assets/` | Logo (`logo.png`) e icono del ejecutable |
| `build.bat` | Compila el `.exe` en un solo archivo |

## Licencia

[MIT](LICENSE)
