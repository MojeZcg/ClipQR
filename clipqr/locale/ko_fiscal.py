"""Catálogo 한국어: texto en español -> traducción."""
TEXTS = {
    'QR de factura incompleto o modificado':
        '청구서 QR이 불완전하거나 변경되었습니다',
    'Comprobante':
        '세금 문서',
    'Documento':
        '문서',
    'Receptor':
        '받는 사람',
    'Consumidor final':
        '최종 소비자',
    'Pasaporte':
        '여권',
    'Factura':
        '청구서',
    'Nota de crédito':
        '대변 메모',
    'Nota de débito':
        '차변 메모',
    'Recibo':
        '영수증',
    'Guía de remisión':
        '납품서',
    'Copiar clave':
        '액세스 키 복사',
    'Clave de acceso':
        '액세스 키',
    'Copiar datos':
        '세부 정보 복사',
    'Emisión':
        '발행일',
    'Serie':
        '시리즈',
    'RUC emisor':
        '발행자 RUC',
    'Factura electrónica':
        '전자 청구서',
    'Nota de crédito electrónica':
        '전자 대변 메모',
    'Nota de débito electrónica':
        '전자 차변 메모',
    'El valor total «{total}» no es válido':
        '총액 “{total}”이(가) 유효하지 않습니다',
    'El monto «{monto}» no es un importe válido':
        '금액 “{monto}”이(가) 유효한 금액이 아닙니다',
    'La fecha de emisión «{fecha}» no es válida':
        '발행일 “{fecha}”이(가) 유효하지 않습니다',
    'El RUC del emisor ({ruc}) no es válido: el QR puede estar modificado':
        '발행자의 RUC({ruc})가 유효하지 않습니다. QR이 변경되었을 수 있습니다',
    'Factura A':
        '청구서 A',
    'Nota de débito A':
        '차변 메모 A',
    'Nota de crédito A':
        '대변 메모 A',
    'Recibo A':
        '영수증 A',
    'Factura B':
        '청구서 B',
    'Nota de débito B':
        '차변 메모 B',
    'Nota de crédito B':
        '대변 메모 B',
    'Recibo B':
        '영수증 B',
    'Factura C':
        '청구서 C',
    'Nota de débito C':
        '차변 메모 C',
    'Nota de crédito C':
        '대변 메모 C',
    'Recibo C':
        '영수증 C',
    'Factura E':
        '청구서 E',
    'Nota de débito E':
        '차변 메모 E',
    'Nota de crédito E':
        '대변 메모 E',
    'Factura M':
        '청구서 M',
    'Nota de débito M':
        '차변 메모 M',
    'Nota de crédito M':
        '대변 메모 M',
    'Recibo M':
        '영수증 M',
    'Factura de crédito MiPyME A':
        'MiPyME 신용 청구서 A',
    'Nota de débito MiPyME A':
        'MiPyME 차변 메모 A',
    'Nota de crédito MiPyME A':
        'MiPyME 대변 메모 A',
    'Factura de crédito MiPyME B':
        'MiPyME 신용 청구서 B',
    'Nota de débito MiPyME B':
        'MiPyME 차변 메모 B',
    'Nota de crédito MiPyME B':
        'MiPyME 대변 메모 B',
    'Factura de crédito MiPyME C':
        'MiPyME 신용 청구서 C',
    'Nota de débito MiPyME C':
        'MiPyME 차변 메모 C',
    'Nota de crédito MiPyME C':
        'MiPyME 대변 메모 C',
    'CI extranjera':
        '외국인 신분증',
    '{doc} receptor':
        '받는 사람 {doc}',
    'CUIT emisor':
        '발행자 CUIT',
    'CUIT emisor: {cuit}':
        '발행자 CUIT: {cuit}',
    'Tipo: {tipo}':
        '유형: {tipo}',
    'Punto de venta: {pto}':
        '판매 지점: {pto}',
    'Número: {nro}':
        '번호: {nro}',
    'Fecha: {fecha}':
        '날짜: {fecha}',
    'Importe: {importe}':
        '금액: {importe}',
    'Comprobante tipo {tipo}':
        '세금 문서 유형 {tipo}',
    'El CUIT del emisor no es válido (dígito verificador)':
        '발행자의 CUIT가 유효하지 않습니다(검증 숫자)',
    'Falta el {codigo} o no tiene 14 dígitos':
        '{codigo}이(가) 없거나 14자리가 아닙니다',
    'La fecha del comprobante es futura':
        '문서 날짜가 미래입니다',
    'Constatar comprobante ↗':
        'ARCA에서 문서 확인 ↗',
    'Copiar datos para constatar':
        '확인용 세부 정보 복사',
    '{rfc} (público en general)':
        '{rfc}(일반 대중)',
    '{rfc} (residente en el extranjero)':
        '{rfc}(외국 거주자)',
    'El total «{total}» no es un importe válido':
        '총액 “{total}”이(가) 유효한 금액이 아닙니다',
    'Factura (CFDI)':
        '청구서(CFDI)',
    'El RFC del emisor ({rfc}) no es válido: el QR puede estar modificado':
        '발행자의 RFC({rfc})가 유효하지 않습니다. QR이 변경되었을 수 있습니다',
    'El RFC del receptor ({rfc}) no es válido: el QR puede estar modificado':
        '받는 사람의 RFC({rfc})가 유효하지 않습니다. QR이 변경되었을 수 있습니다',
    'El folio fiscal (UUID) «{uuid}» no tiene el formato del SAT':
        '세금 폴리오(UUID) “{uuid}”이(가) SAT 형식이 아닙니다',
    'Sello (últimos 8)':
        '디지털 인장(마지막 8자리)',
    'RFC emisor':
        '발행자 RFC',
    'RFC receptor':
        '받는 사람 RFC',
    'Folio fiscal (UUID)':
        '세금 폴리오(UUID)',
    'el SAT':
        'SAT',
    'Factura de inicio':
        '사업 개시 청구서',
    'Factura exenta':
        '면세 청구서',
    'Factura exenta electrónica':
        '전자 면세 청구서',
    'Boleta':
        '영수증(boleta)',
    'Boleta exenta':
        '면세 영수증(boleta)',
    'Boleta electrónica':
        '전자 영수증(boleta)',
    'Boleta exenta electrónica':
        '전자 면세 영수증(boleta)',
    'Liquidación factura':
        '정산 청구서',
    'Liquidación factura electrónica':
        '전자 정산 청구서',
    'Factura de compra':
        '매입 청구서',
    'Factura de compra electrónica':
        '전자 매입 청구서',
    'Comprobante de pago electrónico':
        '전자 지불 증빙',
    'Guía de despacho':
        '발송 전표',
    'Guía de despacho electrónica':
        '전자 발송 전표',
    'Factura de exportación electrónica':
        '전자 수출 청구서',
    'Nota de débito de exportación electrónica':
        '전자 수출 차변 메모',
    'Nota de crédito de exportación electrónica':
        '전자 수출 대변 메모',
    'Documento tributario electrónico (tipo {tipo})':
        '전자 세금 문서(유형 {tipo})',
    'El RUT del emisor ({rut}) no es válido: el timbre puede estar modificado':
        '발행자의 RUT({rut})가 유효하지 않습니다. 전자 스탬프가 변경되었을 수 있습니다',
    'El RUT del receptor ({rut}) no es válido: el timbre puede estar modificado':
        '받는 사람의 RUT({rut})가 유효하지 않습니다. 전자 스탬프가 변경되었을 수 있습니다',
    'El folio «{folio}» no es un número':
        '폴리오 “{folio}”이(가) 숫자가 아닙니다',
    'Razón social receptor':
        '받는 사람 회사명',
    'Monto total (moneda de la operación)':
        '총액(거래 통화)',
    'Primer ítem':
        '첫 번째 품목',
    'Timbrado':
        '스탬프 시각',
    'RUT emisor':
        '발행자 RUT',
    'RUT receptor':
        '받는 사람 RUT',
    'el SII':
        'SII',
    'N° {folio}':
        '번호 {folio}',
    'Tipo de documento':
        '문서 유형',
    'Folio':
        '폴리오',
    'Fecha de emisión':
        '발행일',
    'Monto total':
        '총액',
    'Boleta de venta electrónica':
        '전자 판매 영수증(boleta)',
    'Guía de remisión remitente':
        '발송인 납품서',
    'Ticket de máquina registradora':
        '금전 등록기 영수증',
    'Recibo de servicios públicos':
        '공과금 고지서',
    'Comprobante de retención electrónico':
        '전자 원천징수 증명서',
    'Guía de remisión transportista':
        '운송인 납품서',
    'Comprobante de percepción electrónico':
        '전자 징수 증명서(percepción)',
    'Doc. tributario no domiciliado':
        '비거주자 세금 문서',
    'Carné de extranjería':
        '외국인 신분증',
    'Cédula diplomática':
        '외교관 신분증',
    'Doc. del país de residencia':
        '거주 국가 신분증',
    'Adquirente':
        '구매자',
    '{doc} adquirente':
        '구매자 {doc}',
    'Comprobante electrónico (tipo {tipo})':
        '전자 세금 문서(유형 {tipo})',
    'El número «{numero}» no es válido':
        '번호 “{numero}”이(가) 유효하지 않습니다',
    'El importe total «{total}» no es válido':
        '총액 “{total}”이(가) 유효하지 않습니다',
    'El RUC del adquirente ({ruc}) no es válido':
        '구매자의 RUC({ruc})가 유효하지 않습니다',
    'Valor resumen':
        '요약 값',
    'Valor antes de impuestos':
        '세전 금액',
    'Otros impuestos':
        '기타 세금',
    'Impuestos':
        '세금',
    'El NIT del facturador «{nit}» no es un número válido: el QR puede estar modificado':
        '발행자의 NIT “{nit}”이(가) 유효한 번호가 아닙니다. QR이 변경되었을 수 있습니다',
    'El NIT del facturador ({nit}) no es válido: el QR puede estar modificado':
        '발행자의 NIT({nit})가 유효하지 않습니다. QR이 변경되었을 수 있습니다',
    'Documento electrónico':
        '전자 문서',
    'Factura electrónica de venta':
        '전자 판매 청구서',
    'El {codigo} no tiene el formato de la DIAN':
        '{codigo}이(가) DIAN 형식이 아닙니다',
    'La fecha de la factura «{fecha}» no es válida':
        '청구서 날짜 “{fecha}”이(가) 유효하지 않습니다',
    'El CUFE no coincide con el del enlace de la DIAN: el QR puede estar modificado':
        'CUFE가 DIAN 링크의 값과 일치하지 않습니다. QR이 변경되었을 수 있습니다',
    'Documento del ambiente de habilitación (pruebas) de la DIAN':
        'DIAN 테스트 환경의 문서',
    'Hora':
        '시간',
    'NIT facturador':
        '발행자 NIT',
    'Documento adquirente':
        '구매자 ID',
    'la DIAN':
        'DIAN',
    'Nota de crédito de e-Ticket':
        'e-Ticket 대변 메모',
    'Nota de débito de e-Ticket':
        'e-Ticket 차변 메모',
    'Nota de crédito de e-Factura':
        'e-Factura 대변 메모',
    'Nota de débito de e-Factura':
        'e-Factura 차변 메모',
    'e-Factura de exportación':
        '수출 e-Factura',
    'Nota de crédito de e-Factura de exportación':
        '수출 e-Factura 대변 메모',
    'Nota de débito de e-Factura de exportación':
        '수출 e-Factura 차변 메모',
    'e-Remito de exportación':
        '수출 전자 납품서',
    'e-Ticket venta por cuenta ajena':
        'e-Ticket(제3자 대리 판매)',
    'Nota de crédito de e-Ticket venta por cuenta ajena':
        'e-Ticket 대변 메모(제3자 대리 판매)',
    'Nota de débito de e-Ticket venta por cuenta ajena':
        'e-Ticket 차변 메모(제3자 대리 판매)',
    'e-Factura venta por cuenta ajena':
        'e-Factura(제3자 대리 판매)',
    'Nota de crédito de e-Factura venta por cuenta ajena':
        'e-Factura 대변 메모(제3자 대리 판매)',
    'Nota de débito de e-Factura venta por cuenta ajena':
        'e-Factura 차변 메모(제3자 대리 판매)',
    'e-Boleta de entrada':
        '입금 전자 영수증(e-Boleta)',
    'Nota de crédito de e-Boleta de entrada':
        '입금 전자 영수증 대변 메모',
    'Nota de débito de e-Boleta de entrada':
        '입금 전자 영수증 차변 메모',
    'CFE (tipo {tipo})':
        'CFE(유형 {tipo})',
    '{tipo} (contingencia)':
        '{tipo}(비상 모드)',
    'La fecha «{fecha}» no es válida':
        '날짜 “{fecha}”이(가) 유효하지 않습니다',
    'El número de comprobante «{numero}» no es válido':
        '문서 번호 “{numero}”이(가) 유효하지 않습니다',
    'Código de seguridad':
        '보안 코드',
    'normal':
        '일반',
    'contingencia FS-IA':
        'FS-IA 비상 모드',
    'contingencia SCAN':
        'SCAN 비상 모드',
    'contingencia EPEC':
        'EPEC 비상 모드',
    'contingencia FS-DA':
        'FS-DA 비상 모드',
    'contingencia SVC-AN':
        'SVC-AN 비상 모드',
    'contingencia SVC-RS':
        'SVC-RS 비상 모드',
    'contingencia offline':
        '오프라인 비상 모드',
    'CPF emisor':
        '발행자 CPF',
    'CNPJ emisor':
        '발행자 CNPJ',
    'La clave de acceso no supera el dígito verificador: el QR puede estar modificado':
        '액세스 키의 검증 숫자가 맞지 않습니다. QR이 변경되었을 수 있습니다',
    'El {doc} del emisor ({numero}) no es válido: el QR puede estar modificado':
        '발행자의 {doc}({numero})이(가) 유효하지 않습니다. QR이 변경되었을 수 있습니다',
    'Emitida en ambiente de homologación (pruebas): sin valor fiscal':
        '테스트(인증) 환경에서 발행됨: 세무상 효력 없음',
    'Estado':
        '주',
    'Mes de emisión':
        '발행 월',
    'Nota fiscal (modelo {modelo})':
        '세금 청구서(모델 {modelo})',
    'la {sefaz}':
        '{sefaz}',
    'tipo {tipo}':
        '유형 {tipo}',
    'Liquidación de compra':
        '매입 정산서',
    'Comprobante de retención':
        '원천징수 증명서',
    'El RUC del emisor ({ruc}) no supera la verificación: comprueba la clave en el SRI':
        '발행자의 RUC({ruc}) 검증에 실패했습니다. SRI에서 액세스 키를 확인하세요',
    'Comprobante del ambiente de pruebas: sin validez tributaria':
        '테스트 환경의 문서: 세무상 효력 없음',
    'Ambiente':
        '환경',
    'Pruebas':
        '테스트',
    'Producción':
        '운영',
    'Contingencia':
        '비상 모드',
    'el SRI':
        'SRI',
    'El NIF del emisor no es válido (letra o dígito de control incorrecto)':
        '발행자의 NIF가 유효하지 않습니다(검증 문자 또는 숫자 오류)',
    'La fecha de la factura es posterior a hoy':
        '청구서 날짜가 오늘 이후입니다',
    'NIF emisor':
        '발행자 NIF',
    'QR del entorno de pruebas de la AEAT':
        'AEAT 테스트 환경의 QR',
    'AEAT (no VERI*FACTU)':
        'AEAT(VERI*FACTU 아님)',
    'El enlace no es de la AEAT: apunta a {host}':
        'AEAT의 링크가 아닙니다. {host}(으)로 연결됩니다',
    'El enlace no es de la AEAT: apunta a un dominio desconocido':
        'AEAT의 링크가 아닙니다. 알 수 없는 도메인으로 연결됩니다',
    'Modalidad':
        '모드',
    'VERI*FACTU (verificable en la AEAT)':
        'VERI*FACTU(AEAT에서 확인 가능)',
    'Sistema no VERI*FACTU':
        'VERI*FACTU가 아닌 시스템',
    'Comprobar en la AEAT ↗':
        'AEAT에서 확인 ↗',
    'QR de TicketBAI alterado: el código de control no coincide':
        'TicketBAI QR이 변경되었습니다. 검증 코드가 일치하지 않습니다',
    'Identificador TicketBAI':
        'TicketBAI 식별자',
    'El enlace no es de ninguna Hacienda Foral: apunta a {host}':
        '바스크 지방 세무서(Hacienda Foral)의 링크가 아닙니다. {host}(으)로 연결됩니다',
    'El enlace no es de ninguna Hacienda Foral: apunta a un dominio desconocido':
        '바스크 지방 세무서(Hacienda Foral)의 링크가 아닙니다. 알 수 없는 도메인으로 연결됩니다',
    'QR del entorno de pruebas de TicketBAI':
        'TicketBAI 테스트 환경의 QR',
    'Hacienda Foral de {territorio}':
        '{territorio} 세무서(Hacienda Foral)',
    'Hacienda Foral':
        '바스크 지방 세무서(Hacienda Foral)',
    'Territorio':
        '지역',
    'Comprobar en Hacienda Foral ↗':
        'Hacienda Foral에서 확인 ↗',
    'Factura simplificada':
        '간이 청구서',
    'Factura-recibo':
        '청구서 겸 영수증',
    'Guía de transporte':
        '운송장',
    'Guía de movimiento de activos propios':
        '자사 고정 자산 이동 전표',
    'Guía de consignación':
        '위탁 전표',
    'Guía de devolución':
        '반품 전표',
    'Consulta de mesa':
        '테이블 계산서',
    'Crédito de consignación':
        '위탁 대변',
    'Factura de consignación':
        '위탁 청구서',
    'Hoja de obra':
        '작업 시트',
    'Nota de encargo':
        '주문서',
    'Otro documento':
        '기타 문서',
    'Presupuesto':
        '견적서',
    'Factura proforma':
        '견적 송장(Pro forma)',
    'Documento de conferencia':
        '배송 확인 문서',
    'Recibo de prima':
        '보험료 영수증',
    'Recibo de extorno':
        '보험료 환급 영수증',
    'Imputación a coaseguradoras':
        '공동 보험사 부과',
    'Imputación a coaseguradora líder':
        '주관 공동 보험사 부과',
    'Reaseguro aceptado':
        '수재 재보험',
    'Recibo (IVA de caja)':
        '영수증(현금주의 VAT)',
    'Normal':
        '일반',
    'Autofacturación':
        '자체 발행',
    'Anulado':
        '취소됨',
    'Documento de resumen':
        '요약 문서',
    'Facturado':
        '청구됨',
    'Por cuenta de terceros':
        '제3자 대리',
    'El NIF del emisor no es válido (dígito de control incorrecto)':
        '발행자의 NIF가 유효하지 않습니다(검증 숫자 오류)',
    'El NIF del adquirente no es válido (dígito de control incorrecto)':
        '구매자의 NIF가 유효하지 않습니다(검증 숫자 오류)',
    'La fecha del documento es posterior a hoy':
        '문서 날짜가 오늘 이후입니다',
    'Documento anulado':
        '취소된 문서',
    'Estado del documento':
        '문서 상태',
    'Espacio fiscal':
        '세무 지역',
    'Certificado del programa':
        '소프트웨어 인증서',
    'Otras informaciones':
        '기타 정보',
    'NIF adquirente':
        '구매자 NIF',
    'Total de impuestos':
        '세금 합계',
    'Documento {tipo}':
        '문서 {tipo}',
}
