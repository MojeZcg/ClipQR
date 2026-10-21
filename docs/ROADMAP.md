# Hoja de ruta de ClipQR

Especificación PR por PR desde la versión actual (1.0.0) hasta la 1.3. Cada PR es pequeño, se puede revisar por sí solo y deja la app funcionando.

**Formato de cada PR**
- **Objetivo:** qué problema resuelve.
- **Cambios:** qué se toca.
- **Hecho cuando:** criterios de aceptación comprobables.
- **Tests:** qué se añade a la batería automática (desde el PR 1.0.1).

**Reglas para todos los PR**
- Rama `feat/…` o `fix/…`; nunca directamente en `main` (desde el PR 1.0.1, `main` exige que pasen los tests).
- Nada se ejecuta sin que el usuario pulse un botón: abrir enlaces, conectar redes, borrar archivos…
- Todo funciona sin conexión; la red solo se usa cuando el usuario lo pide (o para buscar actualizaciones, si lo activa).
- Cualquier dato del usuario que se guarde en disco va cifrado con su cuenta de Windows (DPAPI).
- Al cerrar cada versión: subir `VERSION`, escribir `docs/release-notes/vX.Y.Z.md`, etiquetar y publicar (ver [DISTRIBUCION.md](DISTRIBUCION.md)).

| Versión | Tema | PRs |
|---|---|---|
| **1.0.x** | Cimientos: código ordenado, tests, publicación automática | 1.0.1 – 1.0.4 |
| **1.1.0** | Pulir lo que ya hay: rapidez, teclado, varias pantallas, seguridad | 1.1.1 – 1.1.7 |
| **1.2.0** | Funciones nuevas: crear QR, facturas, pagos, embarque, más entradas | 1.2.1 – 1.2.8 |
| **1.3.0** | Alcance: inglés, accesibilidad, webcam, Store | 1.3.1 – 1.3.4 |

---

## 1.0.x — Cimientos

No cambia nada visible para el usuario, pero todo lo demás depende de esto.

### PR 1.0.1 · Dividir el código y añadir tests
**Objetivo:** `clipqr.py` tiene ~1.800 líneas. Separarlo hace que cada PR siguiente toque solo una parte, y los tests evitan que una mejora rompa lo que ya funciona.

**Cambios**
- Paquete `clipqr/`:

  | Módulo | Contenido |
  |---|---|
  | `decode.py` | Lectura de QR |
  | `payloads.py` | Interpretación de cada tipo y `headline` |
  | `actions.py` | Wi‑Fi, abrir, papelera, capturas |
  | `settings.py` | Ajustes |
  | `winplatform.py` | Registro, DWM, StartupTask, rutas de Windows |
  | `ui/popup.py`, `ui/history.py`, `ui/settings_window.py` | Ventanas |
  | `app.py` | Bandeja, sondeo del portapapeles, orquestación |

- `clipqr.py` queda como punto de entrada de una línea, para que los scripts de compilación no cambien.
- `tests/` con pytest:
  - `test_payloads.py`: cada tipo con varios textos reales, incluidos casos raros (`\;` escapado, MeCard sin nombre, URL sin esquema).
  - `test_decode.py`: imágenes generadas con zxing para todos los tipos y formatos; la foto borrosa real en `tests/fixtures/`; una imagen con dos QR; una captura sin QR (debe devolver `[]`).
  - `test_logo.py`: el QR de `assets/logo.png` lleva a la URL del repo.
- `.github/workflows/tests.yml`: pytest en `windows-latest` en cada PR.

**Hecho cuando:** `py -m pytest` pasa en local y en GitHub; la app compilada funciona exactamente igual que la 1.0.0.

### PR 1.0.2 · Releases automáticas
**Objetivo:** publicar versiones sin compilar en tu PC.

**Cambios**
- `.github/workflows/release.yml`: al subir una etiqueta `v*`, ejecuta los tests, compila el exe portátil, el instalador y el MSIX, genera `SHA256SUMS.txt` y publica la release (detalle en [DISTRIBUCION.md §1](DISTRIBUCION.md#1-compilación-y-releases-automáticas-github-actions)).
- `docs/release-notes/v1.0.0.md` con las notas actuales.
- El workflow falla si la etiqueta no coincide con `VERSION`.

**Hecho cuando:** etiquetar `v1.0.1` en una rama de prueba produce una release con los 4 archivos, y los ejecutables descargados funcionan en un Windows sin Python.

### PR 1.0.3 · Instalación silenciosa (necesaria para winget)
**Objetivo:** instalar y desinstalar sin interfaz, para winget y despliegues.

**Cambios** en `installer/setup.py`:
- `ClipQR-Setup.exe /silent [/noautostart] [/desktop] [/launch]` instala sin ventanas y sale con código 0, o ≠0 si hay error.
- `ClipQR.exe --uninstall /silent` desinstala sin preguntar.
- `QuietUninstallString` en el registro.
- Escribe `%TEMP%\ClipQR-Setup.log` con lo que ha hecho.

**Hecho cuando:** `ClipQR-Setup.exe /silent` instala con inicio automático y sin icono en el escritorio, sin mostrar nada; `/silent /noautostart` lo instala sin inicio automático; la desinstalación silenciosa no deja nada (mismas comprobaciones que la manual).

**Tests:** función `parse_args` del instalador.

### PR 1.0.4 · Firma de código y winget
**Objetivo:** reducir el aviso de SmartScreen y publicar en winget.

**Cambios**
- Paso de firma en `release.yml` con el método elegido ([DISTRIBUCION.md §3](DISTRIBUCION.md#3-firma-de-código)). Se firman los dos `ClipQR.exe` antes de empaquetar el instalador, y luego `ClipQR-Setup.exe`.
- Paso `wingetcreate update … --submit` en `release.yml`, con el secret `WINGET_TOKEN`.
- README: instalar con `winget install MojeZcg.ClipQR`.

**Hecho cuando:** `signtool verify /pa` da OK con los 3 ejecutables de la release, y el manifiesto está aceptado en winget-pkgs.

---

## 1.1.0 — Pulir lo que ya hay

### PR 1.1.1 · Detectar el QR copiado durante el arranque
**Objetivo:** hoy, una imagen copiada mientras ClipQR se abre no se detecta, porque solo reacciona a cambios posteriores.

**Cambios:** al terminar de arrancar, si el portapapeles tiene una imagen copiada hace menos de 30 s, se escanea. Para la antigüedad se usa la hora de `GetClipboardSequenceNumber` guardada al cerrar o, en su defecto, solo si ClipQR se ha abierto a mano (no en el inicio de Windows).

**Hecho cuando:** abrir ClipQR justo después de copiar un QR muestra el aviso; abrirlo con una imagen antigua en el portapapeles no muestra nada.

### PR 1.1.2 · Aviso en la pantalla correcta
**Objetivo:** con varios monitores, el aviso sale siempre en el principal.

**Cambios:**
- `_work_area()` pasa a usar `MonitorFromPoint(cursor)` + `GetMonitorInfoW`, para que el aviso salga en el monitor donde está el ratón.
- La posición «Donde lo dejé» se guarda junto con el monitor. Si ese monitor ya no existe, el aviso vuelve a la esquina por defecto.
- Escalado por monitor: `SetProcessDpiAwareness(2)` (*per-monitor*) y tamaños recalculados en cada aviso.

**Hecho cuando:** con dos monitores de distinta escala, el aviso aparece nítido y bien colocado en el monitor del ratón.

### PR 1.1.3 · Teclado en el aviso
**Objetivo:** usar el aviso sin ratón.

**Cambios**
- **Foco:** el aviso no roba el foco al aparecer. Lo toma con `Ctrl+Alt+Espacio` (configurable) o al hacer clic en él.
- **Atajos con el foco en el aviso:**

  | Tecla | Acción |
  |---|---|
  | `Enter` | Acción principal del primer código |
  | `1`–`9` | Copiar el dato n.º 1–9; el número aparece junto a cada botón «Copiar» |
  | `Ctrl+C` | Copiar el dato principal |
  | `Tab` | Pasar al siguiente código |
  | `Esc` | Cerrar |

- Los botones se resaltan al recorrerlos con `Tab`, y se puede pulsar el resaltado con `Espacio`.

**Hecho cuando:** se puede conectar a un Wi‑Fi o copiar cualquier dato solo con el teclado.

### PR 1.1.4 · Atajo global: escanear una zona de la pantalla
**Objetivo:** leer un QR que está en pantalla sin pasar por Recortes ni guardar ningún archivo.

**Cambios**
- `RegisterHotKey` con `Ctrl+Alt+Q` por defecto (configurable en Configuración; avisa si el atajo está ocupado).
- Selector propio: congela la pantalla en todos los monitores, la oscurece y deja arrastrar un rectángulo. Escanea la zona al soltar; `Esc` cancela. Si se hace clic sin arrastrar, escanea toda la pantalla de ese monitor.
- La imagen no se copia al portapapeles ni se guarda en disco.
- Bandeja: «Escanear zona de la pantalla».

**Hecho cuando:** con un QR visible en el navegador, el atajo, arrastrar y soltar muestra el aviso en menos de 0,5 s. El selector funciona igual en varios monitores con distinta escala.

**Tests:** el recorte de coordenadas entre monitores (función pura).

### PR 1.1.5 · Avisos de seguridad en enlaces
**Objetivo:** ayudar a detectar QR fraudulentos (*quishing*), sin bloquear nada.

**Cambios:** `payloads.link_warnings(url)` devuelve avisos que se muestran en el aviso como una franja ámbar sobre el botón «Abrir enlace»:

| Caso | Aviso |
|---|---|
| Enlace `http://` | «La conexión no está cifrada» |
| Acortador conocido (bit.ly, t.co, tinyurl…; lista en `data/shorteners.txt`) | «Enlace acortado: no se sabe a dónde lleva» |
| Dominio con caracteres de otro alfabeto o punycode (`xn--`) | «El dominio usa caracteres que imitan a otros» |
| Dirección IP en vez de dominio | Aviso |
| Muchos subdominios | Aviso |
| Usuario en la URL (`https://banco.com@malo.com`) | «El enlace no lleva a donde parece» (*decide el último dominio*) |

- El dominio real se muestra resaltado en el titular (`banco.com.malo.xyz` → **malo.xyz**).
- **Sin consultar ningún servicio externo.**

**Hecho cuando:** cada caso de la tabla muestra su aviso y un enlace normal `https://` no muestra ninguno.

**Tests:** tabla de URLs → avisos esperados.

### PR 1.1.6 · Buscar actualizaciones
**Objetivo:** que la gente tenga siempre la última versión.

**Cambios**
- Configuración › General: «Buscar actualizaciones» (activado por defecto, con explicación). Una vez al día consulta `https://api.github.com/repos/MojeZcg/ClipQR/releases/latest`.
- Si hay una versión mayor, aparece un aviso discreto (en la bandeja y en el siguiente aviso de QR): «ClipQR 1.2.0 disponible», con los botones **Ver novedades** e **Instalar**.
- **Instalar:** descarga `ClipQR-Setup.exe` en `%TEMP%`, comprueba su SHA-256 con `SHA256SUMS.txt` de la release (y la firma, si existe desde el PR 1.0.4), lo ejecuta con `/silent /launch` y cierra ClipQR. Conserva la opción de inicio con Windows que ya tenía el usuario.
- Instalaciones portátiles y MSIX: solo avisan. El MSIX lo actualiza la Store.

**Hecho cuando:** una 1.1.0 instalada detecta una release 1.1.1 de prueba y se actualiza sola al pulsar Instalar; un hash erróneo aborta la actualización y lo explica.

**Tests:** comparación de versiones y lectura de `SHA256SUMS.txt`.

### PR 1.1.7 · Detalles
- **Contraseña Wi‑Fi visible:** opción «Mostrar contraseñas al momento» (desactivada por defecto).
- **Fijar el aviso a la vez que se arrastra:** si mueves el aviso, se fija solo durante ese aviso.
- **Error log:** Configuración › General › «Copiar informe de errores», que copia los últimos errores al portapapeles para pegarlos en una incidencia de GitHub (no se envía nada).
- **Plantilla de incidencias** en GitHub (`.github/ISSUE_TEMPLATE/bug.yml`) que pide la versión, la versión de Windows y ese informe.

**Cierre de la 1.1.0:** notas, etiqueta `v1.1.0`, actualizar Store y winget (automático desde 1.0.4).

---

## 1.2.0 — Funciones nuevas

### PR 1.2.1 · Crear QR (la función inversa)
**Objetivo:** hoy ClipQR solo lee; crear QR lo convierte en la herramienta completa de QR.

**Cambios**
- **Bandeja:** «Crear QR del portapapeles» (`Ctrl+Alt+G`, configurable). Abre la ventana **Crear QR** con el texto copiado.
- **Ventana Crear QR:**
  - **Tipo:** Texto/enlace, Wi‑Fi (red, contraseña, seguridad, oculta), Contacto (nombre, teléfono, email, empresa, web), Email, Teléfono, SMS o Ubicación. Cada tipo con su formulario, y el contenido se arma con la función inversa de `payloads.py`.
  - **Vista previa en vivo.**
  - **Opciones:** corrección de errores (L/M/Q/H), tamaño, margen, colores (avisa si el contraste es bajo) y logo opcional en el centro (fuerza el nivel H).
  - **Botones:** Copiar imagen, Guardar PNG, Guardar SVG.
- «Crear QR de mi Wi‑Fi actual»: lee la red con `netsh wlan show profile name=… key=clear`. Pide confirmación, porque muestra la contraseña.
- **Verificación:** cada QR generado se vuelve a leer con `decode_image` antes de copiarlo o guardarlo; si no se lee, lo dice (por ejemplo, por un logo demasiado grande).

**Hecho cuando:** cada tipo generado se lee con ClipQR y con la cámara de un móvil (iOS y Android); el SVG se abre en un navegador.

**Tests:** ida y vuelta (payload → texto → `parse_payload` → mismos datos) para cada tipo; generar → `decode_image` → mismo texto.

### PR 1.2.2 · Facturas VeriFactu y TicketBAI
**Objetivo:** el QR de las facturas españolas, obligatorio desde 2026, es uno de los más habituales, y hoy se muestra como un enlace genérico.

**Cambios** en `payloads.py`: el tipo `invoice` se reconoce por el dominio y la ruta de la URL:
- **VeriFactu:** URL de cotejo de la AEAT (`agenciatributaria.gob.es` … `ValidarQR`, con los parámetros `nif`, `numserie`, `fecha`, `importe`).
- **TicketBAI:** dominios de las haciendas forales (Bizkaia/Batuz, Gipuzkoa, Álava), con los parámetros `id`, `s`, `nf`, `i`, `cr`.

En el aviso:
- **Titular:** el importe con formato («123,45 €»).
- **Datos:** NIF del emisor, número de factura, fecha (en formato dd/mm/aaaa) y el sistema (VeriFactu / TicketBAI · territorio).
- **Acción principal:** «Comprobar en Hacienda ↗», que abre la URL de cotejo oficial.
- **Validación:** si el NIF tiene un formato no válido o falta algún parámetro, aparece el aviso «QR de factura incompleto o modificado».

**Antes de programarlo:** confirmar los formatos exactos con la especificación técnica publicada por la AEAT y las haciendas forales, y guardar en `tests/fixtures/` QR reales de facturas con los datos anonimizados.

**Hecho cuando:** los QR reales de prueba de cada sistema se muestran con todos los datos correctos.

### PR 1.2.3 · Pagos SEPA (código EPC)
**Objetivo:** los QR de transferencia («GiroCode/EPC», que empiezan por `BCD`) traen datos que hay que teclear a mano en el banco.

**Cambios:**
- Tipo `payment`. El formato es de líneas, versión 001/002, con el BIC opcional en la 002.
- **Titular:** el importe. **Datos:** beneficiario, IBAN (mostrado en grupos de 4 y validado con su dígito de control), BIC y concepto/referencia, cada uno con su «Copiar».
- **Sin acción de pago:** ClipQR no mueve dinero, solo copia los datos.

**Hecho cuando:** los ejemplos oficiales del EPC se leen bien y un IBAN con el dígito de control mal muestra un aviso.

**Tests:** ejemplos EPC 001 y 002, y IBAN válido/inválido.

### PR 1.2.4 · Tarjetas de embarque
**Objetivo:** las tarjetas de embarque (PDF417 o QR, formato IATA BCBP, empiezan por `M1`) son ilegibles en bruto.

**Cambios:**
- Tipo `boarding`, que interpreta los campos obligatorios de BCBP: pasajero, localizador, origen, destino, aerolínea, vuelo, fecha (día juliano convertido a fecha), asiento y número de secuencia.
- **Titular:** «MAD → BCN · IB 1234». **Datos:** fecha, asiento, pasajero y localizador.
- **Sin acción.**

**Hecho cuando:** los ejemplos del estándar BCBP se leen con todos sus campos; los campos opcionales se ignoran sin errores.

**Tests:** ejemplos BCBP de un tramo y de varios.

### PR 1.2.5 · Más tipos de enlace

| Tipo | Se reconoce por | Muestra | Botón |
|---|---|---|---|
| WhatsApp | `wa.me/…` y `api.whatsapp.com/send` | Número y mensaje | «Abrir chat» |
| Telegram | `t.me/…` | Usuario o canal | «Abrir en Telegram» |
| Criptomonedas | `bitcoin:`, `ethereum:`… | Dirección y cantidad | **Solo copiar** (ninguna acción con dinero) |
| Tiendas de apps | Microsoft Store, Google Play, App Store | Nombre de la tienda | — |
| Redes sociales | Instagram, X, LinkedIn, YouTube, TikTok | Icono y nombre de la red | — |
| Calendario | `.ics` como texto o enlace | Igual que un evento | — |

**Tests:** una tabla con un ejemplo de cada tipo.

### PR 1.2.6 · Arrastrar imágenes y PDF
**Objetivo:** escanear archivos sin copiarlos.

**Cambios**
- Arrastrar imágenes o PDF al icono del escritorio o a la ventana del historial los escanea.
- **PDF:** con `pypdfium2`, cada página a 200 ppp y como mucho 20 páginas. Indica en qué página está cada código.
- Clic derecho en el Explorador › «Escanear con ClipQR»: lo registra el instalador en `HKCU\Software\Classes\SystemFileAssociations\image\shell` y `…\.pdf\shell`, y lo quita la desinstalación.
- Línea de órdenes:
  ```bash
  ClipQR.exe archivo.png
  ```
  Abre el aviso. Con `--json` escribe el resultado por la salida estándar, para usarlo en scripts.

**Hecho cuando:** un PDF de factura con QR en la página 2 muestra el aviso con «Página 2».

### PR 1.2.7 · Historial guardado (opcional)
**Objetivo:** no perder lo escaneado al cerrar.

**Cambios**
- Configuración › Historial: «Guardar el historial al cerrar» (desactivado por defecto).
- **Almacenamiento:** `%APPDATA%\ClipQR\history.bin`, cifrado con DPAPI (`CryptProtectData`, ligado al usuario de Windows). Guarda solo texto, formato, hora y una miniatura pequeña.
- **Borrado:** «Borrar historial» elimina también el archivo. La desinstalación lo borra.
- **Historial:** agrupado por días, con filtro por tipo y opción de fijar elementos (los fijados no caducan).

**Hecho cuando:** el historial sobrevive a un reinicio, y el archivo no se puede leer desde otra cuenta de Windows.

**Tests:** ida y vuelta de cifrado; el archivo nunca contiene el texto en claro.

### PR 1.2.8 · Rendimiento y tamaño
- **Escanear en un proceso aparte** (o con hilos y menos intentos) las capturas grandes sin QR, que hoy tardan ~0,4 s, para que nunca afecten a la interfaz.
- **Probar Nuitka** frente a PyInstaller: tamaño, arranque y falsos positivos de antivirus. Se adopta si mejora al menos dos de los tres.
- **Medición automática:** `tests/bench_*.py` mide el arranque, el primer aviso y la decodificación. Su resultado se publica como artefacto del workflow para detectar si alguna versión empeora.

**Cierre de la 1.2.0:** notas, capturas nuevas (Crear QR, factura, pago), etiqueta `v1.2.0`.

---

## 1.3.0 — Alcance

### PR 1.3.1 · Inglés (y base para más idiomas)
- Todos los textos se mueven a `i18n/es.json` e `i18n/en.json`, con una función `t("clave")`.
- El idioma se elige automáticamente según el de Windows y se puede cambiar en Configuración.
- README en inglés (`README.en.md`) y ficha de la Store en inglés.

**Tests:** las mismas claves en todos los idiomas; ningún texto visible fuera de `t()` (comprobación con un análisis del código).

### PR 1.3.2 · Accesibilidad
- Nombres accesibles para los lectores de pantalla (Narrador, NVDA) en botones e iconos. Los glifos sin texto llevan descripción.
- Modo de alto contraste de Windows: se respetan los colores del sistema.
- Tamaño de texto configurable (100–150 %).

**Hecho cuando:** con el Narrador se oye el tipo y el dato principal al aparecer el aviso.

### PR 1.3.3 · Webcam
- Bandeja › «Escanear con la cámara»: ventana con la imagen en vivo, que lee el QR en cuanto aparece y se cierra sola.
- **Implementación:** Windows Media Foundation (vía `winrt` ya incluido) para no añadir OpenCV. Si no hay cámara, la opción no aparece.

**Hecho cuando:** un QR mostrado en el móvil delante de la webcam se lee en menos de 2 s.

### PR 1.3.4 · Publicación en la Microsoft Store
- Comprobar el MSIX con el Windows App Certification Kit en el workflow.
- Capturas de 1366×768 o más para la Store (escenas completas en `tools/screenshots.py`).
- Primer envío en Partner Center ([DISTRIBUCION.md §5](DISTRIBUCION.md#5-microsoft-store)).

**Cierre de la 1.3.0.**

---

## Ideas para más adelante (sin especificar)
- **Plugins:** tipos de QR añadidos por la comunidad con un archivo de reglas (patrón → campos → acciones).
- **Sincronizar el historial** entre equipos mediante una carpeta elegida (OneDrive), siempre cifrado.
- **Reglas automáticas configurables** («si es un enlace de mi empresa, abrir sin preguntar»), siempre desactivadas por defecto.
- **Versión para macOS/Linux:** el núcleo (lectura e interpretación) ya sería portable tras el PR 1.0.1.
