# Hoja de ruta de ClipQR

Especificación PR por PR desde la versión actual (1.0.0) hasta la 1.4. Cada PR es pequeño, se puede revisar por sí solo y deja la app funcionando.

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
| **1.2.0** | Crear QR; facturas (Argentina/ARCA primero, América Latina, Europa), pagos QR (EMVCo, Pix, SEPA), productos y medicamentos (GS1), DNI y embarque | 1.2.1 – 1.2.9 |
| **1.3.0** | Más formas de escanear y guardar: PDF, lotes a Excel, historial cifrado, webcam, rendimiento | 1.3.1 – 1.3.5 |
| **1.4.0** | Alcance: inglés y portugués, accesibilidad, Microsoft Store | 1.4.1 – 1.4.3 |

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

- `main.py` es el punto de entrada (para PyInstaller y para ejecutar desde el código).
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
- **Foco:** el aviso no roba el foco al aparecer. Lo toma con `Ctrl+Shift+Espacio` (configurable) o al hacer clic en él.
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
- `RegisterHotKey` con `Win+Shift+Q` por defecto, junto al `Win+Shift+S` de las capturas (configurable en Configuración; avisa si el atajo está ocupado). Nunca `Ctrl+Alt+letra`: en teclados español y latinoamericano es `AltGr` (`Ctrl+Alt+Q` escribe @).
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

## 1.2.0 — Comprobantes, pagos y productos (Argentina primero, y más países)

Los QR más útiles en el día a día no son los enlaces: son los de **facturas, pagos y productos**. Cada país tiene su formato, así que esta versión crea una base común y añade los formatos por país, empezando por Argentina.

**Fuentes y muestras.** Antes de programar cada formato hay que:
- confirmar la especificación oficial vigente (los enlaces de cada PR son el punto de partida, no la verdad final);
- guardar en `tests/fixtures/<país>/` al menos dos QR reales con los datos personales anonimizados.

Ningún formato se da por terminado solo con ejemplos inventados.

### PR 1.2.1 · Crear QR (la función inversa)
**Objetivo:** hoy ClipQR solo lee; crear QR lo convierte en la herramienta completa de QR.

**Cambios**
- **Bandeja:** «Crear QR del portapapeles» (`Win+Shift+G`, configurable). Abre la ventana **Crear QR** con el texto copiado.
- **Ventana Crear QR:**
  - **Tipo:** Texto/enlace, Wi‑Fi (red, contraseña, seguridad, oculta), Contacto (nombre, teléfono, email, empresa, web), Email, Teléfono, SMS, Ubicación o WhatsApp. Cada tipo con su formulario, y el contenido se arma con la función inversa de `payloads.py`.
  - **Vista previa en vivo.**
  - **Opciones:** corrección de errores (L/M/Q/H), tamaño, margen, colores (avisa si el contraste es bajo) y logo opcional en el centro (fuerza el nivel H).
  - **Botones:** Copiar imagen, Guardar PNG, Guardar SVG.
- «Crear QR de mi Wi‑Fi actual»: lee la red con `netsh wlan show profile name=… key=clear`. Pide confirmación, porque muestra la contraseña.
- **Verificación:** cada QR generado se vuelve a leer con `decode_image` antes de copiarlo o guardarlo; si no se lee, lo dice.

**Hecho cuando:** cada tipo generado se lee con ClipQR y con la cámara de un móvil (iOS y Android); el SVG se abre en un navegador.

**Tests:** ida y vuelta (datos → texto → `parse_payload` → mismos datos) y generar → `decode_image` → mismo texto, para cada tipo.

### PR 1.2.2 · Base común para comprobantes fiscales
**Objetivo:** que añadir un país sea escribir un archivo pequeño, y que todas las facturas se vean igual en el aviso.

**Cambios**
- Paquete `clipqr/fiscal/` con un registro de formatos. Cada formato es un módulo con:
  - `match(texto) -> bool`: detección barata.
  - `parse(texto) -> Comprobante`: interpretación.
  - Sus tablas (tipos de comprobante, monedas, tipos de documento).
- `Comprobante` (estructura común):

  | Campo | Contenido |
  |---|---|
  | `pais` | — |
  | `sistema` | «ARCA», «SAT CFDI», «VeriFactu»… |
  | `tipo` | «Factura B», «Nota de crédito A»… |
  | `numero` | Número de comprobante |
  | `fecha` | — |
  | `emisor` | Identificador fiscal formateado + validez del dígito verificador |
  | `receptor` | Ídem |
  | `importe` | — |
  | `moneda` | Más la cotización si viene |
  | `codigo_autorizacion` | CAE, UUID, CUFE… |
  | `url_verificacion` | Página oficial para comprobarlo |
  | `avisos` | Lista de problemas encontrados |

- **Aviso (tipo `invoice`):**
  - **Titular:** el importe con el formato del país («$ 12.345,67», «12.345,67 €», «$12,345.67 MXN»).
  - **Debajo:** «Factura B · 00003‑00001234 · 21/10/2026».
  - **Datos:** emisor, receptor y código de autorización, cada uno con «Copiar».
  - **Acción principal:** «Verificar en <organismo> ↗». Solo abre la página oficial; ClipQR no consulta nada por su cuenta.
  - **«Copiar resumen»:** texto con todos los datos, listo para pegar en una planilla.
  - **Franja ámbar** si hay avisos: dígito verificador incorrecto, fecha futura, importe negativo o cero, datos que faltan o código mal formado.
- `clipqr/fiscal/ids.py`: validadores de identificadores fiscales con su dígito verificador. Cada país añade el suyo.

**Hecho cuando:** un formato de ejemplo de prueba se registra en un solo archivo y aparece en el aviso con todos los campos.

**Tests:** formateo de importes por país, y que un formato con datos inválidos genere avisos y no errores.

### PR 1.2.3 · Argentina: comprobantes electrónicos de ARCA (ex AFIP)
**Objetivo:** el QR obligatorio de las facturas argentinas (RG 4892/2020) es una URL con los datos en base64, ilegible a simple vista.

**Formato:** `https://www.afip.gob.ar/fe/qr/?p=<base64 de un JSON>`. Se acepta también el dominio de ARCA cuando lo use, y base64 con o sin relleno o en variante URL.

**Campos del JSON:**

| Campo | Contenido |
|---|---|
| `ver` | Versión |
| `fecha` | Fecha |
| `cuit` | CUIT del emisor |
| `ptoVta` | Punto de venta |
| `tipoCmp` | Tipo de comprobante |
| `nroCmp` | Número |
| `importe` | Importe |
| `moneda` | Moneda |
| `ctz` | Cotización |
| `tipoDocRec` | Tipo de documento del receptor |
| `nroDocRec` | Documento del receptor |
| `tipoCodAut` | `E` = CAE, `A` = CAEA |
| `codAut` | Código de autorización |

**Cambios** (`clipqr/fiscal/ar_arca.py`)
- **Tablas:**
  - **Tipos de comprobante:** 1 Factura A, 2 Nota de débito A, 3 Nota de crédito A, 6/7/8 lo mismo B, 11/12/13 C, 51 M, 19 E de exportación…, completada con la tabla oficial de ARCA.
  - **Monedas:** `PES` = $, `DOL` = US$, `060` = €, `012` = R$…
  - **Tipos de documento:** 80 CUIT, 86 CUIL, 96 DNI, 99 Consumidor final.
- **Número:** formateado como `PPPPP-NNNNNNNN` (punto de venta y número).
- **CUIT/CUIL:** validados con el dígito verificador (módulo 11) y mostrados como `20-12345678-9`.
- **Moneda extranjera:** se muestra «US$ 100,00 (cotización 1.000,00 → $ 100.000,00)».
- **Acciones:**
  - «Ver en ARCA ↗» abre la URL del propio QR.
  - «Constatar comprobante ↗» abre la página oficial de constatación de comprobantes.
  - «Copiar datos para constatar» copia en un bloque CUIT, tipo, punto de venta, número, fecha, importe y CAE, en el orden en que los pide ese formulario.
- **Avisos:** JSON inválido o base64 roto («QR de factura dañado o modificado»), CUIT con dígito verificador incorrecto, falta el CAE, o la fecha es posterior a hoy.

**Fuente:** especificación del código QR para comprobantes electrónicos publicada por ARCA (afip.gob.ar/fe/qr/). Confirmar los campos y las tablas vigentes.

**Hecho cuando:**
- QR reales de Factura A, B y C, de una nota de crédito y de un comprobante en dólares se muestran con todos los datos correctos;
- un QR con el CUIT alterado muestra el aviso;
- un QR con el base64 cortado muestra «dañado» en vez de fallar.

**Tests:** cada fixture → `Comprobante` esperado; validador de CUIT con casos válidos e inválidos.

### PR 1.2.4 · Pagos con QR (estándar EMVCo): Argentina, Brasil y más
**Objetivo:** los QR de cobro de los comercios (Transferencias 3.0 en Argentina, Mercado Pago, MODO, Pix en Brasil, Bre-B en Colombia, y otros) siguen casi todos el estándar **EMVCo**. Hoy se ven como un texto de números (`000201010211…`).

**Cambios** (`clipqr/payments/emvco.py`)
- **Lectura del formato:** TLV (etiqueta 2 dígitos + largo 2 dígitos + valor), con plantillas anidadas.
- **Campos:**

  | Etiqueta | Contenido |
  |---|---|
  | 59 | Nombre del comercio |
  | 60 | Ciudad |
  | 58 | País |
  | 53 | Moneda ISO 4217 (`032` ARS, `986` BRL, `170` COP…) |
  | 54 | Importe; sin importe = «el importe se ingresa al pagar» |
  | 62 | Datos adicionales: referencia, terminal, etiqueta |
  | 01 | QR estático o dinámico |
  | 26–51 | Cuenta del comercio |

- **CRC:** verifica el CRC16 de la etiqueta 63 y, si no coincide, muestra el aviso «QR de pago alterado: no lo uses».
- **Cuenta del comercio, por país**, reconocida por el identificador de cada plantilla:
  - **Argentina:** CVU/CBU (validado con sus dígitos verificadores) o alias, y la entidad o billetera si se puede identificar.
  - **Brasil (Pix):** `br.gov.bcb.pix` con la clave Pix (email, teléfono, CPF/CNPJ validado o clave aleatoria) o la URL del pago dinámico.
  - **Otros identificadores:** se muestran tal cual, con su número de plantilla.
- **Aviso:**
  - **Titular:** «Pagar a <comercio>» y el importe.
  - **Datos:** CVU, alias o clave Pix, ciudad y referencia, cada uno con «Copiar».
  - **Sin botón de pago:** ClipQR no mueve dinero. El texto explica que se paga escaneando el QR con la app del banco o la billetera.

**Hecho cuando:** QR reales de Mercado Pago, MODO, un QR de Transferencias 3.0 y un Pix (estático y dinámico) se leen con el comercio, el importe y la cuenta, y un QR con un carácter cambiado muestra el aviso de CRC.

**Tests:** parser TLV con plantillas anidadas, CRC16 (casos válidos y alterados), validación de CVU/CBU, CPF y CNPJ.

### PR 1.2.5 · Facturas de América Latina
Cada formato es un módulo de `clipqr/fiscal/` sobre la base del PR 1.2.2, con su validador de identificador fiscal. Se puede dividir en un PR por país si se prefiere.

| País | Sistema | Cómo se reconoce | Datos principales | Verificación |
|---|---|---|---|---|
| **México** | CFDI (SAT) | URL `verificacfdi.facturaelectronica.sat.gob.mx` con `id` (UUID), `re`, `rr`, `tt`, `fe` | RFC del emisor y del receptor (validados), total, UUID | Abrir la URL del SAT |
| **Chile** | DTE (SII) | PDF417 con el timbre electrónico `<TED>` (XML) | RUT del emisor (módulo 11), tipo de DTE, folio, fecha, monto, RUT del receptor | Enlace de verificación del SII + «Copiar datos» |
| **Perú** | CPE (SUNAT) | Texto separado por `\|`: RUC, tipo, serie, número, IGV, total, fecha, tipo y número de documento del receptor | RUC (dígito verificador), serie-número, total, IGV | Página de consulta de SUNAT + «Copiar datos» |
| **Colombia** | Factura electrónica (DIAN) | Texto con `NumFac`, `FecFac`, `NitFac`, `ValTolFac`, `CUFE` y URL `catalogo-vpfe.dian.gov.co` | NIT (dígito verificador), número, total, CUFE | Abrir la URL de la DIAN |
| **Uruguay** | CFE (DGI) | URL de consulta de la DGI con RUC, tipo, serie, número, monto, fecha y código de seguridad | RUC, tipo y número, monto | Abrir la URL de la DGI |
| **Brasil** | NFC-e / NF-e (SEFAZ) | URL de la SEFAZ del estado con la clave de acceso de 44 dígitos | Clave desglosada: estado, fecha, CNPJ (validado), modelo, serie, número | Abrir la URL de la SEFAZ |
| **Ecuador** | Comprobante electrónico (SRI) | Clave de acceso de 49 dígitos | Clave desglosada: fecha, tipo, RUC, serie, secuencial, con su dígito verificador | «Copiar clave» + página de consulta del SRI |

**Hecho cuando:** cada país tiene al menos dos fixtures reales anonimizados que se leen bien, y un identificador fiscal alterado muestra el aviso.

### PR 1.2.6 · Facturas y pagos de Europa
| País | Sistema | Datos principales |
|---|---|---|
| **España** | **VeriFactu:** URL de cotejo de la AEAT con `nif`, `numserie`, `fecha`, `importe` | NIF (validado), número, fecha, importe; «Comprobar en la AEAT» |
| **España** | **TicketBAI:** URLs de las haciendas forales con `id`, `s`, `nf`, `i`, `cr` | NIF, serie y número, importe, territorio |
| **Portugal** | **ATCUD:** texto `A:…*B:…*…` (campos separados por `*`) | NIF del emisor y del cliente, tipo, fecha, ATCUD, total, IVA |
| **Zona SEPA** | **Transferencia EPC («GiroCode»):** líneas que empiezan por `BCD` | Beneficiario, IBAN (validado), BIC, importe, concepto. Solo copiar |
| **Suiza** | **QR-factura:** líneas que empiezan por `SPC` | Acreedor, IBAN/QR-IBAN, importe, moneda, referencia. Solo copiar |

**Hecho cuando:** igual que en el PR 1.2.5, con fixtures reales.

### PR 1.2.7 · Productos y medicamentos (GS1)
**Objetivo:** los envases están pasando del código de barras al QR (GS1 Digital Link), y los medicamentos llevan un DataMatrix con lote y vencimiento.

**Cambios** (tipo `product`, ampliado):
- **Qué se reconoce:**
  - **GS1 Digital Link:** URLs con `/01/<GTIN>` y, opcionalmente, `/10/<lote>`, `/17/<vencimiento>`, `/21/<serie>`, en cualquier dominio. Es el estándar mundial.
  - **Cadenas GS1 con identificadores de aplicación** (DataMatrix de medicamentos, `]d2…` o con separador FNC1): GTIN (01), lote (10), vencimiento (17), fecha de fabricación (11), serie (21), cantidad (30)…
  - **EAN/UPC** como hasta ahora, ahora con su dígito de control validado.
- **Aviso:**
  - **Titular:** el GTIN.
  - **Datos:** lote, serie, fabricación y **vencimiento**, en una franja roja si está vencido y ámbar si vence en menos de 30 días.
  - **País de origen del prefijo GS1:** solo informativo (779 = Argentina, 84 = España…).
- **Acciones:** «Buscar producto ↗» y, si es un Digital Link, «Abrir página del fabricante ↗».

**Hecho cuando:** un DataMatrix real de un medicamento muestra el lote y el vencimiento correctos, y un producto vencido muestra la franja roja.

**Tests:** identificadores GS1 de largo fijo y variable (con FNC1), fechas `AAMMDD` (con día `00` = fin de mes) y dígito de control del GTIN.

### PR 1.2.8 · Documentos de identidad y tarjetas de embarque
**Objetivo:** leer los códigos PDF417 que traen datos estructurados, cuidando la privacidad.

**Cambios**
- **DNI argentino (PDF417):** campos separados por `@`: número de trámite, apellido, nombre, sexo, DNI, ejemplar, nacimiento y emisión. Se reconocen el formato actual y el anterior.
  - **Titular:** «APELLIDO, Nombre».
  - **Datos:** DNI con puntos, nacimiento y emisión.
  - **Privacidad:**
    - los documentos de identidad **nunca** se guardan en el historial (ni en memoria ni en disco);
    - el aviso no se queda fijo;
    - la miniatura se difumina.
  - Otros documentos con formato público y estable (licencias de conducir de otros países con AAMVA) pueden añadirse después con el mismo cuidado.
- **Tarjetas de embarque (IATA BCBP, empiezan por `M1`):** pasajero, localizador, origen → destino, aerolínea y vuelo, fecha (día juliano convertido), asiento y secuencia.
  - **Titular:** «EZE → MAD · AR 1132».
  - **Privacidad:** el localizador cuenta como dato sensible y se trata igual que el DNI.

**Hecho cuando:** un DNI de prueba (o un ejemplo con datos ficticios en el formato oficial) se muestra bien y **no** aparece en el historial; las tarjetas de embarque de uno y varios tramos se leen.

**Tests:** los dos formatos de DNI, BCBP de un tramo y de varios, y que estos tipos no se añadan al historial.

### PR 1.2.9 · Más tipos de enlace y mensajería

| Tipo | Se reconoce por | Muestra | Botón |
|---|---|---|---|
| WhatsApp | `wa.me/…`, `api.whatsapp.com/send` | Número y mensaje | «Abrir chat» |
| Telegram | `t.me/…` | Usuario o canal | «Abrir en Telegram» |
| UPI (India) | `upi://pay?pa=…&pn=…&am=…` | Beneficiario, ID y importe | **Solo copiar** |
| Criptomonedas | `bitcoin:`, `ethereum:`… | Dirección y cantidad | **Solo copiar** |
| Tiendas de apps | Microsoft Store, Google Play, App Store | Nombre de la tienda | — |
| Redes sociales | Instagram, X, LinkedIn, YouTube, TikTok | Icono y nombre de la red | — |
| Calendario | `.ics` como texto o enlace | Igual que un evento | — |

**Tests:** una tabla con un ejemplo de cada tipo.

**Cierre de la 1.2.0:** notas, capturas nuevas (Crear QR, factura ARCA, pago QR, medicamento), etiqueta `v1.2.0`.

---

## 1.3.0 — Más formas de escanear y de guardar

### PR 1.3.1 · Arrastrar imágenes y PDF
**Objetivo:** escanear archivos sin copiarlos; muy útil con facturas en PDF.

**Cambios**
- Arrastrar imágenes o PDF al icono del escritorio o a la ventana del historial los escanea.
- **PDF:** con `pypdfium2`, cada página a 200 ppp y como mucho 20 páginas. Indica en qué página está cada código.
- Clic derecho en el Explorador › «Escanear con ClipQR»: lo registra el instalador en `HKCU\Software\Classes\SystemFileAssociations\image\shell` y `…\.pdf\shell`, y lo quita la desinstalación.
- Línea de órdenes:
  ```bash
  ClipQR.exe archivo.pdf
  ```
  Abre el aviso. Con `--json` escribe el resultado por la salida estándar, con los campos de `Comprobante` cuando es una factura, para usarlo en scripts y planillas.

**Hecho cuando:** un PDF de factura de ARCA con el QR en la página 2 muestra el aviso con «Página 2».

### PR 1.3.2 · Escanear varias facturas a la vez
**Objetivo:** pasar comprobantes a una planilla sin teclearlos.

**Cambios**
- Ventana «Lote»: arrastras varios PDF o imágenes y se arma una tabla. Cada factura es una fila con fecha, emisor, tipo, número, importe, moneda, código de autorización y avisos.
- **Exportar:** CSV y Excel (`.xlsx`). Las columnas siguen la estructura `Comprobante`.
- **Duplicados:** las facturas repetidas (mismo emisor, tipo y número) se marcan.

**Hecho cuando:** 20 PDF de facturas de distintos países se exportan a un Excel correcto en menos de 30 s.

### PR 1.3.3 · Historial guardado (opcional)
**Objetivo:** no perder lo escaneado al cerrar.

**Cambios**
- Configuración › Historial: «Guardar el historial al cerrar» (desactivado por defecto).
- **Almacenamiento:** `%APPDATA%\ClipQR\history.bin`, cifrado con DPAPI (`CryptProtectData`, ligado al usuario de Windows). Guarda solo texto, formato, hora y una miniatura pequeña. Los documentos de identidad y las tarjetas de embarque nunca se guardan (PR 1.2.8).
- **Borrado:** «Borrar historial» elimina también el archivo. La desinstalación lo borra.
- **Historial:** agrupado por días, con filtro por tipo (facturas, pagos, enlaces…) y opción de fijar elementos.

**Hecho cuando:** el historial sobrevive a un reinicio, y el archivo no se puede leer desde otra cuenta de Windows.

**Tests:** ida y vuelta de cifrado; el archivo nunca contiene el texto en claro.

### PR 1.3.4 · Webcam
- Bandeja › «Escanear con la cámara»: ventana con la imagen en vivo, que lee el QR en cuanto aparece y se cierra sola.
- **Implementación:** Windows Media Foundation (vía `winrt` ya incluido) para no añadir OpenCV. Si no hay cámara, la opción no aparece.

**Hecho cuando:** un QR mostrado en el móvil delante de la webcam se lee en menos de 2 s.

### PR 1.3.5 · Rendimiento y tamaño
- **Escanear en un proceso aparte** (o con hilos y menos intentos) las capturas grandes sin QR, que hoy tardan ~0,4 s, para que nunca afecten a la interfaz.
- **Probar Nuitka** frente a PyInstaller: tamaño, arranque y falsos positivos de antivirus. Se adopta si mejora al menos dos de los tres.
- **Medición automática:** `tests/bench_*.py` mide el arranque, el primer aviso y la decodificación. Su resultado se publica como artefacto del workflow para detectar si alguna versión empeora.

**Cierre de la 1.3.0.**

---

## 1.4.0 — Alcance

### PR 1.4.1 · Idiomas: inglés y portugués
- Todos los textos se mueven a `i18n/es.json`, `i18n/en.json` e `i18n/pt.json`, con una función `t("clave")`. El portugués es por Brasil y Portugal, que ya tienen formatos en la 1.2.
- El idioma se elige automáticamente según el de Windows y se puede cambiar en Configuración.
- **Formato de números y fechas:** según el país del comprobante (no el idioma de la interfaz).
- README en inglés (`README.en.md`) y ficha de la Store en inglés y portugués.

**Tests:** las mismas claves en todos los idiomas; ningún texto visible fuera de `t()`.

### PR 1.4.2 · Accesibilidad
- Nombres accesibles para los lectores de pantalla (Narrador, NVDA) en botones e iconos. Los glifos sin texto llevan descripción.
- Modo de alto contraste de Windows: se respetan los colores del sistema.
- Tamaño de texto configurable (100–150 %).

**Hecho cuando:** con el Narrador se oye el tipo y el dato principal al aparecer el aviso.

### PR 1.4.3 · Publicación en la Microsoft Store
- Comprobar el MSIX con el Windows App Certification Kit en el workflow.
- Capturas de 1366×768 o más para la Store (escenas completas en `tools/screenshots.py`), incluidas una factura de ARCA y un pago QR.
- Primer envío en Partner Center ([DISTRIBUCION.md §5](DISTRIBUCION.md#5-microsoft-store)), con la ficha en español, inglés y portugués.

**Cierre de la 1.4.0.**

---

## Ideas para más adelante (sin especificar)
- **Formatos aportados por la comunidad:** facturas o pagos de otros países con un archivo de reglas (patrón → campos → validaciones → acciones) en vez de código, para que cualquiera pueda añadir su país con un PR pequeño.
- **Sincronizar el historial** entre equipos mediante una carpeta elegida (OneDrive), siempre cifrado.
- **Reglas automáticas configurables** («si es una factura de ARCA, copiar el resumen al portapapeles»), siempre desactivadas por defecto.
- **Versión para macOS/Linux:** el núcleo (lectura, interpretación y `fiscal/`) ya sería portable tras el PR 1.0.1.
