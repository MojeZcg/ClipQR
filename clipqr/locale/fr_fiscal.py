"""Catálogo francés (fiscal): texto en español -> traducción."""
TEXTS = {
    'QR de factura incompleto o modificado':
        'QR de facture incomplet ou modifié',
    'Comprobante':
        'Justificatif fiscal',
    'Documento':
        'Document',
    'Receptor':
        'Destinataire',
    'Consumidor final':
        'Consommateur final',
    'Pasaporte':
        'Passeport',
    'Factura':
        'Facture',
    'Nota de crédito':
        'Avoir',
    'Nota de débito':
        'Note de débit',
    'Recibo':
        'Reçu',
    'Guía de remisión':
        'Bon de livraison',
    'Copiar clave':
        'Copier la clé',
    'Clave de acceso':
        "Clé d'accès",
    'Copiar datos':
        'Copier les données',
    'Emisión':
        "Date d'émission",
    'Serie':
        'Série',
    'RUC emisor':
        "RUC de l'émetteur",
    'Factura electrónica':
        'Facture électronique',
    'Nota de crédito electrónica':
        'Avoir électronique',
    'Nota de débito electrónica':
        'Note de débit électronique',
    'El valor total «{total}» no es válido':
        "Le montant total « {total} » n'est pas valide",
    'El monto «{monto}» no es un importe válido':
        "Le montant « {monto} » n'est pas valide",
    'La fecha de emisión «{fecha}» no es válida':
        "La date d'émission « {fecha} » n'est pas valide",
    'El RUC del emisor ({ruc}) no es válido: el QR puede estar modificado':
        "Le RUC de l'émetteur ({ruc}) n'est pas valide : le QR a peut-être été modifié",
    'Factura A':
        'Facture A',
    'Nota de débito A':
        'Note de débit A',
    'Nota de crédito A':
        'Avoir A',
    'Recibo A':
        'Reçu A',
    'Factura B':
        'Facture B',
    'Nota de débito B':
        'Note de débit B',
    'Nota de crédito B':
        'Avoir B',
    'Recibo B':
        'Reçu B',
    'Factura C':
        'Facture C',
    'Nota de débito C':
        'Note de débit C',
    'Nota de crédito C':
        'Avoir C',
    'Recibo C':
        'Reçu C',
    'Factura E':
        'Facture E',
    'Nota de débito E':
        'Note de débit E',
    'Nota de crédito E':
        'Avoir E',
    'Factura M':
        'Facture M',
    'Nota de débito M':
        'Note de débit M',
    'Nota de crédito M':
        'Avoir M',
    'Recibo M':
        'Reçu M',
    'Factura de crédito MiPyME A':
        'Facture de crédit MiPyME A',
    'Nota de débito MiPyME A':
        'Note de débit MiPyME A',
    'Nota de crédito MiPyME A':
        'Avoir MiPyME A',
    'Factura de crédito MiPyME B':
        'Facture de crédit MiPyME B',
    'Nota de débito MiPyME B':
        'Note de débit MiPyME B',
    'Nota de crédito MiPyME B':
        'Avoir MiPyME B',
    'Factura de crédito MiPyME C':
        'Facture de crédit MiPyME C',
    'Nota de débito MiPyME C':
        'Note de débit MiPyME C',
    'Nota de crédito MiPyME C':
        'Avoir MiPyME C',
    'CI extranjera':
        "Pièce d'identité étrangère",
    '{doc} receptor':
        '{doc} du destinataire',
    'CUIT emisor':
        "CUIT de l'émetteur",
    'CUIT emisor: {cuit}':
        "CUIT de l'émetteur : {cuit}",
    'Tipo: {tipo}':
        'Type : {tipo}',
    'Punto de venta: {pto}':
        'Point de vente : {pto}',
    'Número: {nro}':
        'Numéro : {nro}',
    'Fecha: {fecha}':
        'Date : {fecha}',
    'Importe: {importe}':
        'Montant : {importe}',
    'Comprobante tipo {tipo}':
        'Justificatif de type {tipo}',
    'El CUIT del emisor no es válido (dígito verificador)':
        "Le CUIT de l'émetteur n'est pas valide (chiffre de contrôle)",
    'Falta el {codigo} o no tiene 14 dígitos':
        "Le {codigo} est absent ou n'a pas 14 chiffres",
    'La fecha del comprobante es futura':
        'La date du justificatif est dans le futur',
    'Constatar comprobante ↗':
        "Vérifier le justificatif auprès de l'ARCA ↗",
    'Copiar datos para constatar':
        'Copier les données pour la vérification',
    '{rfc} (público en general)':
        '{rfc} (grand public)',
    '{rfc} (residente en el extranjero)':
        "{rfc} (résident à l'étranger)",
    'El total «{total}» no es un importe válido':
        "Le total « {total} » n'est pas un montant valide",
    'Factura (CFDI)':
        'Facture (CFDI)',
    'El RFC del emisor ({rfc}) no es válido: el QR puede estar modificado':
        "Le RFC de l'émetteur ({rfc}) n'est pas valide : le QR a peut-être été modifié",
    'El RFC del receptor ({rfc}) no es válido: el QR puede estar modificado':
        "Le RFC du destinataire ({rfc}) n'est pas valide : le QR a peut-être été modifié",
    'El folio fiscal (UUID) «{uuid}» no tiene el formato del SAT':
        "Le folio fiscal (UUID) « {uuid} » n'a pas le format du SAT",
    'Sello (últimos 8)':
        'Sceau numérique (8 derniers)',
    'RFC emisor':
        "RFC de l'émetteur",
    'RFC receptor':
        'RFC du destinataire',
    'Folio fiscal (UUID)':
        'Folio fiscal (UUID)',
    'el SAT':
        'SAT',
    'Factura de inicio':
        "Facture de début d'activité",
    'Factura exenta':
        'Facture exonérée',
    'Factura exenta electrónica':
        'Facture exonérée électronique',
    'Boleta':
        'Ticket (boleta)',
    'Boleta exenta':
        'Ticket exonéré (boleta)',
    'Boleta electrónica':
        'Ticket électronique (boleta)',
    'Boleta exenta electrónica':
        'Ticket exonéré électronique (boleta)',
    'Liquidación factura':
        'Facture de liquidation',
    'Liquidación factura electrónica':
        'Facture de liquidation électronique',
    'Factura de compra':
        "Facture d'achat",
    'Factura de compra electrónica':
        "Facture d'achat électronique",
    'Comprobante de pago electrónico':
        'Justificatif de paiement électronique',
    'Guía de despacho':
        "Bon d'expédition",
    'Guía de despacho electrónica':
        "Bon d'expédition électronique",
    'Factura de exportación electrónica':
        "Facture d'exportation électronique",
    'Nota de débito de exportación electrónica':
        "Note de débit d'exportation électronique",
    'Nota de crédito de exportación electrónica':
        "Avoir d'exportation électronique",
    'Documento tributario electrónico (tipo {tipo})':
        'Document fiscal électronique (type {tipo})',
    'El RUT del emisor ({rut}) no es válido: el timbre puede estar modificado':
        "Le RUT de l'émetteur ({rut}) n'est pas valide : le timbre a peut-être été modifié",
    'El RUT del receptor ({rut}) no es válido: el timbre puede estar modificado':
        "Le RUT du destinataire ({rut}) n'est pas valide : le timbre a peut-être été modifié",
    'El folio «{folio}» no es un número':
        "Le folio « {folio} » n'est pas un nombre",
    'Razón social receptor':
        'Raison sociale du destinataire',
    'Monto total (moneda de la operación)':
        "Montant total (devise de l'opération)",
    'Primer ítem':
        'Premier article',
    'Timbrado':
        'Horodaté le',
    'RUT emisor':
        "RUT de l'émetteur",
    'RUT receptor':
        'RUT du destinataire',
    'el SII':
        'SII',
    'N° {folio}':
        'N° {folio}',
    'Tipo de documento':
        'Type de document',
    'Folio':
        'Folio',
    'Fecha de emisión':
        "Date d'émission",
    'Monto total':
        'Montant total',
    'Boleta de venta electrónica':
        'Ticket de vente électronique (boleta)',
    'Guía de remisión remitente':
        "Bon de livraison de l'expéditeur",
    'Ticket de máquina registradora':
        'Ticket de caisse enregistreuse',
    'Recibo de servicios públicos':
        'Facture de services publics',
    'Comprobante de retención electrónico':
        'Certificat de retenue électronique',
    'Guía de remisión transportista':
        'Bon de livraison du transporteur',
    'Comprobante de percepción electrónico':
        'Certificat de perception électronique',
    'Doc. tributario no domiciliado':
        'Doc. fiscal de non-résident',
    'Carné de extranjería':
        'Carte de séjour',
    'Cédula diplomática':
        'Carte diplomatique',
    'Doc. del país de residencia':
        'Pièce du pays de résidence',
    'Adquirente':
        'Acquéreur',
    '{doc} adquirente':
        "{doc} de l'acquéreur",
    'Comprobante electrónico (tipo {tipo})':
        'Justificatif électronique (type {tipo})',
    'El número «{numero}» no es válido':
        "Le numéro « {numero} » n'est pas valide",
    'El importe total «{total}» no es válido':
        "Le montant total « {total} » n'est pas valide",
    'El RUC del adquirente ({ruc}) no es válido':
        "Le RUC de l'acquéreur ({ruc}) n'est pas valide",
    'Valor resumen':
        'Valeur de résumé',
    'Valor antes de impuestos':
        'Montant hors taxes',
    'Otros impuestos':
        'Autres taxes',
    'Impuestos':
        'Impôts',
    'El NIT del facturador «{nit}» no es un número válido: el QR puede estar modificado':
        "Le NIT de l'émetteur « {nit} » n'est pas un numéro valide : le QR a peut-être été modifié",
    'El NIT del facturador ({nit}) no es válido: el QR puede estar modificado':
        "Le NIT de l'émetteur ({nit}) n'est pas valide : le QR a peut-être été modifié",
    'Documento electrónico':
        'Document électronique',
    'Factura electrónica de venta':
        'Facture de vente électronique',
    'El {codigo} no tiene el formato de la DIAN':
        "Le {codigo} n'a pas le format de la DIAN",
    'La fecha de la factura «{fecha}» no es válida':
        "La date de la facture « {fecha} » n'est pas valide",
    'El CUFE no coincide con el del enlace de la DIAN: el QR puede estar modificado':
        'Le CUFE ne correspond pas à celui du lien de la DIAN : le QR a peut-être été modifié',
    'Documento del ambiente de habilitación (pruebas) de la DIAN':
        "Document de l'environnement de test de la DIAN",
    'Hora':
        'Heure',
    'NIT facturador':
        "NIT de l'émetteur",
    'Documento adquirente':
        "Pièce de l'acquéreur",
    'la DIAN':
        'DIAN',
    'Nota de crédito de e-Ticket':
        "Avoir d'e-Ticket",
    'Nota de débito de e-Ticket':
        "Note de débit d'e-Ticket",
    'Nota de crédito de e-Factura':
        "Avoir d'e-Factura",
    'Nota de débito de e-Factura':
        "Note de débit d'e-Factura",
    'e-Factura de exportación':
        "e-Factura d'exportation",
    'Nota de crédito de e-Factura de exportación':
        "Avoir d'e-Factura d'exportation",
    'Nota de débito de e-Factura de exportación':
        "Note de débit d'e-Factura d'exportation",
    'e-Remito de exportación':
        "e-Remito d'exportation",
    'e-Ticket venta por cuenta ajena':
        'e-Ticket (vente pour compte de tiers)',
    'Nota de crédito de e-Ticket venta por cuenta ajena':
        "Avoir d'e-Ticket (vente pour compte de tiers)",
    'Nota de débito de e-Ticket venta por cuenta ajena':
        "Note de débit d'e-Ticket (vente pour compte de tiers)",
    'e-Factura venta por cuenta ajena':
        'e-Factura (vente pour compte de tiers)',
    'Nota de crédito de e-Factura venta por cuenta ajena':
        "Avoir d'e-Factura (vente pour compte de tiers)",
    'Nota de débito de e-Factura venta por cuenta ajena':
        "Note de débit d'e-Factura (vente pour compte de tiers)",
    'e-Boleta de entrada':
        "e-Boleta d'entrée",
    'Nota de crédito de e-Boleta de entrada':
        "Avoir d'e-Boleta d'entrée",
    'Nota de débito de e-Boleta de entrada':
        "Note de débit d'e-Boleta d'entrée",
    'CFE (tipo {tipo})':
        'CFE (type {tipo})',
    '{tipo} (contingencia)':
        '{tipo} (contingence)',
    'La fecha «{fecha}» no es válida':
        "La date « {fecha} » n'est pas valide",
    'El número de comprobante «{numero}» no es válido':
        "Le numéro de justificatif « {numero} » n'est pas valide",
    'Código de seguridad':
        'Code de sécurité',
    'normal':
        'normal',
    'contingencia FS-IA':
        'contingence FS-IA',
    'contingencia SCAN':
        'contingence SCAN',
    'contingencia EPEC':
        'contingence EPEC',
    'contingencia FS-DA':
        'contingence FS-DA',
    'contingencia SVC-AN':
        'contingence SVC-AN',
    'contingencia SVC-RS':
        'contingence SVC-RS',
    'contingencia offline':
        'contingence hors ligne',
    'CPF emisor':
        "CPF de l'émetteur",
    'CNPJ emisor':
        "CNPJ de l'émetteur",
    'La clave de acceso no supera el dígito verificador: el QR puede estar modificado':
        "La clé d'accès ne passe pas le contrôle du chiffre de vérification : le QR a peut-être été modifié",
    'El {doc} del emisor ({numero}) no es válido: el QR puede estar modificado':
        "Le {doc} de l'émetteur ({numero}) n'est pas valide : le QR a peut-être été modifié",
    'Emitida en ambiente de homologación (pruebas): sin valor fiscal':
        "Émise dans l'environnement d'homologation (test) : sans valeur fiscale",
    'Estado':
        'État',
    'Mes de emisión':
        "Mois d'émission",
    'Nota fiscal (modelo {modelo})':
        'Note fiscale (modèle {modelo})',
    'la {sefaz}':
        '{sefaz}',
    'tipo {tipo}':
        'type {tipo}',
    'Liquidación de compra':
        "Liquidation d'achat",
    'Comprobante de retención':
        'Certificat de retenue',
    'El RUC del emisor ({ruc}) no supera la verificación: comprueba la clave en el SRI':
        "Le RUC de l'émetteur ({ruc}) ne passe pas la vérification : vérifiez la clé auprès du SRI",
    'Comprobante del ambiente de pruebas: sin validez tributaria':
        "Justificatif de l'environnement de test : sans valeur fiscale",
    'Ambiente':
        'Environnement',
    'Pruebas':
        'Test',
    'Producción':
        'Production',
    'Contingencia':
        'Contingence',
    'el SRI':
        'SRI',
    'El NIF del emisor no es válido (letra o dígito de control incorrecto)':
        "Le NIF de l'émetteur n'est pas valide (lettre ou chiffre de contrôle incorrect)",
    'La fecha de la factura es posterior a hoy':
        "La date de la facture est postérieure à aujourd'hui",
    'NIF emisor':
        "NIF de l'émetteur",
    'QR del entorno de pruebas de la AEAT':
        "QR de l'environnement de test de l'AEAT",
    'AEAT (no VERI*FACTU)':
        'AEAT (non VERI*FACTU)',
    'El enlace no es de la AEAT: apunta a {host}':
        "Le lien ne provient pas de l'AEAT : il pointe vers {host}",
    'El enlace no es de la AEAT: apunta a un dominio desconocido':
        "Le lien ne provient pas de l'AEAT : il pointe vers un domaine inconnu",
    'Modalidad':
        'Modalité',
    'VERI*FACTU (verificable en la AEAT)':
        "VERI*FACTU (vérifiable auprès de l'AEAT)",
    'Sistema no VERI*FACTU':
        'Système non VERI*FACTU',
    'Comprobar en la AEAT ↗':
        "Vérifier auprès de l'AEAT ↗",
    'QR de TicketBAI alterado: el código de control no coincide':
        'QR TicketBAI modifié : le code de contrôle ne correspond pas',
    'Identificador TicketBAI':
        'Identifiant TicketBAI',
    'El enlace no es de ninguna Hacienda Foral: apunta a {host}':
        "Le lien ne provient d'aucune Hacienda Foral (fisc basque) : il pointe vers {host}",
    'El enlace no es de ninguna Hacienda Foral: apunta a un dominio desconocido':
        "Le lien ne provient d'aucune Hacienda Foral (fisc basque) : il pointe vers un domaine inconnu",
    'QR del entorno de pruebas de TicketBAI':
        "QR de l'environnement de test de TicketBAI",
    'Hacienda Foral de {territorio}':
        'Hacienda Foral de {territorio}',
    'Hacienda Foral':
        'Hacienda Foral (fisc basque)',
    'Territorio':
        'Territoire',
    'Comprobar en Hacienda Foral ↗':
        'Vérifier auprès de la Hacienda Foral ↗',
    'Factura simplificada':
        'Facture simplifiée',
    'Factura-recibo':
        'Facture-reçu',
    'Guía de transporte':
        'Bon de transport',
    'Guía de movimiento de activos propios':
        "Bon de mouvement d'immobilisations propres",
    'Guía de consignación':
        'Bon de consignation',
    'Guía de devolución':
        'Bon de retour',
    'Consulta de mesa':
        'Addition de table',
    'Crédito de consignación':
        'Crédit de consignation',
    'Factura de consignación':
        'Facture de consignation',
    'Hoja de obra':
        'Feuille de chantier',
    'Nota de encargo':
        'Bon de commande',
    'Otro documento':
        'Autre document',
    'Presupuesto':
        'Devis',
    'Factura proforma':
        'Facture pro forma',
    'Documento de conferencia':
        'Document de conférence',
    'Recibo de prima':
        'Reçu de prime',
    'Recibo de extorno':
        'Reçu de ristourne',
    'Imputación a coaseguradoras':
        'Imputation aux coassureurs',
    'Imputación a coaseguradora líder':
        'Imputation au coassureur principal',
    'Reaseguro aceptado':
        'Réassurance acceptée',
    'Recibo (IVA de caja)':
        'Reçu (TVA sur les encaissements)',
    'Normal':
        'Normal',
    'Autofacturación':
        'Autofacturation',
    'Anulado':
        'Annulé',
    'Documento de resumen':
        'Document récapitulatif',
    'Facturado':
        'Facturé',
    'Por cuenta de terceros':
        'Pour le compte de tiers',
    'El NIF del emisor no es válido (dígito de control incorrecto)':
        "Le NIF de l'émetteur n'est pas valide (chiffre de contrôle incorrect)",
    'El NIF del adquirente no es válido (dígito de control incorrecto)':
        "Le NIF de l'acquéreur n'est pas valide (chiffre de contrôle incorrect)",
    'La fecha del documento es posterior a hoy':
        "La date du document est postérieure à aujourd'hui",
    'Documento anulado':
        'Document annulé',
    'Estado del documento':
        'État du document',
    'Espacio fiscal':
        'Région fiscale',
    'Certificado del programa':
        'Certificat du logiciel',
    'Otras informaciones':
        'Autres informations',
    'NIF adquirente':
        "NIF de l'acquéreur",
    'Total de impuestos':
        'Total des taxes',
    'Documento {tipo}':
        'Document {tipo}',
}
