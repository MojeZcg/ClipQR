"""Catálogo 한국어: texto en español -> traducción."""
TEXTS = {
    'Windows no confirmó la conexión a «{red}».\nComprueba que la red está al alcance y que la contraseña es correcta.':
        'Windows에서 “{red}” 연결을 확인하지 못했습니다.\n네트워크가 범위 안에 있고 암호가 올바른지 확인하세요.',
    'Ya estás conectado a «{red}».':
        '이미 “{red}”에 연결되어 있습니다.',
    'No se pudo conectar.':
        '연결하지 못했습니다.',
    'Conectado a «{red}».':
        '“{red}”에 연결되었습니다.',
    'No se pudo crear el perfil Wi‑Fi.':
        'Wi‑Fi 프로필을 만들지 못했습니다.',
    'Último: {texto}':
        '최근: {texto}',
    '{app} - en pausa':
        '{app} - 일시 중지됨',
    '{app} - vigilando portapapeles':
        '{app} - 클립보드 감시 중',
    'ClipQR se ha desinstalado.':
        'ClipQR이 제거되었습니다.',
    'El atajo {atajo} ya lo usa otra aplicación.\nPuedes elegir otro en Configuración › Atajos.':
        '단축키 {atajo}은(는) 이미 다른 앱에서 사용 중입니다.\n설정 › 단축키에서 다른 단축키를 선택할 수 있습니다.',
    'Último: (nada todavía)':
        '최근: (아직 없음)',
    'Abrir historial':
        '기록 열기',
    'Escanear portapapeles ahora':
        '지금 클립보드 스캔',
    'Configuración…':
        '설정…',
    'Invitar un cafecito ☕':
        '커피 한 잔 후원하기 ☕',
    'Pausar':
        '일시 중지',
    'Iniciar con Windows':
        'Windows 시작 시 실행',
    'Salir':
        '종료',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.\nSe iniciará solo con Windows.':
        'ClipQR이 트레이(시계 옆)에서 실행 중입니다.\nQR 코드의 스크린샷을 찍으면 여기에 표시됩니다.\nWindows 시작 시 자동으로 실행됩니다.',
    '✓ Copiado':
        '✓ 복사됨',
    'Desinstalar ClipQR':
        'ClipQR 제거',
    '¿Quieres desinstalar ClipQR de este equipo?':
        '이 PC에서 ClipQR을 제거하시겠습니까?',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.\nPuedes hacer que se inicie con Windows en Configuración (⚙).':
        'ClipQR이 트레이(시계 옆)에서 실행 중입니다.\nQR 코드의 스크린샷을 찍으면 여기에 표시됩니다.\n설정(⚙)에서 Windows 시작 시 실행되도록 할 수 있습니다.',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.':
        'ClipQR이 트레이(시계 옆)에서 실행 중입니다.\nQR 코드의 스크린샷을 찍으면 여기에 표시됩니다.',
    'No se pudo reiniciar ClipQR.\n{error}':
        'ClipQR을 다시 시작하지 못했습니다.\n{error}',
    'No hay ninguna imagen en el portapapeles.':
        '클립보드에 이미지가 없습니다.',
    'No se encontró ningún QR en la imagen.':
        '이미지에서 QR 코드를 찾지 못했습니다.',
    'No hay ninguna aplicación para abrir esto.\n{error}':
        '이 항목을 열 수 있는 앱이 없습니다.\n{error}',
    'Escanear zona de la pantalla':
        '화면 영역 스캔',
    'Crear QR…':
        'QR 만들기…',
    'Actualizar a ClipQR {version}…':
        'ClipQR {version}(으)로 업데이트…',
    'Conectando…':
        '연결 중…',
    'La conexión no está cifrada (http).':
        '연결이 암호화되지 않았습니다(http).',
    'El enlace no lleva a donde parece: el destino real es {host}.':
        '링크가 보이는 곳으로 연결되지 않습니다. 실제 대상은 {host}입니다.',
    'Lleva a una dirección IP en vez de a un dominio.':
        '도메인 대신 IP 주소로 연결됩니다.',
    'El dominio usa caracteres de otros alfabetos que pueden imitar a otro ({dominio}).':
        '도메인에 다른 도메인을 흉내 낼 수 있는 다른 문자 체계의 문자가 있습니다({dominio}).',
    'Enlace acortado: no se sabe a dónde lleva hasta abrirlo.':
        '단축 링크: 열기 전에는 어디로 연결되는지 알 수 없습니다.',
    'Ojo: el dominio real es {dominio}; lo de delante son subdominios.':
        '주의: 실제 도메인은 {dominio}이며, 그 앞부분은 하위 도메인일 뿐입니다.',
    'El enlace está mal formado.':
        '링크 형식이 잘못되었습니다.',
    '(no hay errores registrados)':
        '(기록된 오류 없음)',
    'Desactivado':
        '끄기',
    'Arriba a la derecha':
        '오른쪽 위',
    'Abajo a la derecha':
        '오른쪽 아래',
    'En el centro':
        '가운데',
    'Donde lo dejé al arrastrarlo':
        '드래그해서 놓은 위치',
    'Espacio':
        'Space',
    'La versión publicada no incluye el instalador o sus sumas de comprobación.':
        '게시된 릴리스에 설치 프로그램 또는 체크섬이 없습니다.',
    'SHA256SUMS.txt no tiene la suma del instalador.':
        'SHA256SUMS.txt에 설치 프로그램의 체크섬이 없습니다.',
    'El instalador descargado no coincide con su suma SHA-256: no se instala.':
        '다운로드한 설치 프로그램이 SHA-256 체크섬과 일치하지 않아 설치하지 않습니다.',
    'Windows no permite el inicio automático (directiva del equipo).':
        'Windows에서 자동 시작을 허용하지 않습니다(시스템 정책).',
    'Lo desactivaste desde Windows. Actívalo en\nConfiguración de Windows › Aplicaciones › Inicio.':
        'Windows에서 꺼져 있습니다. 다음 위치에서 켜세요.\nWindows 설정 › 앱 › 시작 프로그램',
    'No se pudo cambiar el inicio con Windows.\n{error}':
        'Windows 시작 시 실행 설정을 변경하지 못했습니다.\n{error}',
    'Texto o enlace':
        '텍스트 또는 링크',
    'Contacto':
        '연락처',
    'Teléfono':
        '전화',
    'Ubicación':
        '위치',
    'Negro':
        '검정',
    'Azul':
        '파랑',
    'Verde':
        '초록',
    'Morado':
        '보라',
    'Nombre de la red':
        '네트워크 이름',
    'Contraseña':
        '암호',
    'Nombre':
        '이름',
    'Empresa':
        '회사',
    'Web':
        '웹사이트',
    'Para':
        '받는 사람',
    'Asunto':
        '제목',
    'Mensaje':
        '메시지',
    'Número':
        '번호',
    'Número con prefijo de país':
        '국가 번호를 포함한 번호',
    'Mensaje (opcional)':
        '메시지(선택 사항)',
    'Latitud':
        '위도',
    'Longitud':
        '경도',
    'Crear QR':
        'QR 만들기',
    'Elige el tipo, rellena los datos y copia o guarda el código':
        '유형을 선택하고 정보를 입력한 다음 코드를 복사하거나 저장하세요',
    'TIPO':
        '유형',
    'DATOS':
        '정보',
    'OPCIONES':
        '옵션',
    'Copiar imagen':
        '이미지 복사',
    'Guardar PNG…':
        'PNG 저장…',
    'Guardar SVG…':
        'SVG 저장…',
    '✓ Se lee correctamente':
        '✓ 정상적으로 스캔됨',
    'Usar mi Wi‑Fi actual':
        '현재 Wi‑Fi 사용',
    'Se leerá de Windows la red a la que estás conectado y su contraseña, y se mostrarán aquí. ¿Continuar?':
        '연결된 네트워크와 암호를 Windows에서 읽어 여기에 표시합니다. 계속하시겠습니까?',
    '✓ Copiada':
        '✓ 복사됨',
    'No se pudo copiar':
        '복사하지 못했습니다',
    '✓ Guardado':
        '✓ 저장됨',
    'Guardar SVG':
        'SVG 저장',
    'El SVG se guarda sin el logo (solo el código).':
        'SVG는 로고 없이 저장됩니다(코드만).',
    'No estás conectado a ninguna Wi‑Fi.':
        '연결된 Wi‑Fi가 없습니다.',
    'Corrección de errores':
        '오류 정정',
    'Rellena los datos para ver el código.':
        '코드를 보려면 정보를 입력하세요.',
    '(contraste justo: puede costar con algunas cámaras)':
        '(대비가 낮음: 일부 카메라에서 인식이 어려울 수 있음)',
    '✕ No se puede leer: prueba sin logo o con más corrección.':
        '✕ 스캔할 수 없음: 로고를 빼거나 오류 정정 수준을 높여 보세요.',
    'Logo de ClipQR en el centro (usa corrección H)':
        '가운데에 ClipQR 로고(H 수준 사용)',
    'Demasiado texto para un código QR.':
        'QR 코드에 넣기에는 텍스트가 너무 깁니다.',
    'Imagen PNG':
        'PNG 이미지',
    'Imagen SVG':
        'SVG 이미지',
    'Red oculta':
        '숨겨진 네트워크',
    'Copiar':
        '복사',
    'Historial':
        '기록',
    'Escanear ahora':
        '지금 스캔',
    'Sin resultados.':
        '결과가 없습니다.',
    'Aún no se ha detectado ningún código.\nHaz una captura de un QR (Win+Shift+S o Impr Pant).':
        '아직 감지된 코드가 없습니다.\nQR 코드의 스크린샷을 찍으세요(Win+Shift+S 또는 Print Screen).',
    'Secreto':
        '비밀 키',
    'Dominio':
        '도메인',
    'Arrástralo desde arriba · 📌 para fijarlo · Esc para cerrar':
        '위쪽을 끌어서 이동 · 📌 고정 · Esc 닫기',
    'Enter: acción · 1–9: copiar · Supr: borrar captura · Esc: cerrar':
        'Enter: 작업 · 1–9: 복사 · Del: 스크린샷 삭제 · Esc: 닫기',
    'Copiar todo':
        '모두 복사',
    'Copiar selección':
        '선택 영역 복사',
    'Buscando la captura guardada…':
        '저장된 스크린샷을 찾는 중…',
    'Captura enviada a la Papelera':
        '스크린샷을 휴지통으로 이동했습니다',
    'Borrar siempre':
        '항상 삭제',
    '🗑 Borrar captura':
        '🗑 스크린샷 삭제',
    'Selecciona texto arriba':
        '위의 텍스트 일부를 선택하세요',
    '1 código detectado':
        '코드 1개 감지됨',
    '{n} códigos detectados':
        '코드 {n}개 감지됨',
    '+{n} más en el historial':
        '기록에 +{n}개 더',
    'Copiar  {n}':
        '복사  {n}',
    'Captura: {archivo}':
        '스크린샷: {archivo}',
    'La captura ya no está en la carpeta':
        '스크린샷이 폴더에 더 이상 없습니다',
    'No se pudo borrar':
        '삭제하지 못했습니다',
    'Arrastra alrededor del código  ·  Clic: toda la pantalla  ·  Esc: cancelar':
        '코드 주위를 드래그  ·  클릭: 전체 화면  ·  Esc: 취소',
    'Configuración':
        '설정',
    '{app} {version} · los cambios se guardan al momento':
        '{app} {version} · 변경 사항은 즉시 저장됩니다',
    'AVISO':
        '알림',
    'Tiempo visible':
        '표시 시간',
    'Cuánto tarda en cerrarse solo.':
        '자동으로 닫힐 때까지의 시간입니다.',
    'Cerrar solo':
        '자동으로 닫기',
    'Si lo desactivas, el aviso queda abierto hasta que lo cierres.':
        '끄면 직접 닫을 때까지 알림이 열려 있습니다.',
    'Pausar con el ratón encima':
        '마우스를 올리면 일시 중지',
    'La cuenta atrás se detiene mientras lo señalas.':
        '포인터를 올려 두는 동안 카운트다운이 멈춥니다.',
    'Animación de entrada':
        '슬라이드 애니메이션',
    'Posición':
        '위치',
    'También puedes arrastrarlo desde su cabecera.':
        '머리글을 끌어서 옮길 수도 있습니다.',
    'Probar':
        '테스트',
    'Muestra un aviso de ejemplo con estos ajustes.':
        '이 설정으로 샘플 알림을 표시합니다.',
    'APARIENCIA':
        '모양',
    'Tema':
        '테마',
    'DETECCIÓN':
        '감지',
    'Solo códigos QR':
        'QR 코드만',
    'Desactivado: también lee códigos de barras (EAN, Code 128, DataMatrix…).':
        '끄면 바코드도 읽습니다(EAN, Code 128, DataMatrix…).',
    'Leer archivos copiados':
        '복사한 파일 읽기',
    'Imágenes copiadas desde el Explorador de archivos.':
        '파일 탐색기에서 복사한 이미지입니다.',
    'Mostrar contraseñas al momento':
        '암호 바로 표시',
    'Contraseñas Wi‑Fi y secretos 2FA visibles sin pulsar el ojo. Desactivado es más seguro si alguien mira tu pantalla.':
        '눈 아이콘을 클릭하지 않아도 Wi‑Fi 암호와 2FA 비밀 키가 표시됩니다. 다른 사람이 화면을 볼 수 있다면 끄는 것이 더 안전합니다.',
    'Sonido al detectar':
        '감지 시 소리',
    'Pausar la detección':
        '감지 일시 중지',
    'No se escanea el portapapeles hasta que lo reactives.':
        '다시 켤 때까지 클립보드를 스캔하지 않습니다.',
    'HISTORIAL':
        '기록',
    'Guardar hasta':
        '최대 보관 개수',
    'Escaneos que se recuerdan mientras ClipQR está abierto.':
        'ClipQR이 열려 있는 동안 기억하는 스캔 결과입니다.',
    'Borrar todo el historial':
        '모든 기록 지우기',
    'ATAJOS DE TECLADO':
        '바로 가기 키',
    'Escanear una zona de la pantalla':
        '화면 영역 스캔',
    'Congela la pantalla y lees el código que rodees, sin capturas ni portapapeles.':
        '화면을 정지하고 드래그한 영역의 코드를 읽습니다. 스크린샷이나 클립보드를 사용하지 않습니다.',
    'Crear un QR':
        'QR 코드 만들기',
    'Abre «Crear QR» con lo que tengas copiado.':
        '복사한 내용으로 “QR 만들기”를 엽니다.',
    'Usar el aviso con el teclado':
        '키보드로 알림 사용',
    'Pasa el foco al aviso abierto. Luego: Enter = acción, 1–9 = copiar ese dato, Tab = moverse, Esc = cerrar.':
        '열린 알림으로 포커스를 옮깁니다. 그다음 Enter = 작업, 1–9 = 해당 필드 복사, Tab = 이동, Esc = 닫기.',
    'GENERAL':
        '일반',
    'El idioma nuevo se aplica al reiniciar ClipQR.':
        '새 언어는 ClipQR을 다시 시작한 후 적용됩니다.',
    'Informe de errores':
        '오류 보고서',
    'Copia la versión y los últimos errores para pegarlos en una incidencia de GitHub. No incluye imágenes ni el contenido de tus códigos; no se envía nada.':
        '버전과 최근 오류를 복사하여 GitHub 이슈에 붙여 넣을 수 있습니다. 이미지나 코드 내용은 포함되지 않으며 아무것도 전송되지 않습니다.',
    'APOYAR CLIPQR':
        'ClipQR 후원',
    'ClipQR es gratis y de código abierto. Si te sirve, puedes apoyarlo con un cafecito en cafecito.app.':
        'ClipQR은 무료 오픈 소스입니다. 유용하다면 cafecito.app에서 커피 한 잔으로 후원할 수 있습니다.',
    'Borrar historial':
        '기록 지우기',
    'Reiniciar ahora':
        '지금 다시 시작',
    'Copiar informe':
        '보고서 복사',
    'Buscar actualizaciones':
        '업데이트 확인',
    'Una vez al día consulta las versiones publicadas en GitHub. Solo se instalan si las aceptas, y antes se comprueba que el instalador no está alterado.':
        '하루에 한 번 GitHub에 게시된 버전을 확인합니다. 동의한 경우에만 설치되며, 설치 프로그램이 변조되지 않았는지 먼저 확인합니다.',
    'Buscar ahora':
        '지금 확인',
    'Versión instalada: {version}':
        '설치된 버전: {version}',
    'Ver aviso de prueba':
        '테스트 알림 표시',
    '✓ Borrado':
        '✓ 지움',
    'Invitar un cafecito ↗':
        '커피 한 잔 후원하기 ↗',
    'Automático (idioma del sistema)':
        '자동(시스템 언어)',
    'Los cambios se guardan al momento.':
        '변경 사항은 즉시 저장됩니다.',
    'Arriba dcha.':
        '오른쪽 위',
    'Abajo dcha.':
        '오른쪽 아래',
    'Centro':
        '가운데',
    'Donde lo dejé':
        '마지막 위치',
    'Como Windows':
        '시스템',
    'Claro':
        '밝게',
    'Oscuro':
        '어둡게',
    'Tienes la {version}. Se descarga, se comprueba y se instala sola; tus ajustes se conservan.':
        '현재 버전은 {version}입니다. 자동으로 다운로드, 확인, 설치되며 설정은 유지됩니다.',
    'Tienes la {version}. Descárgala desde GitHub.':
        '현재 버전은 {version}입니다. GitHub에서 다운로드하세요.',
    'ClipQR {version} disponible':
        'ClipQR {version} 사용 가능',
    'Las actualizaciones de la versión de la Microsoft Store las gestiona la Store.':
        'Microsoft Store 업데이트는 Store에서 처리합니다.',
    'Instalar':
        '설치',
    'Ver novedades ↗':
        '새로운 기능 ↗',
    'Ahora no':
        '나중에',
    'Descargar ↗':
        '다운로드 ↗',
    'Descargando…':
        '다운로드 중…',
    'No se pudo actualizar.\n{error}':
        '업데이트하지 못했습니다.\n{error}',
    'No se pudo consultar GitHub.\n{error}':
        'GitHub에 연결하지 못했습니다.\n{error}',
    'Tienes la última versión ({version}).':
        '최신 버전({version})을 사용 중입니다.',
    'Avisar al iniciar':
        '시작 시 알림 표시',
    'Un aviso breve confirma que ClipQR está activo cuando se abre.':
        '시작할 때 ClipQR이 실행 중임을 짧은 알림으로 알려 줍니다.',
    'Captura un QR o pulsa {atajo} para escanear una zona.':
        'QR 코드를 스크린샷하거나 {atajo}을(를) 눌러 영역을 스캔하세요.',
    'Captura o copia un QR y aparecerá aquí.':
        'QR 코드를 스크린샷하거나 복사하면 여기에 표시됩니다.',
    'ClipQR está activo':
        'ClipQR 실행 중',
    'Selecciona una parte con el ratón y pulsa Ctrl+C':
        '마우스로 일부를 선택하고 Ctrl+C를 누르세요',
    'CAPTURAS':
        '스크린샷',
    'Borrar la captura al detectar un código':
        '코드를 감지하면 스크린샷 삭제',
    'Cuando una captura de pantalla tiene un QR o un código de barras, la envía a la Papelera (se puede recuperar) para no llenar Imágenes › Capturas de pantalla. Cada aviso indica que está activo.':
        '스크린샷에 QR 코드나 바코드가 있으면 휴지통으로 옮깁니다(복원 가능). 사진 › 스크린샷 폴더가 가득 차지 않게 해 줍니다. 켜져 있으면 알림마다 표시됩니다.',
    'Borrado automático desactivado':
        '자동 삭제를 껐습니다',
    'Desactivar':
        '끄기',
    'Borrado automático activo · buscando la captura…':
        '자동 삭제 켜짐 · 스크린샷을 찾는 중…',
    'Captura enviada a la Papelera (borrado automático)':
        '스크린샷을 휴지통으로 옮겼습니다(자동 삭제)',
    'Borrado automático activo · esta imagen no es una captura guardada':
        '자동 삭제 켜짐 · 이 이미지는 저장된 스크린샷이 아닙니다',
    'No se pudo mostrar el icono de ClipQR en la bandeja del sistema.\nClipQR sigue activo: usa la ventana del historial.':
        '시스템 트레이에 ClipQR 아이콘을 표시할 수 없습니다.\nClipQR는 계속 실행 중입니다. 기록 창을 사용하세요.',
    'Para leer el portapapeles, instala xclip (X11) o wl-clipboard (Wayland).':
        '클립보드를 읽으려면 xclip (X11) 또는 wl-clipboard (Wayland)를 설치하세요.',
    'Hace falta NetworkManager (nmcli) para conectarse a la Wi‑Fi.':
        'Wi‑Fi에 연결하려면 NetworkManager (nmcli)가 필요합니다.',
    'No se encontró la interfaz Wi‑Fi.':
        'Wi‑Fi 인터페이스를 찾을 수 없습니다.',
    'No se pudo capturar la pantalla.\nEn Wayland las aplicaciones no pueden capturarla: haz una captura con la herramienta del sistema y cópiala.':
        '화면을 캡처할 수 없습니다.\nWayland에서는 앱이 화면을 캡처할 수 없습니다. 시스템 도구로 스크린샷을 찍은 다음 복사하세요.',
    'No se pudo capturar la pantalla.\n{error}':
        '화면을 캡처할 수 없습니다.\n{error}',
    'Cuando una captura de pantalla tiene un QR o un código de barras, la envía a la Papelera (se puede recuperar) para no llenar la carpeta de capturas. Cada aviso indica que está activo.':
        '스크린샷에 QR 코드나 바코드가 있으면 스크린샷 폴더가 가득 차지 않도록 휴지통으로 이동합니다(복원할 수 있음). 알림마다 이 기능이 켜져 있음을 표시합니다.',
    'Se leerá del sistema la red a la que estás conectado y su contraseña, y se mostrarán aquí. ¿Continuar?':
        '현재 연결된 네트워크와 비밀번호를 시스템에서 읽어 여기에 표시합니다. 계속할까요?',
    'Iniciar al iniciar sesión':
        '로그인 시 시작',
    'Como el sistema':
        '시스템 설정에 따름',
    'Imágenes copiadas desde el gestor de archivos.':
        '파일 관리자에서 복사한 이미지입니다.',
    'Aún no se ha detectado ningún código.\nHaz una captura de un QR con ⌃⇧⌘4 (la copia al portapapeles).':
        '아직 감지된 코드가 없습니다.\n⌃⇧⌘4로 QR 코드를 스크린샷으로 찍으세요(클립보드에 복사됩니다).',
    'Aún no se ha detectado ningún código.\nHaz una captura de un QR (Impr Pant) y cópiala.':
        '아직 감지된 코드가 없습니다.\nQR 코드를 스크린샷(PrtSc)으로 찍어 복사하세요.',
    'ClipQR está activo en la barra de menús.\nHaz una captura de un QR y aparecerá aquí.\nSe iniciará solo al iniciar sesión.':
        'ClipQR가 메뉴 막대에서 실행 중입니다.\nQR 코드를 스크린샷으로 찍으면 여기에 표시됩니다.\n로그인 시 자동으로 시작됩니다.',
    'ClipQR está activo en la bandeja del sistema.\nHaz una captura de un QR y aparecerá aquí.\nSe iniciará solo al iniciar sesión.':
        'ClipQR가 시스템 트레이에서 실행 중입니다.\nQR 코드를 스크린샷으로 찍으면 여기에 표시됩니다.\n로그인 시 자동으로 시작됩니다.',
    'En Wayland las aplicaciones no pueden usar atajos de teclado globales.\nUsa el menú de ClipQR en la bandeja del sistema.':
        'Wayland에서는 앱이 전역 키보드 단축키를 사용할 수 없습니다.\n시스템 트레이의 ClipQR 메뉴를 사용하세요.',
    'Para usar los atajos de teclado, permite ClipQR en\nAjustes del Sistema › Privacidad y seguridad › Accesibilidad.':
        '키보드 단축키를 사용하려면\n시스템 설정 › 개인정보 보호 및 보안 › 손쉬운 사용에서 ClipQR를 허용하세요.',
    'Los atajos de teclado globales no están disponibles: falta el módulo pynput.':
        '전역 키보드 단축키를 사용할 수 없습니다. pynput 모듈이 없습니다.',
}
