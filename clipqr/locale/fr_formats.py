"""Catálogo francés (formats): texto en español -> traducción."""
TEXTS = {
    'Código QR':
        'QR code',
    'Nombre':
        'Nom',
    'Teléfono':
        'Téléphone',
    'Empresa':
        'Entreprise',
    'Cargo':
        'Fonction',
    'Dirección':
        'Adresse',
    'Nota':
        'Note',
    'Evento':
        'Événement',
    'Inicio':
        'Début',
    'Fin':
        'Fin',
    'Lugar':
        'Lieu',
    'Descripción':
        'Description',
    'Red (SSID)':
        'Réseau (SSID)',
    'Número':
        'Numéro',
    'Coordenadas':
        'Coordonnées',
    'Código':
        'Code',
    'Emisor':
        'Émetteur',
    'Cuenta':
        'Compte',
    'Dominio':
        'Domaine',
    'Texto':
        'Texte',
    'Guardar contacto':
        'Enregistrer le contact',
    'Contacto':
        'Contact',
    'Ubicación':
        'Localisation',
    'Enlace':
        'Lien',
    'Producto':
        'Produit',
    'Llamar':
        'Appeler',
    'Escribir email':
        'Écrire un e-mail',
    'Abrir web ↗':
        'Ouvrir le site ↗',
    'Buscar en Google ↗':
        'Rechercher sur Google ↗',
    'Añadir al calendario':
        'Ajouter au calendrier',
    'Secreto':
        'Secret',
    'Asunto':
        'Objet',
    'Mensaje':
        'Message',
    'Enviar SMS':
        'Envoyer un SMS',
    'Ver en el mapa ↗':
        'Voir sur la carte ↗',
    'Servidor':
        'Serveur',
    'Abrir enlace ↗':
        'Ouvrir le lien ↗',
    'Buscar producto ↗':
        'Rechercher le produit ↗',
    'Contraseña':
        'Mot de passe',
    'Seguridad':
        'Sécurité',
    'Conectar a la red':
        'Se connecter au réseau',
    'Los pagos con criptomonedas no se pueden revertir: comprueba la dirección completa antes de pagar':
        "Les paiements en cryptomonnaie sont irréversibles : vérifiez l'adresse complète avant de payer",
    '{red} · empresa':
        '{red} · entreprise',
    '{red} · perfil':
        '{red} · profil',
    '{red} · publicación':
        '{red} · publication',
    'Pago QR · UPI':
        'Paiement QR · UPI',
    'Cripto · {moneda}':
        'Crypto · {moneda}',
    'WhatsApp · grupo':
        'WhatsApp · groupe',
    'Abrir chat en WhatsApp ↗':
        'Ouvrir la discussion dans WhatsApp ↗',
    'Abre el chat; el mensaje no se envía hasta que lo mandes tú':
        "Ouvre la discussion ; le message n'est envoyé que lorsque vous l'envoyez",
    'Telegram · grupo':
        'Telegram · groupe',
    'Usuario':
        "Nom d'utilisateur",
    'YouTube · vídeo':
        'YouTube · vidéo',
    'Calendario':
        'Calendrier',
    'La dirección UPI no tiene la forma usuario@banco':
        "L'adresse UPI n'a pas la forme utilisateur@banque",
    'Importe':
        'Montant',
    'Cobra':
        'Bénéficiaire',
    'Para {nombre}':
        'À {nombre}',
    'Red':
        'Réseau',
    'Destinatario':
        'Destinataire',
    'Invitación a un grupo':
        'Invitation à un groupe',
    'Copiar número':
        'Copier le numéro',
    'Abrir en Telegram ↗':
        'Ouvrir dans Telegram ↗',
    'Copiar usuario':
        "Copier le nom d'utilisateur",
    'Vídeo de YouTube':
        'Vidéo YouTube',
    'Abrir en {red} ↗':
        'Ouvrir dans {red} ↗',
    'Tienda':
        'Boutique',
    'Identificador':
        'Identifiant',
    'Copiar dirección UPI':
        "Copier l'adresse UPI",
    'Copiar dirección':
        "Copier l'adresse",
    'Invitación':
        'Invitation',
    'Unirse al grupo en WhatsApp ↗':
        'Rejoindre le groupe dans WhatsApp ↗',
    'Unirse en Telegram ↗':
        'Rejoindre dans Telegram ↗',
    'Vídeo':
        'Vidéo',
    'Ver en YouTube ↗':
        'Regarder sur YouTube ↗',
    'GitHub · repositorio':
        'GitHub · dépôt',
    'Suscribirse al calendario ↗':
        "S'abonner au calendrier ↗",
    'Copiar enlace':
        'Copier le lien',
    'Dirección UPI':
        'Adresse UPI',
    'Concepto':
        'Libellé',
    'Repositorio':
        'Dépôt',
    'Abrir en GitHub ↗':
        'Ouvrir dans GitHub ↗',
    'Copiar «git clone»':
        'Copier « git clone »',
    'Publicación':
        'Publication',
    'QR de pago alterado o dañado (el código de control no coincide)':
        'QR de paiement modifié ou endommagé (la somme de contrôle ne correspond pas)',
    'Brasil':
        'Brésil',
    'México':
        'Mexique',
    'Perú':
        'Pérou',
    'Compra de bienes':
        'Achat de biens',
    'Salario':
        'Salaire',
    'Alquiler':
        'Loyer',
    'Donación':
        'Don',
    'Pago a proveedor':
        'Paiement fournisseur',
    'Impuestos':
        'Impôts',
    'La clave Pix parece un CPF pero no es válido':
        "La clé Pix ressemble à un CPF mais n'est pas valide",
    'La clave Pix parece un CNPJ pero no es válido':
        "La clé Pix ressemble à un CNPJ mais n'est pas valide",
    'Pago QR · {red}':
        'Paiement QR · {red}',
    'Pago QR':
        'Paiement QR',
    'Sin importe: lo eliges en la app al pagar':
        "Sans montant : vous le choisissez dans l'application au moment de payer",
    'Transferencia SEPA inmediata':
        'Virement SEPA instantané',
    'Transferencia SEPA':
        'Virement SEPA',
    'QR-factura suiza':
        'QR-facture suisse',
    'Factura':
        'Facture',
    'Referencia':
        'Référence',
    'Terminal':
        'Terminal',
    'Copiar código de pago':
        'Copier le code de paiement',
    'El IBAN no es válido (dígitos de control)':
        "L'IBAN n'est pas valide (chiffres de contrôle)",
    'Copiar IBAN':
        "Copier l'IBAN",
    'Beneficiario':
        'Bénéficiaire',
    'QR de transferencia incompleto o con un formato que no se reconoce':
        'QR de virement incomplet ou dans un format non reconnu',
    'Motivo':
        'Motif',
    'QR-factura suiza incompleta o con un formato que no se reconoce':
        'QR-facture suisse incomplète ou dans un format non reconnu',
    'Clave Pix':
        'Clé Pix',
    'Cobro Pix':
        'Encaissement Pix',
    'El {cuenta} no es válido (dígito verificador)':
        "Le {cuenta} n'est pas valide (chiffre de contrôle)",
    'Ciudad':
        'Ville',
    'País':
        'Pays',
    'Tipo':
        'Type',
    'QR de un solo cobro':
        'QR à usage unique',
    'Comercio':
        'Commerçant',
    'Copiar clave Pix':
        'Copier la clé Pix',
    'Copiar {cuenta}':
        'Copier le {cuenta}',
    'Copiar referencia':
        'Copier la référence',
    'El importe no tiene el formato «EUR123.45»':
        "Le montant n'a pas le format « EUR123.45 »",
    'Referencia QR':
        'Référence QR',
    'Referencia ISO 11649':
        'Référence ISO 11649',
    'Localidad':
        'Localité',
    'Tipo de referencia':
        'Type de référence',
    'SSCC (envío)':
        'SSCC (expédition)',
    'GTIN contenido':
        'GTIN contenu',
    'Lote':
        'Lot',
    'Fabricado':
        'Date de fabrication',
    'Vence el pago':
        'Échéance du paiement',
    'Envasado':
        "Date d'emballage",
    'Consumir preferentemente antes de':
        'À consommer de préférence avant',
    'Vender antes de':
        'À vendre avant',
    'Vencimiento':
        "Date d'expiration",
    'Variante':
        'Variante',
    'Número de serie':
        'Numéro de série',
    'Variante de consumo':
        'Variante de produit',
    'Cantidad':
        'Quantité',
    'Unidades':
        'Unités',
    'Pieza del cliente':
        'Référence client',
    'Serie secundaria':
        'Numéro de série secondaire',
    'Pedido':
        'Commande',
    'Enviar a (GLN)':
        'Livrer à (GLN)',
    'Ubicación (GLN)':
        'Emplacement (GLN)',
    'País de origen':
        "Pays d'origine",
    'Vence (fecha y hora)':
        'Expire (date et heure)',
    'Peso neto':
        'Poids net',
    'Largo':
        'Longueur',
    'Peso bruto':
        'Poids brut',
    'Precio':
        'Prix',
    'EE. UU. y Canadá':
        'États-Unis et Canada',
    'EE. UU.':
        'États-Unis',
    'Francia':
        'France',
    'Alemania':
        'Allemagne',
    'Japón':
        'Japon',
    'Rusia':
        'Russie',
    'Taiwán':
        'Taïwan',
    'Filipinas':
        'Philippines',
    'Reino Unido':
        'Royaume-Uni',
    'Grecia':
        'Grèce',
    'Irlanda':
        'Irlande',
    'Bélgica y Luxemburgo':
        'Belgique et Luxembourg',
    'Dinamarca':
        'Danemark',
    'Polonia':
        'Pologne',
    'Sudáfrica':
        'Afrique du Sud',
    'Noruega':
        'Norvège',
    'Suecia':
        'Suède',
    'Panamá':
        'Panama',
    'República Dominicana':
        'République dominicaine',
    'Canadá':
        'Canada',
    'Suiza':
        'Suisse',
    'Italia':
        'Italie',
    'España':
        'Espagne',
    'Eslovaquia':
        'Slovaquie',
    'República Checa':
        'République tchèque',
    'Turquía':
        'Turquie',
    'Países Bajos':
        'Pays-Bas',
    'Corea del Sur':
        'Corée du Sud',
    'Tailandia':
        'Thaïlande',
    'Singapur':
        'Singapour',
    'Nueva Zelanda':
        'Nouvelle-Zélande',
    'Malasia':
        'Malaisie',
    'Revista (ISSN)':
        'Revue (ISSN)',
    'Libro (ISBN)':
        'Livre (ISBN)',
    'Uso interno de la tienda':
        'Usage interne du magasin',
    'Producto · GS1':
        'Produit · GS1',
    'El dígito verificador del GTIN no cuadra: el código puede estar mal leído':
        'Le chiffre de contrôle du GTIN ne correspond pas : le code a peut-être été mal lu',
    'Ver en GS1 ↗':
        'Voir sur GS1 ↗',
    'Abrir enlace del fabricante ↗':
        'Ouvrir le lien du fabricant ↗',
    'Código GS1':
        'Code GS1',
    'Registrado en':
        'Enregistré en',
    'Producto vencido el {fecha}':
        'Produit périmé depuis le {fecha}',
    'Pasó la fecha de consumo preferente ({fecha})':
        'Date de consommation recommandée dépassée ({fecha})',
    'Vence hoy':
        "Expire aujourd'hui",
    'Vence en {dias} día':
        'Expire dans {dias} jour',
    'Vence en {dias} días':
        'Expire dans {dias} jours',
    'Lote {lote}':
        'Lot {lote}',
    'Vence {fecha}':
        'Expire le {fecha}',
    'Datos personales: no se guardan en el historial':
        "Données personnelles : non enregistrées dans l'historique",
    'Masculino':
        'Masculin',
    'Femenino':
        'Féminin',
    'No binario':
        'Non binaire',
    'Primera':
        'Première',
    'Turista premium':
        'Premium économique',
    'Turista':
        'Économique',
    'no va al historial':
        "non enregistré dans l'historique",
    'Tarjeta de embarque':
        "Carte d'embarquement",
    'Apellido':
        'Nom de famille',
    'Sexo':
        'Sexe',
    'Nacimiento':
        'Date de naissance',
    'Emisión':
        "Date d'émission",
    'Ejemplar':
        'Exemplaire',
    'Número de trámite':
        'Numéro de démarche',
    'Copiar DNI':
        'Copier le DNI',
    'Copiar nombre completo':
        'Copier le nom complet',
    'Titular':
        'Titulaire',
    'Pasajero':
        'Passager',
    'Vuelo':
        'Vol',
    'Origen':
        'Départ',
    'Destino':
        'Arrivée',
    'Reserva':
        'Réservation',
    'Copiar reserva':
        'Copier la réservation',
    'Estado del vuelo ↗':
        'État du vol ↗',
    'Fecha':
        'Date',
    'Asiento':
        'Siège',
    'Clase':
        'Classe',
    'Secuencia':
        'Séquence',
    'Tramos':
        'Segments',
    'Comprobante':
        'Justificatif fiscal',
    'Copiar resumen':
        'Copier le résumé',
    'Verificar en {organismo} ↗':
        'Vérifier auprès de {organismo} ↗',
    'Cotización':
        'Taux de change',
    'Receptor':
        'Destinataire',
    'Autorización':
        'Autorisation',
    'Verificación':
        'Vérification',
}
