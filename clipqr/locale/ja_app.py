"""Catálogo 日本語: texto en español -> traducción."""
TEXTS = {
    'Windows no confirmó la conexión a «{red}».\nComprueba que la red está al alcance y que la contraseña es correcta.':
        'Windows で「{red}」への接続を確認できませんでした。\nネットワークが範囲内にあり、パスワードが正しいことを確認してください。',
    'Ya estás conectado a «{red}».':
        'すでに「{red}」に接続しています。',
    'No se pudo conectar.':
        '接続できませんでした。',
    'Conectado a «{red}».':
        '「{red}」に接続しました。',
    'No se pudo crear el perfil Wi‑Fi.':
        'Wi‑Fi プロファイルを作成できませんでした。',
    'Último: {texto}':
        '最新：{texto}',
    '{app} - en pausa':
        '{app} - 一時停止中',
    '{app} - vigilando portapapeles':
        '{app} - クリップボードを監視中',
    'ClipQR se ha desinstalado.':
        'ClipQR をアンインストールしました。',
    'El atajo {atajo} ya lo usa otra aplicación.\nPuedes elegir otro en Configuración › Atajos.':
        'ショートカット {atajo} は別のアプリで使用されています。\n［設定 › ショートカット］で別のものを選べます。',
    'Último: (nada todavía)':
        '最新：（まだありません）',
    'Abrir historial':
        '履歴を開く',
    'Escanear portapapeles ahora':
        '今すぐクリップボードをスキャン',
    'Configuración…':
        '設定…',
    'Invitar un cafecito ☕':
        'コーヒーをおごる ☕',
    'Pausar':
        '一時停止',
    'Iniciar con Windows':
        'Windows の起動時に開始',
    'Salir':
        '終了',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.\nSe iniciará solo con Windows.':
        'ClipQR は通知領域（時計の横）で動作しています。\nQR コードのスクリーンショットを撮ると、ここに表示されます。\nWindows の起動時に自動で開始します。',
    '✓ Copiado':
        '✓ コピーしました',
    'Desinstalar ClipQR':
        'ClipQR をアンインストール',
    '¿Quieres desinstalar ClipQR de este equipo?':
        'この PC から ClipQR をアンインストールしますか？',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.\nPuedes hacer que se inicie con Windows en Configuración (⚙).':
        'ClipQR は通知領域（時計の横）で動作しています。\nQR コードのスクリーンショットを撮ると、ここに表示されます。\n設定（⚙）で Windows の起動時に開始するようにできます。',
    'ClipQR está activo en la bandeja (junto al reloj).\nHaz una captura de un QR y aparecerá aquí.':
        'ClipQR は通知領域（時計の横）で動作しています。\nQR コードのスクリーンショットを撮ると、ここに表示されます。',
    'No se pudo reiniciar ClipQR.\n{error}':
        'ClipQR を再起動できませんでした。\n{error}',
    'No hay ninguna imagen en el portapapeles.':
        'クリップボードに画像がありません。',
    'No se encontró ningún QR en la imagen.':
        '画像に QR コードが見つかりません。',
    'No hay ninguna aplicación para abrir esto.\n{error}':
        'これを開けるアプリがありません。\n{error}',
    'Escanear zona de la pantalla':
        '画面の範囲をスキャン',
    'Crear QR…':
        'QR コードを作成…',
    'Actualizar a ClipQR {version}…':
        'ClipQR {version} に更新…',
    'Conectando…':
        '接続中…',
    'La conexión no está cifrada (http).':
        '接続は暗号化されていません（http）。',
    'El enlace no lleva a donde parece: el destino real es {host}.':
        'リンクの実際の行き先は見た目と異なります：本当の行き先は {host} です。',
    'Lleva a una dirección IP en vez de a un dominio.':
        'ドメインではなく IP アドレスに移動します。',
    'El dominio usa caracteres de otros alfabetos que pueden imitar a otro ({dominio}).':
        'このドメインには別のドメインになりすませる他の文字体系の文字が使われています（{dominio}）。',
    'Enlace acortado: no se sabe a dónde lleva hasta abrirlo.':
        '短縮リンク：開くまで行き先がわかりません。',
    'Ojo: el dominio real es {dominio}; lo de delante son subdominios.':
        '注意：本当のドメインは {dominio} です。その前の部分はサブドメインにすぎません。',
    'El enlace está mal formado.':
        'リンクの形式が正しくありません。',
    '(no hay errores registrados)':
        '（記録されたエラーはありません）',
    'Desactivado':
        'オフ',
    'Arriba a la derecha':
        '右上',
    'Abajo a la derecha':
        '右下',
    'En el centro':
        '中央',
    'Donde lo dejé al arrastrarlo':
        'ドラッグして置いた場所',
    'Espacio':
        'スペース',
    'La versión publicada no incluye el instalador o sus sumas de comprobación.':
        '公開されたリリースにインストーラーまたはそのチェックサムが含まれていません。',
    'SHA256SUMS.txt no tiene la suma del instalador.':
        'SHA256SUMS.txt にインストーラーのチェックサムがありません。',
    'El instalador descargado no coincide con su suma SHA-256: no se instala.':
        'ダウンロードしたインストーラーが SHA-256 チェックサムと一致しません。インストールは行いません。',
    'Windows no permite el inicio automático (directiva del equipo).':
        'Windows で自動起動が許可されていません（システム ポリシー）。',
    'Lo desactivaste desde Windows. Actívalo en\nConfiguración de Windows › Aplicaciones › Inicio.':
        'Windows でオフにされています。\nWindows の［設定 › アプリ › スタートアップ］でオンにしてください。',
    'No se pudo cambiar el inicio con Windows.\n{error}':
        'Windows の起動時の設定を変更できませんでした。\n{error}',
    'Texto o enlace':
        'テキストまたはリンク',
    'Contacto':
        '連絡先',
    'Teléfono':
        '電話',
    'Ubicación':
        '位置情報',
    'Negro':
        '黒',
    'Azul':
        '青',
    'Verde':
        '緑',
    'Morado':
        '紫',
    'Nombre de la red':
        'ネットワーク名',
    'Contraseña':
        'パスワード',
    'Nombre':
        '名前',
    'Empresa':
        '会社',
    'Web':
        'Web サイト',
    'Para':
        '宛先',
    'Asunto':
        '件名',
    'Mensaje':
        'メッセージ',
    'Número':
        '番号',
    'Número con prefijo de país':
        '国番号付きの番号',
    'Mensaje (opcional)':
        'メッセージ（任意）',
    'Latitud':
        '緯度',
    'Longitud':
        '経度',
    'Crear QR':
        'QR コードを作成',
    'Elige el tipo, rellena los datos y copia o guarda el código':
        '種類を選んで情報を入力し、コードをコピーまたは保存します',
    'TIPO':
        '種類',
    'DATOS':
        '情報',
    'OPCIONES':
        'オプション',
    'Copiar imagen':
        '画像をコピー',
    'Guardar PNG…':
        'PNG を保存…',
    'Guardar SVG…':
        'SVG を保存…',
    '✓ Se lee correctamente':
        '✓ 正しく読み取れます',
    'Usar mi Wi‑Fi actual':
        '現在の Wi‑Fi を使用',
    'Se leerá de Windows la red a la que estás conectado y su contraseña, y se mostrarán aquí. ¿Continuar?':
        '接続中のネットワークとそのパスワードを Windows から読み取り、ここに表示します。続行しますか？',
    '✓ Copiada':
        '✓ コピーしました',
    'No se pudo copiar':
        'コピーできませんでした',
    '✓ Guardado':
        '✓ 保存しました',
    'Guardar SVG':
        'SVG を保存',
    'El SVG se guarda sin el logo (solo el código).':
        'SVG はロゴなし（コードのみ）で保存されます。',
    'No estás conectado a ninguna Wi‑Fi.':
        'Wi‑Fi に接続していません。',
    'Corrección de errores':
        '誤り訂正',
    'Rellena los datos para ver el código.':
        '情報を入力するとコードが表示されます。',
    '(contraste justo: puede costar con algunas cámaras)':
        '（コントラストが低いため、一部のカメラでは読み取りにくい場合があります）',
    '✕ No se puede leer: prueba sin logo o con más corrección.':
        '✕ 読み取れません：ロゴなしにするか、誤り訂正レベルを上げてください。',
    'Logo de ClipQR en el centro (usa corrección H)':
        '中央に ClipQR のロゴ（レベル H を使用）',
    'Demasiado texto para un código QR.':
        'QR コードにするにはテキストが長すぎます。',
    'Imagen PNG':
        'PNG 画像',
    'Imagen SVG':
        'SVG 画像',
    'Red oculta':
        '非公開ネットワーク',
    'Copiar':
        'コピー',
    'Historial':
        '履歴',
    'Escanear ahora':
        '今すぐスキャン',
    'Sin resultados.':
        '結果はありません。',
    'Aún no se ha detectado ningún código.\nHaz una captura de un QR (Win+Shift+S o Impr Pant).':
        'まだコードは検出されていません。\nQR コードのスクリーンショットを撮ってください（Win+Shift+S または Print Screen）。',
    'Secreto':
        'シークレット',
    'Dominio':
        'ドメイン',
    'Arrástralo desde arriba · 📌 para fijarlo · Esc para cerrar':
        '上部をドラッグ · 📌 で固定 · Esc で閉じる',
    'Enter: acción · 1–9: copiar · Supr: borrar captura · Esc: cerrar':
        'Enter：操作 · 1–9：コピー · Del：スクリーンショットを削除 · Esc：閉じる',
    'Copiar todo':
        'すべてコピー',
    'Copiar selección':
        '選択部分をコピー',
    'Buscando la captura guardada…':
        '保存されたスクリーンショットを探しています…',
    'Captura enviada a la Papelera':
        'スクリーンショットをごみ箱に移動しました',
    'Borrar siempre':
        '常に削除',
    '🗑 Borrar captura':
        '🗑 スクリーンショットを削除',
    'Selecciona texto arriba':
        '上のテキストの一部を選択してください',
    '1 código detectado':
        '1 個のコードを検出しました',
    '{n} códigos detectados':
        '{n} 個のコードを検出しました',
    '+{n} más en el historial':
        '履歴にあと {n} 件',
    'Copiar  {n}':
        'コピー  {n}',
    'Captura: {archivo}':
        'スクリーンショット：{archivo}',
    'La captura ya no está en la carpeta':
        'スクリーンショットはフォルダーにありません',
    'No se pudo borrar':
        '削除できませんでした',
    'Arrastra alrededor del código  ·  Clic: toda la pantalla  ·  Esc: cancelar':
        'コードを囲むようにドラッグ  ·  クリック：画面全体  ·  Esc：キャンセル',
    'Configuración':
        '設定',
    '{app} {version} · los cambios se guardan al momento':
        '{app} {version} · 変更はすぐに保存されます',
    'AVISO':
        '通知',
    'Tiempo visible':
        '表示時間',
    'Cuánto tarda en cerrarse solo.':
        '自動で閉じるまでの時間です。',
    'Cerrar solo':
        '自動で閉じる',
    'Si lo desactivas, el aviso queda abierto hasta que lo cierres.':
        'オフにすると、通知は閉じるまで表示されたままになります。',
    'Pausar con el ratón encima':
        'マウスを重ねると一時停止',
    'La cuenta atrás se detiene mientras lo señalas.':
        'ポインターを合わせている間はカウントダウンが止まります。',
    'Animación de entrada':
        'スライドイン アニメーション',
    'Posición':
        '位置',
    'También puedes arrastrarlo desde su cabecera.':
        'ヘッダーをドラッグして移動することもできます。',
    'Probar':
        '試す',
    'Muestra un aviso de ejemplo con estos ajustes.':
        'この設定でサンプルの通知を表示します。',
    'APARIENCIA':
        '外観',
    'Tema':
        'テーマ',
    'DETECCIÓN':
        '検出',
    'Solo códigos QR':
        'QR コードのみ',
    'Desactivado: también lee códigos de barras (EAN, Code 128, DataMatrix…).':
        'オフにするとバーコード（EAN、Code 128、DataMatrix…）も読み取ります。',
    'Leer archivos copiados':
        'コピーしたファイルを読み取る',
    'Imágenes copiadas desde el Explorador de archivos.':
        'エクスプローラーからコピーした画像。',
    'Borrar las capturas con QR':
        'QR コードを含むスクリーンショットを削除',
    'Envía a la Papelera la captura que Windows guarda en Imágenes › Capturas de pantalla. Si está desactivado, el aviso muestra un botón para hacerlo.':
        'Windows が［ピクチャ › スクリーンショット］に保存したスクリーンショットをごみ箱に移動します。オフのときは、通知に削除用のボタンが表示されます。',
    'Mostrar contraseñas al momento':
        'パスワードをすぐに表示',
    'Contraseñas Wi‑Fi y secretos 2FA visibles sin pulsar el ojo. Desactivado es más seguro si alguien mira tu pantalla.':
        '目のアイコンをクリックしなくても Wi‑Fi のパスワードと 2 段階認証のシークレットが表示されます。画面を誰かに見られるおそれがある場合はオフのほうが安全です。',
    'Sonido al detectar':
        '検出時にサウンドを鳴らす',
    'Pausar la detección':
        '検出を一時停止',
    'No se escanea el portapapeles hasta que lo reactives.':
        '再びオンにするまでクリップボードはスキャンされません。',
    'HISTORIAL':
        '履歴',
    'Guardar hasta':
        '保持する件数',
    'Escaneos que se recuerdan mientras ClipQR está abierto.':
        'ClipQR を開いている間に記憶されるスキャン結果です。',
    'Borrar todo el historial':
        '履歴をすべて消去',
    'ATAJOS DE TECLADO':
        'キーボード ショートカット',
    'Escanear una zona de la pantalla':
        '画面の範囲をスキャン',
    'Congela la pantalla y lees el código que rodees, sin capturas ni portapapeles.':
        '画面を固定し、囲んだ範囲のコードを読み取ります。スクリーンショットもクリップボードも使いません。',
    'Crear un QR':
        'QR コードを作成',
    'Abre «Crear QR» con lo que tengas copiado.':
        'コピーした内容で「QR コードを作成」を開きます。',
    'Usar el aviso con el teclado':
        'キーボードで通知を操作',
    'Pasa el foco al aviso abierto. Luego: Enter = acción, 1–9 = copiar ese dato, Tab = moverse, Esc = cerrar.':
        '開いている通知にフォーカスを移します。その後は Enter = 操作、1–9 = その項目をコピー、Tab = 移動、Esc = 閉じる。',
    'GENERAL':
        '全般',
    'El idioma nuevo se aplica al reiniciar ClipQR.':
        '新しい言語は ClipQR の再起動後に適用されます。',
    'Informe de errores':
        'エラー レポート',
    'Copia la versión y los últimos errores para pegarlos en una incidencia de GitHub. No incluye imágenes ni el contenido de tus códigos; no se envía nada.':
        'バージョンと最近のエラーをコピーし、GitHub の Issue に貼り付けられるようにします。画像やコードの内容は含まれず、何も送信されません。',
    'APOYAR CLIPQR':
        'CLIPQR を支援',
    'ClipQR es gratis y de código abierto. Si te sirve, puedes apoyarlo con un cafecito en cafecito.app.':
        'ClipQR は無料のオープンソースです。役に立ったら、cafecito.app でコーヒーをおごって支援できます。',
    'Borrar historial':
        '履歴を消去',
    'Reiniciar ahora':
        '今すぐ再起動',
    'Copiar informe':
        'レポートをコピー',
    'Buscar actualizaciones':
        '更新を確認',
    'Una vez al día consulta las versiones publicadas en GitHub. Solo se instalan si las aceptas, y antes se comprueba que el instalador no está alterado.':
        '1 日に 1 回、GitHub で公開されているバージョンを確認します。インストールは同意した場合のみ行われ、改ざんされていないことを事前にインストーラーで検証します。',
    'Buscar ahora':
        '今すぐ確認',
    'Versión instalada: {version}':
        'インストール済みのバージョン：{version}',
    'Ver aviso de prueba':
        'テスト通知を表示',
    '✓ Borrado':
        '✓ 消去しました',
    'Invitar un cafecito ↗':
        'コーヒーをおごる ↗',
    'Automático (idioma del sistema)':
        '自動（システムの言語）',
    'Los cambios se guardan al momento.':
        '変更はすぐに保存されます。',
    'Arriba dcha.':
        '右上',
    'Abajo dcha.':
        '右下',
    'Centro':
        '中央',
    'Donde lo dejé':
        '前回置いた場所',
    'Como Windows':
        'システム',
    'Claro':
        'ライト',
    'Oscuro':
        'ダーク',
    'Tienes la {version}. Se descarga, se comprueba y se instala sola; tus ajustes se conservan.':
        '現在のバージョンは {version} です。自動でダウンロード、検証、インストールされ、設定はそのまま保持されます。',
    'Tienes la {version}. Descárgala desde GitHub.':
        '現在のバージョンは {version} です。GitHub からダウンロードしてください。',
    'ClipQR {version} disponible':
        'ClipQR {version} が利用可能です',
    'Las actualizaciones de la versión de la Microsoft Store las gestiona la Store.':
        'Microsoft Store 版の更新は Store が行います。',
    'Instalar':
        'インストール',
    'Ver novedades ↗':
        '新機能 ↗',
    'Ahora no':
        '後で',
    'Descargar ↗':
        'ダウンロード ↗',
    'Descargando…':
        'ダウンロード中…',
    'No se pudo actualizar.\n{error}':
        '更新できませんでした。\n{error}',
    'No se pudo consultar GitHub.\n{error}':
        'GitHub に接続できませんでした。\n{error}',
    'Tienes la última versión ({version}).':
        '最新バージョン（{version}）を使用しています。',
    'Avisar al iniciar':
        '起動時に通知を表示',
    'Un aviso breve confirma que ClipQR está activo cuando se abre.':
        '起動時に短い通知で ClipQR が動作していることを知らせます。',
    'Captura un QR o pulsa {atajo} para escanear una zona.':
        'QR コードのスクリーンショットを撮るか、{atajo} を押して範囲をスキャンします。',
    'Captura o copia un QR y aparecerá aquí.':
        'QR コードのスクリーンショットを撮るかコピーすると、ここに表示されます。',
    'ClipQR está activo':
        'ClipQR が動作しています',
    'Selecciona una parte con el ratón y pulsa Ctrl+C':
        'マウスで一部を選択して Ctrl+C を押してください',
}
