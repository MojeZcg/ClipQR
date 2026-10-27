"""Catálogo Русский: texto en español -> traducción."""
TEXTS = {
    'Código QR':
        'QR-код',
    'Nombre':
        'Имя',
    'Teléfono':
        'Телефон',
    'Empresa':
        'Компания',
    'Cargo':
        'Должность',
    'Dirección':
        'Адрес',
    'Nota':
        'Заметка',
    'Evento':
        'Событие',
    'Inicio':
        'Начало',
    'Fin':
        'Конец',
    'Lugar':
        'Место',
    'Descripción':
        'Описание',
    'Red (SSID)':
        'Сеть (SSID)',
    'Número':
        'Номер',
    'Coordenadas':
        'Координаты',
    'Código':
        'Код',
    'Emisor':
        'Издатель',
    'Cuenta':
        'Учётная запись',
    'Dominio':
        'Домен',
    'Texto':
        'Текст',
    'Guardar contacto':
        'Сохранить контакт',
    'Contacto':
        'Контакт',
    'Ubicación':
        'Местоположение',
    'Enlace':
        'Ссылка',
    'Producto':
        'Товар',
    'Llamar':
        'Позвонить',
    'Escribir email':
        'Написать письмо',
    'Abrir web ↗':
        'Открыть сайт ↗',
    'Buscar en Google ↗':
        'Найти в Google ↗',
    'Añadir al calendario':
        'Добавить в календарь',
    'Secreto':
        'Секретный ключ',
    'Asunto':
        'Тема',
    'Mensaje':
        'Сообщение',
    'Enviar SMS':
        'Отправить SMS',
    'Ver en el mapa ↗':
        'Показать на карте ↗',
    'Servidor':
        'Сервер',
    'Abrir enlace ↗':
        'Открыть ссылку ↗',
    'Buscar producto ↗':
        'Найти товар ↗',
    'Contraseña':
        'Пароль',
    'Seguridad':
        'Безопасность',
    'Conectar a la red':
        'Подключиться к сети',
    'Los pagos con criptomonedas no se pueden revertir: comprueba la dirección completa antes de pagar':
        'Криптовалютные платежи нельзя отменить: перед оплатой проверьте адрес полностью',
    '{red} · empresa':
        '{red} · компания',
    '{red} · perfil':
        '{red} · профиль',
    '{red} · publicación':
        '{red} · публикация',
    'Pago QR · UPI':
        'Оплата по QR · UPI',
    'Cripto · {moneda}':
        'Криптовалюта · {moneda}',
    'WhatsApp · grupo':
        'WhatsApp · группа',
    'Abrir chat en WhatsApp ↗':
        'Открыть чат в WhatsApp ↗',
    'Abre el chat; el mensaje no se envía hasta que lo mandes tú':
        'Открывает чат; сообщение не отправится, пока вы его не отправите',
    'Telegram · grupo':
        'Telegram · группа',
    'Usuario':
        'Имя пользователя',
    'YouTube · vídeo':
        'YouTube · видео',
    'Calendario':
        'Календарь',
    'La dirección UPI no tiene la forma usuario@banco':
        'Адрес UPI не в формате пользователь@банк',
    'Importe':
        'Сумма',
    'Cobra':
        'Получатель',
    'Para {nombre}':
        'Для: {nombre}',
    'Red':
        'Сеть',
    'Destinatario':
        'Получатель',
    'Invitación a un grupo':
        'Приглашение в группу',
    'Copiar número':
        'Копировать номер',
    'Abrir en Telegram ↗':
        'Открыть в Telegram ↗',
    'Copiar usuario':
        'Копировать имя пользователя',
    'Vídeo de YouTube':
        'Видео YouTube',
    'Abrir en {red} ↗':
        'Открыть в {red} ↗',
    'Tienda':
        'Магазин',
    'Identificador':
        'ID',
    'Copiar dirección UPI':
        'Копировать адрес UPI',
    'Copiar dirección':
        'Копировать адрес',
    'Invitación':
        'Приглашение',
    'Unirse al grupo en WhatsApp ↗':
        'Вступить в группу в WhatsApp ↗',
    'Unirse en Telegram ↗':
        'Вступить в Telegram ↗',
    'Vídeo':
        'Видео',
    'Ver en YouTube ↗':
        'Смотреть на YouTube ↗',
    'GitHub · repositorio':
        'GitHub · репозиторий',
    'Suscribirse al calendario ↗':
        'Подписаться на календарь ↗',
    'Copiar enlace':
        'Копировать ссылку',
    'Dirección UPI':
        'Адрес UPI',
    'Concepto':
        'Описание',
    'Repositorio':
        'Репозиторий',
    'Abrir en GitHub ↗':
        'Открыть в GitHub ↗',
    'Copiar «git clone»':
        'Копировать «git clone»',
    'Publicación':
        'Публикация',
    'QR de pago alterado o dañado (el código de control no coincide)':
        'Платёжный QR-код изменён или повреждён (контрольная сумма не совпадает)',
    'Brasil':
        'Бразилия',
    'México':
        'Мексика',
    'Perú':
        'Перу',
    'Compra de bienes':
        'Покупка товаров',
    'Salario':
        'Зарплата',
    'Alquiler':
        'Аренда',
    'Donación':
        'Пожертвование',
    'Pago a proveedor':
        'Оплата поставщику',
    'Impuestos':
        'Налоги',
    'La clave Pix parece un CPF pero no es válido':
        'Ключ Pix похож на CPF, но недействителен',
    'La clave Pix parece un CNPJ pero no es válido':
        'Ключ Pix похож на CNPJ, но недействителен',
    'Pago QR · {red}':
        'Оплата по QR · {red}',
    'Pago QR':
        'Оплата по QR',
    'Sin importe: lo eliges en la app al pagar':
        'Сумма не указана: вы введёте её в приложении при оплате',
    'Transferencia SEPA inmediata':
        'Мгновенный перевод SEPA',
    'Transferencia SEPA':
        'Перевод SEPA',
    'QR-factura suiza':
        'Швейцарский QR-счёт',
    'Factura':
        'Счёт',
    'Referencia':
        'Референс',
    'Terminal':
        'Терминал',
    'Copiar código de pago':
        'Копировать платёжный код',
    'El IBAN no es válido (dígitos de control)':
        'IBAN недействителен (контрольные цифры)',
    'Copiar IBAN':
        'Копировать IBAN',
    'Beneficiario':
        'Бенефициар',
    'QR de transferencia incompleto o con un formato que no se reconoce':
        'QR-код перевода неполный или в нераспознанном формате',
    'Motivo':
        'Назначение',
    'QR-factura suiza incompleta o con un formato que no se reconoce':
        'Швейцарский QR-счёт неполный или в нераспознанном формате',
    'Clave Pix':
        'Ключ Pix',
    'Cobro Pix':
        'Счёт Pix',
    'El {cuenta} no es válido (dígito verificador)':
        '{cuenta} недействителен (контрольная цифра)',
    'Ciudad':
        'Город',
    'País':
        'Страна',
    'Tipo':
        'Тип',
    'QR de un solo cobro':
        'QR-код для одного платежа',
    'Comercio':
        'Продавец',
    'Copiar clave Pix':
        'Копировать ключ Pix',
    'Copiar {cuenta}':
        'Копировать {cuenta}',
    'Copiar referencia':
        'Копировать референс',
    'El importe no tiene el formato «EUR123.45»':
        'Сумма не в формате «EUR123.45»',
    'Referencia QR':
        'QR-референс',
    'Referencia ISO 11649':
        'Референс ISO 11649',
    'Localidad':
        'Населённый пункт',
    'Tipo de referencia':
        'Тип референса',
    'SSCC (envío)':
        'SSCC (отправка)',
    'GTIN contenido':
        'Вложенный GTIN',
    'Lote':
        'Партия',
    'Fabricado':
        'Дата производства',
    'Vence el pago':
        'Срок оплаты',
    'Envasado':
        'Дата упаковки',
    'Consumir preferentemente antes de':
        'Употребить до',
    'Vender antes de':
        'Продать до',
    'Vencimiento':
        'Срок годности',
    'Variante':
        'Вариант',
    'Número de serie':
        'Серийный номер',
    'Variante de consumo':
        'Вариант потребительского товара',
    'Cantidad':
        'Количество',
    'Unidades':
        'Штук',
    'Pieza del cliente':
        'Номер детали клиента',
    'Serie secundaria':
        'Дополнительный серийный номер',
    'Pedido':
        'Номер заказа',
    'Enviar a (GLN)':
        'Доставить в (GLN)',
    'Ubicación (GLN)':
        'Местоположение (GLN)',
    'País de origen':
        'Страна происхождения',
    'Vence (fecha y hora)':
        'Срок годности (дата и время)',
    'Peso neto':
        'Вес нетто',
    'Largo':
        'Длина',
    'Peso bruto':
        'Вес брутто',
    'Precio':
        'Цена',
    'EE. UU. y Canadá':
        'США и Канада',
    'EE. UU.':
        'США',
    'Francia':
        'Франция',
    'Alemania':
        'Германия',
    'Japón':
        'Япония',
    'Rusia':
        'Россия',
    'Taiwán':
        'Тайвань',
    'Filipinas':
        'Филиппины',
    'Reino Unido':
        'Великобритания',
    'Grecia':
        'Греция',
    'Irlanda':
        'Ирландия',
    'Bélgica y Luxemburgo':
        'Бельгия и Люксембург',
    'Dinamarca':
        'Дания',
    'Polonia':
        'Польша',
    'Sudáfrica':
        'ЮАР',
    'Noruega':
        'Норвегия',
    'Suecia':
        'Швеция',
    'Panamá':
        'Панама',
    'República Dominicana':
        'Доминиканская Республика',
    'Canadá':
        'Канада',
    'Suiza':
        'Швейцария',
    'Italia':
        'Италия',
    'España':
        'Испания',
    'Eslovaquia':
        'Словакия',
    'República Checa':
        'Чехия',
    'Turquía':
        'Турция',
    'Países Bajos':
        'Нидерланды',
    'Corea del Sur':
        'Южная Корея',
    'Tailandia':
        'Таиланд',
    'Singapur':
        'Сингапур',
    'Nueva Zelanda':
        'Новая Зеландия',
    'Malasia':
        'Малайзия',
    'Revista (ISSN)':
        'Журнал (ISSN)',
    'Libro (ISBN)':
        'Книга (ISBN)',
    'Uso interno de la tienda':
        'Внутренний код магазина',
    'Producto · GS1':
        'Товар · GS1',
    'El dígito verificador del GTIN no cuadra: el código puede estar mal leído':
        'Контрольная цифра GTIN не совпадает: код мог быть считан неверно',
    'Ver en GS1 ↗':
        'Посмотреть в GS1 ↗',
    'Abrir enlace del fabricante ↗':
        'Открыть ссылку производителя ↗',
    'Código GS1':
        'Код GS1',
    'Registrado en':
        'Зарегистрирован в',
    'Producto vencido el {fecha}':
        'Срок годности товара истёк {fecha}',
    'Pasó la fecha de consumo preferente ({fecha})':
        'Рекомендуемый срок употребления истёк ({fecha})',
    'Vence hoy':
        'Срок годности истекает сегодня',
    'Vence en {dias} día':
        'Срок годности истекает, осталось дней: {dias}',
    'Vence en {dias} días':
        'Срок годности истекает, осталось дней: {dias}',
    'Lote {lote}':
        'Партия {lote}',
    'Vence {fecha}':
        'Годен до {fecha}',
    'Datos personales: no se guardan en el historial':
        'Персональные данные: не сохраняются в истории',
    'Masculino':
        'Мужской',
    'Femenino':
        'Женский',
    'No binario':
        'Небинарный',
    'Primera':
        'Первый',
    'Turista premium':
        'Премиум-эконом',
    'Turista':
        'Эконом',
    'no va al historial':
        'не сохраняется в истории',
    'Tarjeta de embarque':
        'Посадочный талон',
    'Apellido':
        'Фамилия',
    'Sexo':
        'Пол',
    'Nacimiento':
        'Дата рождения',
    'Emisión':
        'Дата выдачи',
    'Ejemplar':
        'Копировать',
    'Número de trámite':
        'Номер оформления',
    'Copiar DNI':
        'Копировать DNI',
    'Copiar nombre completo':
        'Копировать ФИО',
    'Titular':
        'Владелец',
    'Pasajero':
        'Пассажир',
    'Vuelo':
        'Рейс',
    'Origen':
        'Откуда',
    'Destino':
        'Куда',
    'Reserva':
        'Код бронирования',
    'Copiar reserva':
        'Копировать код бронирования',
    'Estado del vuelo ↗':
        'Статус рейса ↗',
    'Fecha':
        'Дата',
    'Asiento':
        'Место',
    'Clase':
        'Класс',
    'Secuencia':
        'Порядковый номер',
    'Tramos':
        'Сегменты',
    'Comprobante':
        'Налоговый документ',
    'Copiar resumen':
        'Копировать сводку',
    'Verificar en {organismo} ↗':
        'Проверить в {organismo} ↗',
    'Cotización':
        'Курс обмена',
    'Receptor':
        'Получатель',
    'Autorización':
        'Авторизация',
    'Verificación':
        'Проверка',
}
