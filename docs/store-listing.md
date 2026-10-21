# Ficha para la Microsoft Store

Textos listos para copiar en Partner Center › Envío › Listados de Store (Español).

## Nombre
ClipQR

## Descripción breve (máx. 100 caracteres)
Haz una captura de un QR y úsalo al instante: copia datos, conéctate al Wi‑Fi o abre el enlace.

## Descripción

ClipQR detecta automáticamente códigos QR y códigos de barras en lo que copias o capturas en Windows y te muestra su contenido en un aviso, con un botón para cada cosa que puedes hacer.

Haz una captura con Win+Shift+S o Impr Pant, copia una imagen o copia un archivo de imagen desde el Explorador: si hay un código, ClipQR lo lee al momento. Funciona con capturas de pantalla, con fotos borrosas de códigos impresos y con imágenes que tienen varios códigos a la vez.

Nada se ejecuta solo. ClipQR nunca abre enlaces ni se conecta a redes por su cuenta: siempre hay un botón y lo pulsas tú.

QUÉ PUEDES HACER
• Wi‑Fi: ver la red y la contraseña, y conectarte con un clic.
• Contactos: guardar el contacto, llamar, escribir un email o abrir su web.
• Eventos: añadirlos al calendario.
• Enlaces, emails, teléfonos, SMS y ubicaciones: abrirlos en la aplicación adecuada.
• Productos (EAN / UPC): buscar el producto.
• Copiar cualquier dato por separado, todo el contenido o solo la parte que selecciones.

TAMBIÉN INCLUYE
• Historial con búsqueda y miniaturas de cada código.
• Tema claro, oscuro o el mismo que Windows.
• Aviso configurable: tiempo visible, posición, animación y sonido. Se puede arrastrar y fijar.
• Lee QR, Micro QR, DataMatrix, Aztec, PDF417, EAN, UPC, Code 128, Code 39 y más.
• Inicio con Windows opcional.

PRIVACIDAD
Todo se procesa en tu equipo. ClipQR no envía imágenes ni datos a ningún servidor y no tiene publicidad ni telemetría.

## Características (una por línea, máx. 20)
Detecta QR y códigos de barras en capturas y en el portapapeles
Conecta al Wi‑Fi desde un QR con un clic
Guarda contactos y añade eventos al calendario
Copia cada dato por separado o solo la parte que elijas
Historial con búsqueda
Tema claro y oscuro
Aviso configurable, arrastrable y fijable
Funciona sin conexión; nada sale de tu equipo

## Palabras clave (máx. 7)
QR, código QR, lector QR, escáner QR, código de barras, portapapeles, captura de pantalla

## Categoría
Utilidades y herramientas

## URL de la política de privacidad
https://github.com/MojeZcg/ClipQR/blob/main/PRIVACY.md

## Sitio web / soporte
https://github.com/MojeZcg/ClipQR
https://github.com/MojeZcg/ClipQR/issues

## Capturas de pantalla (en este orden)
1. docs/screenshots/hero.png
2. docs/screenshots/popup-wifi.png
3. docs/screenshots/popup-contact.png
4. docs/screenshots/popup-multi.png
5. docs/screenshots/history.png
6. docs/screenshots/settings-dark.png
7. docs/screenshots/popup-light.png

La Store pide capturas de al menos 1366×768 para escritorio. `hero.png` (1920×1080) ya cumple; las demás conviene presentarlas a ese tamaño, o generar escenas completas con `tools/screenshots.py`.

## Declaración de capacidades restringidas
**runFullTrust**: ClipQR es una aplicación de escritorio Win32 (Python + Tkinter). Necesita confianza total para leer el portapapeles, mostrar el icono en la bandeja del sistema y crear perfiles Wi‑Fi con `netsh` cuando el usuario pulsa *Conectar a la red*.

## Clasificación por edades
Cuestionario IARC: sin violencia, sin contenido sexual, sin compras, sin intercambio de datos entre usuarios, sin ubicación compartida. Resultado esperado: 3+ / Todos.

## Pasos en Partner Center
1. Reserva el nombre **ClipQR**.
2. En *Administración de productos › Identidad del producto*, copia `Package/Identity/Name`, `Package/Identity/Publisher` y `Package/Properties/PublisherDisplayName`.
3. Compila con esos valores:
   `.\build_msix.ps1 -IdentityName "<Name>" -Publisher "<Publisher>" -PublisherDisplayName "<PublisherDisplayName>"`
4. En *Paquetes*, sube `dist\ClipQR-<versión>.msix`.
5. Rellena *Propiedades* (categoría, política de privacidad), *Clasificaciones por edades* y *Listados de Store* con este documento.
6. Envía para certificación.
