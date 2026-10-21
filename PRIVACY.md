# Política de privacidad de ClipQR

*Última actualización: 21 de octubre de 2026*

ClipQR es una aplicación para Windows que detecta códigos QR y códigos de barras en las imágenes que copias o capturas. Esta política explica qué datos usa y qué hace con ellos.

## Resumen

**ClipQR no recoge, envía ni vende ningún dato.** Todo se procesa en tu equipo.

## Qué datos usa la aplicación

- **Imágenes del portapapeles.** Cuando copias una imagen o haces una captura, ClipQR la analiza en tu equipo para buscar códigos. La imagen no se guarda en disco ni se envía a ningún sitio.
- **Contenido de los códigos detectados.** Se muestra en pantalla y se guarda en un historial **solo en memoria**, que se borra al cerrar ClipQR o al pulsar *Borrar historial*.
- **Configuración.** Tus preferencias (tiempo visible, posición, tema…) se guardan en un archivo local (`settings.json`) dentro de la carpeta de datos de la aplicación.
- **Registro de errores.** Si algo falla, el detalle técnico se guarda en un archivo local (`error.log`) para poder diagnosticarlo. No contiene imágenes y nunca se envía.

## Conexiones a internet

ClipQR solo se conecta a internet por su cuenta para una cosa, y se puede desactivar:

- **Buscar actualizaciones** (activado por defecto; se desactiva en *Configuración › General*). Una vez al día consulta la lista de versiones publicadas en GitHub (`api.github.com/repos/MojeZcg/ClipQR/releases/latest`). No envía ningún dato tuyo ni de tus códigos: es una petición normal, y GitHub ve lo que ve cualquier web (tu dirección IP y la versión de ClipQR en el agente de usuario). Si hay una versión nueva, ClipQR te avisa y solo la descarga e instala si pulsas **Instalar**. La versión de la Microsoft Store no hace esta consulta: la actualiza la Store.

Además, la red se usa cuando **tú** pulsas un botón que la necesita, por ejemplo:

- **Abrir enlace**, **Ver en el mapa**, **Buscar producto** o **Buscar en Google**: se abre tu navegador con esa dirección.
- **Escribir email**, **Llamar** o **Enviar SMS**: se abre la aplicación que tengas configurada en Windows para eso.
- **Conectar a la red**: se crea el perfil Wi‑Fi en Windows con el nombre y la contraseña del código, y Windows se conecta a esa red.

Lo que ocurra a partir de ahí depende de esas aplicaciones y sitios web, que tienen sus propias políticas de privacidad.

## Datos de terceros

ClipQR no incluye publicidad, analítica, telemetría ni servicios de terceros.

## Menores

ClipQR no recoge datos de nadie, tampoco de menores.

## Cambios

Si esta política cambia, la nueva versión se publicará en esta misma página con su fecha de actualización.

## Contacto

Para cualquier duda sobre privacidad, abre una incidencia en https://github.com/MojeZcg/ClipQR/issues.

---

# ClipQR privacy policy (English)

ClipQR does not collect, transmit or sell any data. Clipboard images are analyzed locally and never stored or uploaded. Detected codes are kept in an in-memory history that is cleared when the app closes. Settings and an error log are stored only in local files. The only connection the app makes on its own is an optional daily update check against the public GitHub releases API (it sends no personal data and can be turned off in Settings; the Microsoft Store version doesn't do it). Otherwise the network is used only when you press a button that requires it (open a link, search, connect to Wi‑Fi), which hands the action to your browser, another app, or Windows. There is no advertising, analytics or telemetry. Questions: https://github.com/MojeZcg/ClipQR/issues
