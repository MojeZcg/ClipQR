"""Catálogo alemán (fiscal): texto en español -> traducción."""
TEXTS = {
    'QR de factura incompleto o modificado':
        'Rechnungs-QR unvollständig oder verändert',
    'Comprobante':
        'Steuerbeleg',
    'Documento':
        'Dokument',
    'Receptor':
        'Empfänger',
    'Consumidor final':
        'Endverbraucher',
    'Pasaporte':
        'Reisepass',
    'Factura':
        'Rechnung',
    'Nota de crédito':
        'Gutschrift',
    'Nota de débito':
        'Lastschriftanzeige',
    'Recibo':
        'Quittung',
    'Guía de remisión':
        'Lieferschein',
    'Copiar clave':
        'Schlüssel kopieren',
    'Clave de acceso':
        'Zugriffsschlüssel',
    'Copiar datos':
        'Daten kopieren',
    'Emisión':
        'Ausstellungsdatum',
    'Serie':
        'Serie',
    'RUC emisor':
        'RUC des Ausstellers',
    'Factura electrónica':
        'Elektronische Rechnung',
    'Nota de crédito electrónica':
        'Elektronische Gutschrift',
    'Nota de débito electrónica':
        'Elektronische Lastschriftanzeige',
    'El valor total «{total}» no es válido':
        'Der Gesamtbetrag „{total}“ ist ungültig',
    'El monto «{monto}» no es un importe válido':
        'Der Betrag „{monto}“ ist ungültig',
    'La fecha de emisión «{fecha}» no es válida':
        'Das Ausstellungsdatum „{fecha}“ ist ungültig',
    'El RUC del emisor ({ruc}) no es válido: el QR puede estar modificado':
        'Die RUC des Ausstellers ({ruc}) ist ungültig: Der QR-Code wurde möglicherweise verändert',
    'Factura A':
        'Rechnung A',
    'Nota de débito A':
        'Lastschriftanzeige A',
    'Nota de crédito A':
        'Gutschrift A',
    'Recibo A':
        'Quittung A',
    'Factura B':
        'Rechnung B',
    'Nota de débito B':
        'Lastschriftanzeige B',
    'Nota de crédito B':
        'Gutschrift B',
    'Recibo B':
        'Quittung B',
    'Factura C':
        'Rechnung C',
    'Nota de débito C':
        'Lastschriftanzeige C',
    'Nota de crédito C':
        'Gutschrift C',
    'Recibo C':
        'Quittung C',
    'Factura E':
        'Rechnung E',
    'Nota de débito E':
        'Lastschriftanzeige E',
    'Nota de crédito E':
        'Gutschrift E',
    'Factura M':
        'Rechnung M',
    'Nota de débito M':
        'Lastschriftanzeige M',
    'Nota de crédito M':
        'Gutschrift M',
    'Recibo M':
        'Quittung M',
    'Factura de crédito MiPyME A':
        'MiPyME-Kreditrechnung A',
    'Nota de débito MiPyME A':
        'MiPyME-Lastschriftanzeige A',
    'Nota de crédito MiPyME A':
        'MiPyME-Gutschrift A',
    'Factura de crédito MiPyME B':
        'MiPyME-Kreditrechnung B',
    'Nota de débito MiPyME B':
        'MiPyME-Lastschriftanzeige B',
    'Nota de crédito MiPyME B':
        'MiPyME-Gutschrift B',
    'Factura de crédito MiPyME C':
        'MiPyME-Kreditrechnung C',
    'Nota de débito MiPyME C':
        'MiPyME-Lastschriftanzeige C',
    'Nota de crédito MiPyME C':
        'MiPyME-Gutschrift C',
    'CI extranjera':
        'Ausländischer Ausweis',
    '{doc} receptor':
        '{doc} des Empfängers',
    'CUIT emisor':
        'CUIT des Ausstellers',
    'CUIT emisor: {cuit}':
        'CUIT des Ausstellers: {cuit}',
    'Tipo: {tipo}':
        'Typ: {tipo}',
    'Punto de venta: {pto}':
        'Verkaufsstelle: {pto}',
    'Número: {nro}':
        'Nummer: {nro}',
    'Fecha: {fecha}':
        'Datum: {fecha}',
    'Importe: {importe}':
        'Betrag: {importe}',
    'Comprobante tipo {tipo}':
        'Steuerbeleg Typ {tipo}',
    'El CUIT del emisor no es válido (dígito verificador)':
        'Die CUIT des Ausstellers ist ungültig (Prüfziffer)',
    'Falta el {codigo} o no tiene 14 dígitos':
        'Die {codigo} fehlt oder hat keine 14 Ziffern',
    'La fecha del comprobante es futura':
        'Das Belegdatum liegt in der Zukunft',
    'Constatar comprobante ↗':
        'Beleg bei ARCA prüfen ↗',
    'Copiar datos para constatar':
        'Daten für die Prüfung kopieren',
    '{rfc} (público en general)':
        '{rfc} (Allgemeinheit)',
    '{rfc} (residente en el extranjero)':
        '{rfc} (im Ausland ansässig)',
    'El total «{total}» no es un importe válido':
        'Der Gesamtbetrag „{total}“ ist kein gültiger Betrag',
    'Factura (CFDI)':
        'Rechnung (CFDI)',
    'El RFC del emisor ({rfc}) no es válido: el QR puede estar modificado':
        'Der RFC des Ausstellers ({rfc}) ist ungültig: Der QR-Code wurde möglicherweise verändert',
    'El RFC del receptor ({rfc}) no es válido: el QR puede estar modificado':
        'Der RFC des Empfängers ({rfc}) ist ungültig: Der QR-Code wurde möglicherweise verändert',
    'El folio fiscal (UUID) «{uuid}» no tiene el formato del SAT':
        'Das Steuerfolio (UUID) „{uuid}“ hat nicht das SAT-Format',
    'Sello (últimos 8)':
        'Digitales Siegel (letzte 8)',
    'RFC emisor':
        'RFC des Ausstellers',
    'RFC receptor':
        'RFC des Empfängers',
    'Folio fiscal (UUID)':
        'Steuerfolio (UUID)',
    'el SAT':
        'SAT',
    'Factura de inicio':
        'Rechnung bei Geschäftsaufnahme',
    'Factura exenta':
        'Steuerbefreite Rechnung',
    'Factura exenta electrónica':
        'Elektronische steuerbefreite Rechnung',
    'Boleta':
        'Kassenbeleg (Boleta)',
    'Boleta exenta':
        'Steuerbefreiter Kassenbeleg (Boleta)',
    'Boleta electrónica':
        'Elektronischer Kassenbeleg (Boleta)',
    'Boleta exenta electrónica':
        'Elektronischer steuerbefreiter Kassenbeleg (Boleta)',
    'Liquidación factura':
        'Abrechnungsrechnung',
    'Liquidación factura electrónica':
        'Elektronische Abrechnungsrechnung',
    'Factura de compra':
        'Einkaufsrechnung',
    'Factura de compra electrónica':
        'Elektronische Einkaufsrechnung',
    'Comprobante de pago electrónico':
        'Elektronischer Zahlungsbeleg',
    'Guía de despacho':
        'Versandschein',
    'Guía de despacho electrónica':
        'Elektronischer Versandschein',
    'Factura de exportación electrónica':
        'Elektronische Exportrechnung',
    'Nota de débito de exportación electrónica':
        'Elektronische Export-Lastschriftanzeige',
    'Nota de crédito de exportación electrónica':
        'Elektronische Export-Gutschrift',
    'Documento tributario electrónico (tipo {tipo})':
        'Elektronisches Steuerdokument (Typ {tipo})',
    'El RUT del emisor ({rut}) no es válido: el timbre puede estar modificado':
        'Der RUT des Ausstellers ({rut}) ist ungültig: Der elektronische Stempel wurde möglicherweise verändert',
    'El RUT del receptor ({rut}) no es válido: el timbre puede estar modificado':
        'Der RUT des Empfängers ({rut}) ist ungültig: Der elektronische Stempel wurde möglicherweise verändert',
    'El folio «{folio}» no es un número':
        'Das Folio „{folio}“ ist keine Zahl',
    'Razón social receptor':
        'Firmenname des Empfängers',
    'Monto total (moneda de la operación)':
        'Gesamtbetrag (Transaktionswährung)',
    'Primer ítem':
        'Erster Artikel',
    'Timbrado':
        'Gestempelt am',
    'RUT emisor':
        'RUT des Ausstellers',
    'RUT receptor':
        'RUT des Empfängers',
    'el SII':
        'SII',
    'N° {folio}':
        'Nr. {folio}',
    'Tipo de documento':
        'Dokumenttyp',
    'Folio':
        'Folio',
    'Fecha de emisión':
        'Ausstellungsdatum',
    'Monto total':
        'Gesamtbetrag',
    'Boleta de venta electrónica':
        'Elektronischer Verkaufsbeleg (Boleta)',
    'Guía de remisión remitente':
        'Lieferschein des Versenders',
    'Ticket de máquina registradora':
        'Registrierkassenbon',
    'Recibo de servicios públicos':
        'Rechnung für öffentliche Versorgungsleistungen',
    'Comprobante de retención electrónico':
        'Elektronische Einbehaltungsbescheinigung',
    'Guía de remisión transportista':
        'Lieferschein des Frachtführers',
    'Comprobante de percepción electrónico':
        'Elektronische Perzeptionsbescheinigung',
    'Doc. tributario no domiciliado':
        'Steuerdok. für Nichtansässige',
    'Carné de extranjería':
        'Ausländerausweis',
    'Cédula diplomática':
        'Diplomatenausweis',
    'Doc. del país de residencia':
        'Ausweis des Wohnsitzlandes',
    'Adquirente':
        'Erwerber',
    '{doc} adquirente':
        '{doc} des Erwerbers',
    'Comprobante electrónico (tipo {tipo})':
        'Elektronischer Beleg (Typ {tipo})',
    'El número «{numero}» no es válido':
        'Die Nummer „{numero}“ ist ungültig',
    'El importe total «{total}» no es válido':
        'Der Gesamtbetrag „{total}“ ist ungültig',
    'El RUC del adquirente ({ruc}) no es válido':
        'Die RUC des Erwerbers ({ruc}) ist ungültig',
    'Valor resumen':
        'Zusammenfassungswert',
    'Valor antes de impuestos':
        'Betrag vor Steuern',
    'Otros impuestos':
        'Sonstige Steuern',
    'Impuestos':
        'Steuern',
    'El NIT del facturador «{nit}» no es un número válido: el QR puede estar modificado':
        'Die NIT des Rechnungsstellers „{nit}“ ist keine gültige Nummer: Der QR-Code wurde möglicherweise verändert',
    'El NIT del facturador ({nit}) no es válido: el QR puede estar modificado':
        'Die NIT des Rechnungsstellers ({nit}) ist ungültig: Der QR-Code wurde möglicherweise verändert',
    'Documento electrónico':
        'Elektronisches Dokument',
    'Factura electrónica de venta':
        'Elektronische Verkaufsrechnung',
    'El {codigo} no tiene el formato de la DIAN':
        'Der {codigo} hat nicht das DIAN-Format',
    'La fecha de la factura «{fecha}» no es válida':
        'Das Rechnungsdatum „{fecha}“ ist ungültig',
    'El CUFE no coincide con el del enlace de la DIAN: el QR puede estar modificado':
        'Der CUFE stimmt nicht mit dem im DIAN-Link überein: Der QR-Code wurde möglicherweise verändert',
    'Documento del ambiente de habilitación (pruebas) de la DIAN':
        'Dokument aus der Testumgebung der DIAN',
    'Hora':
        'Uhrzeit',
    'NIT facturador':
        'NIT des Rechnungsstellers',
    'Documento adquirente':
        'Ausweis des Erwerbers',
    'la DIAN':
        'DIAN',
    'Nota de crédito de e-Ticket':
        'Gutschrift zum e-Ticket',
    'Nota de débito de e-Ticket':
        'Lastschriftanzeige zum e-Ticket',
    'Nota de crédito de e-Factura':
        'Gutschrift zur e-Factura',
    'Nota de débito de e-Factura':
        'Lastschriftanzeige zur e-Factura',
    'e-Factura de exportación':
        'Export-e-Factura',
    'Nota de crédito de e-Factura de exportación':
        'Gutschrift zur Export-e-Factura',
    'Nota de débito de e-Factura de exportación':
        'Lastschriftanzeige zur Export-e-Factura',
    'e-Remito de exportación':
        'Export-e-Remito',
    'e-Ticket venta por cuenta ajena':
        'e-Ticket (Verkauf für fremde Rechnung)',
    'Nota de crédito de e-Ticket venta por cuenta ajena':
        'Gutschrift zum e-Ticket (Verkauf für fremde Rechnung)',
    'Nota de débito de e-Ticket venta por cuenta ajena':
        'Lastschriftanzeige zum e-Ticket (Verkauf für fremde Rechnung)',
    'e-Factura venta por cuenta ajena':
        'e-Factura (Verkauf für fremde Rechnung)',
    'Nota de crédito de e-Factura venta por cuenta ajena':
        'Gutschrift zur e-Factura (Verkauf für fremde Rechnung)',
    'Nota de débito de e-Factura venta por cuenta ajena':
        'Lastschriftanzeige zur e-Factura (Verkauf für fremde Rechnung)',
    'e-Boleta de entrada':
        'Eingangs-e-Boleta',
    'Nota de crédito de e-Boleta de entrada':
        'Gutschrift zur Eingangs-e-Boleta',
    'Nota de débito de e-Boleta de entrada':
        'Lastschriftanzeige zur Eingangs-e-Boleta',
    'CFE (tipo {tipo})':
        'CFE (Typ {tipo})',
    '{tipo} (contingencia)':
        '{tipo} (Notfallbetrieb)',
    'La fecha «{fecha}» no es válida':
        'Das Datum „{fecha}“ ist ungültig',
    'El número de comprobante «{numero}» no es válido':
        'Die Belegnummer „{numero}“ ist ungültig',
    'Código de seguridad':
        'Sicherheitscode',
    'normal':
        'normal',
    'contingencia FS-IA':
        'Notfallbetrieb FS-IA',
    'contingencia SCAN':
        'Notfallbetrieb SCAN',
    'contingencia EPEC':
        'Notfallbetrieb EPEC',
    'contingencia FS-DA':
        'Notfallbetrieb FS-DA',
    'contingencia SVC-AN':
        'Notfallbetrieb SVC-AN',
    'contingencia SVC-RS':
        'Notfallbetrieb SVC-RS',
    'contingencia offline':
        'Notfallbetrieb offline',
    'CPF emisor':
        'CPF des Ausstellers',
    'CNPJ emisor':
        'CNPJ des Ausstellers',
    'La clave de acceso no supera el dígito verificador: el QR puede estar modificado':
        'Der Zugriffsschlüssel besteht die Prüfziffernkontrolle nicht: Der QR-Code wurde möglicherweise verändert',
    'El {doc} del emisor ({numero}) no es válido: el QR puede estar modificado':
        'Die {doc} des Ausstellers ({numero}) ist ungültig: Der QR-Code wurde möglicherweise verändert',
    'Emitida en ambiente de homologación (pruebas): sin valor fiscal':
        'In der Homologations-(Test-)Umgebung ausgestellt: steuerlich ungültig',
    'Estado':
        'Bundesstaat',
    'Mes de emisión':
        'Ausstellungsmonat',
    'Nota fiscal (modelo {modelo})':
        'Steuerrechnung (Modell {modelo})',
    'la {sefaz}':
        '{sefaz}',
    'tipo {tipo}':
        'Typ {tipo}',
    'Liquidación de compra':
        'Einkaufsabrechnung',
    'Comprobante de retención':
        'Einbehaltungsbescheinigung',
    'El RUC del emisor ({ruc}) no supera la verificación: comprueba la clave en el SRI':
        'Die RUC des Ausstellers ({ruc}) besteht die Prüfung nicht: Zugriffsschlüssel beim SRI prüfen',
    'Comprobante del ambiente de pruebas: sin validez tributaria':
        'Beleg aus der Testumgebung: steuerlich ungültig',
    'Ambiente':
        'Umgebung',
    'Pruebas':
        'Test',
    'Producción':
        'Produktion',
    'Contingencia':
        'Notfallbetrieb',
    'el SRI':
        'SRI',
    'El NIF del emisor no es válido (letra o dígito de control incorrecto)':
        'Die NIF des Ausstellers ist ungültig (falscher Prüfbuchstabe oder falsche Prüfziffer)',
    'La fecha de la factura es posterior a hoy':
        'Das Rechnungsdatum liegt nach dem heutigen Tag',
    'NIF emisor':
        'NIF des Ausstellers',
    'QR del entorno de pruebas de la AEAT':
        'QR-Code aus der Testumgebung der AEAT',
    'AEAT (no VERI*FACTU)':
        'AEAT (nicht VERI*FACTU)',
    'El enlace no es de la AEAT: apunta a {host}':
        'Der Link stammt nicht von der AEAT: Er verweist auf {host}',
    'El enlace no es de la AEAT: apunta a un dominio desconocido':
        'Der Link stammt nicht von der AEAT: Er verweist auf eine unbekannte Domain',
    'Modalidad':
        'Modus',
    'VERI*FACTU (verificable en la AEAT)':
        'VERI*FACTU (bei der AEAT überprüfbar)',
    'Sistema no VERI*FACTU':
        'System ohne VERI*FACTU',
    'Comprobar en la AEAT ↗':
        'Bei der AEAT prüfen ↗',
    'QR de TicketBAI alterado: el código de control no coincide':
        'TicketBAI-QR verändert: Der Prüfcode stimmt nicht',
    'Identificador TicketBAI':
        'TicketBAI-Kennung',
    'El enlace no es de ninguna Hacienda Foral: apunta a {host}':
        'Der Link stammt von keiner Hacienda Foral (baskische Steuerbehörde): Er verweist auf {host}',
    'El enlace no es de ninguna Hacienda Foral: apunta a un dominio desconocido':
        'Der Link stammt von keiner Hacienda Foral (baskische Steuerbehörde): Er verweist auf eine unbekannte Domain',
    'QR del entorno de pruebas de TicketBAI':
        'QR-Code aus der Testumgebung von TicketBAI',
    'Hacienda Foral de {territorio}':
        'Hacienda Foral de {territorio}',
    'Hacienda Foral':
        'Hacienda Foral (baskische Steuerbehörde)',
    'Territorio':
        'Territorium',
    'Comprobar en Hacienda Foral ↗':
        'Bei der Hacienda Foral prüfen ↗',
    'Factura simplificada':
        'Vereinfachte Rechnung',
    'Factura-recibo':
        'Rechnung mit Quittung',
    'Guía de transporte':
        'Transportbegleitschein',
    'Guía de movimiento de activos propios':
        'Begleitschein für eigenes Anlagevermögen',
    'Guía de consignación':
        'Konsignationsschein',
    'Guía de devolución':
        'Rücksendeschein',
    'Consulta de mesa':
        'Tischrechnung',
    'Crédito de consignación':
        'Konsignationsgutschrift',
    'Factura de consignación':
        'Konsignationsrechnung',
    'Hoja de obra':
        'Arbeitsblatt',
    'Nota de encargo':
        'Auftragsschein',
    'Otro documento':
        'Sonstiges Dokument',
    'Presupuesto':
        'Angebot',
    'Factura proforma':
        'Proformarechnung',
    'Documento de conferencia':
        'Abgleichsdokument',
    'Recibo de prima':
        'Prämienquittung',
    'Recibo de extorno':
        'Prämienerstattungsquittung',
    'Imputación a coaseguradoras':
        'Belastung der Mitversicherer',
    'Imputación a coaseguradora líder':
        'Belastung des führenden Mitversicherers',
    'Reaseguro aceptado':
        'Übernommene Rückversicherung',
    'Recibo (IVA de caja)':
        'Quittung (Ist-Versteuerung)',
    'Normal':
        'Normal',
    'Autofacturación':
        'Gutschriftverfahren',
    'Anulado':
        'Storniert',
    'Documento de resumen':
        'Sammeldokument',
    'Facturado':
        'Abgerechnet',
    'Por cuenta de terceros':
        'Für Rechnung Dritter',
    'El NIF del emisor no es válido (dígito de control incorrecto)':
        'Die NIF des Ausstellers ist ungültig (falsche Prüfziffer)',
    'El NIF del adquirente no es válido (dígito de control incorrecto)':
        'Die NIF des Erwerbers ist ungültig (falsche Prüfziffer)',
    'La fecha del documento es posterior a hoy':
        'Das Dokumentdatum liegt nach dem heutigen Tag',
    'Documento anulado':
        'Storniertes Dokument',
    'Estado del documento':
        'Dokumentstatus',
    'Espacio fiscal':
        'Steuergebiet',
    'Certificado del programa':
        'Softwarezertifikat',
    'Otras informaciones':
        'Weitere Angaben',
    'NIF adquirente':
        'NIF des Erwerbers',
    'Total de impuestos':
        'Steuern gesamt',
    'Documento {tipo}':
        'Dokument {tipo}',
}
