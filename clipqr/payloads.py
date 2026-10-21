"""Interpretación del texto de un código: tipo, datos y acciones (botones)."""
import importlib
import re
import urllib.parse

from clipqr.i18n import N_, _
from clipqr.linksafety import link_warnings, registrable_domain
from clipqr.structured import Result, detect

def _unescape(s):
    return re.sub(r"\\([\\;,:\"])", r"\1", s)

def _split_fields(body):
    """Separa 'K:V;K:V;' respetando escapes con backslash."""
    parts = re.split(r"(?<!\\);", body)
    fields = []
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            fields.append((k.upper(), _unescape(v)))
    return fields

FORMAT_NAMES = {"QRCode": N_("Código QR"), "MicroQRCode": "Micro QR", "RMQRCode": "rMQR", "DataMatrix": "DataMatrix",
                "Aztec": "Aztec", "PDF417": "PDF417", "EAN13": "EAN-13", "EAN8": "EAN-8", "UPCA": "UPC-A",
                "UPCE": "UPC-E", "Code128": "Code 128", "Code39": "Code 39", "Code93": "Code 93",
                "ITF": "ITF", "Codabar": "Codabar"}

# tipo -> etiquetas preferidas para el dato principal, por orden
HEADLINE_LABELS = {"wifi": (N_("Red (SSID)"),), "contact": (N_("Nombre"), N_("Empresa"), N_("Teléfono"), "Email"),
                   "email": ("Email",), "phone": (N_("Número"),), "sms": (N_("Número"),),
                   "geo": (N_("Coordenadas"),), "event": (N_("Evento"),), "product": (N_("Código"),),
                   "otp": (N_("Emisor"), N_("Cuenta")), "link": (N_("Dominio"),)}

def headline(kind, items, text):
    """(etiqueta, valor) del dato que se muestra en grande en el aviso."""
    for label in HEADLINE_LABELS.get(kind, ()):
        label = _(label)  # las etiquetas de items ya están traducidas
        for l, v in items:
            if l == label and v:
                return l, v
    first = text.strip().splitlines()[0] if text.strip() else text
    return None, first

def shorten(s, n, middle=False):
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    if middle:
        k = (n - 1) // 2
        return s[:k] + "…" + s[-k:]
    return s[:n - 1] + "…"

def format_name(fmt):
    return _(FORMAT_NAMES[fmt]) if fmt in FORMAT_NAMES else fmt

def _vcard_from(items):
    """vCard mínima a partir de [(etiqueta, valor)] (para MeCard)."""
    keys = {_(label): key for label, key in ((N_("Nombre"), "FN"), (N_("Teléfono"), "TEL"), ("Email", "EMAIL"),
                                              (N_("Web"), "URL"), (N_("Dirección"), "ADR"), (N_("Nota"), "NOTE"),
                                              (N_("Empresa"), "ORG"))}
    lines = ["BEGIN:VCARD", "VERSION:3.0"] + [f"{keys[l]}:{v}" for l, v in items if l in keys]
    return "\r\n".join(lines + ["END:VCARD"]) + "\r\n"

def _contact_actions(items, card_text):
    actions = [(_("Guardar contacto"), "file", (card_text, ".vcf"))]
    first = lambda label: next((v for l, v in items if l == label), None)
    phone, email, web = first(_("Teléfono")), first("Email"), first(_("Web"))
    if phone:
        actions.append((_("Llamar"), "open", "tel:" + re.sub(r"[^\d+]", "", phone)))
    if email:
        actions.append((_("Escribir email"), "open", "mailto:" + email))
    if web:
        actions.append((_("Abrir web ↗"), "open", web if "://" in web else "https://" + web))
    return actions

def analyze(text):
    """Interpretación completa de un código: formatos estructurados (facturas, pagos…) y, si no, los tipos
    básicos. Devuelve un Result (tipo, título, datos, acciones, avisos, dato principal, subtítulo)."""
    importlib.import_module("clipqr.formats")  # registra los formatos estructurados (una sola vez)
    r = detect(text.strip())
    if r is not None:
        return r
    kind, title, items, actions = _basic_payload(text)
    warnings = link_warnings(actions[0][2]) if kind == "link" and actions else []
    return Result(kind, title, items, actions, warnings)


def parse_payload(text):
    """(tipo, titulo, [(etiqueta, valor)], [(texto_boton, accion, arg)]) — forma corta de analyze()."""
    r = analyze(text)
    return r.kind, r.title, r.items, r.actions


VCARD_LABELS = {"FN": N_("Nombre"), "TEL": N_("Teléfono"), "EMAIL": "Email", "ORG": N_("Empresa"),
                "TITLE": N_("Cargo"), "URL": N_("Web"), "ADR": N_("Dirección"), "NOTE": N_("Nota")}
MECARD_LABELS = {"N": N_("Nombre"), "TEL": N_("Teléfono"), "EMAIL": "Email", "URL": N_("Web"),
                 "ADR": N_("Dirección"), "NOTE": N_("Nota"), "ORG": N_("Empresa")}
EVENT_LABELS = {"SUMMARY": N_("Evento"), "DTSTART": N_("Inicio"), "DTEND": N_("Fin"),
                "LOCATION": N_("Lugar"), "DESCRIPTION": N_("Descripción")}


def _basic_payload(text):
    """Tipos básicos: (tipo, titulo, [(etiqueta, valor)], [(texto_boton, accion, arg)]).

    Las acciones son siempre botones: nada se ejecuta sin que el usuario lo pulse.
    accion: "open" (abrir URI), "wifi" (conectar), "file" (guardar y abrir (contenido, extensión)).
    """
    t = text.strip()
    low = t.lower()

    if low.startswith("wifi:"):
        f = dict(_split_fields(t[5:]))
        items = [(_(l), f[k]) for k, l in (("S", N_("Red (SSID)")), ("P", N_("Contraseña")), ("T", N_("Seguridad")))
                 if f.get(k)]
        wifi = {"ssid": f.get("S", ""), "password": f.get("P", ""), "auth": f.get("T", ""),
                "hidden": f.get("H", "").lower() == "true"}
        return "wifi", "Wi-Fi", items, [(_("Conectar a la red"), "wifi", wifi)] if wifi["ssid"] else []

    if low.startswith("begin:vcard"):
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.split(";")[0].upper()
            val = val.replace("\\,", ",").replace("\\;", ";").strip()
            label = VCARD_LABELS.get(key)
            if label and val:
                if key == "ADR":
                    val = ", ".join(p for p in val.split(";") if p)
                items.append((_(label), val))
        return "contact", _("Contacto"), items, _contact_actions(items, t)

    if low.startswith("mecard:"):
        items = [(_(MECARD_LABELS[k]), " ".join(reversed(v.split(","))) if k == "N" else v)
                 for k, v in _split_fields(t[7:]) if k in MECARD_LABELS and v]
        return "contact", _("Contacto"), items, _contact_actions(items, _vcard_from(items))

    if "begin:vevent" in low:
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.split(";")[0].upper()
                if key in EVENT_LABELS and val.strip():
                    items.append((_(EVENT_LABELS[key]), val.strip()))
        ics = t if low.startswith("begin:vcalendar") else f"BEGIN:VCALENDAR\r\nVERSION:2.0\r\n{t}\r\nEND:VCALENDAR\r\n"
        return "event", _("Evento"), items, [(_("Añadir al calendario"), "file", (ics, ".ics"))]

    if low.startswith("otpauth://"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [(_("Cuenta"), urllib.parse.unquote(u.path.lstrip("/")))]
        if q.get("secret"):
            items.append((_("Secreto"), q["secret"]))
        if q.get("issuer"):
            items.append((_("Emisor"), q["issuer"]))
        return "otp", "2FA (OTP)", items, []

    if low.startswith("mailto:"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [("Email", urllib.parse.unquote(u.path))]
        if q.get("subject"):
            items.append((_("Asunto"), q["subject"]))
        if q.get("body"):
            items.append((_("Mensaje"), q["body"]))
        return "email", "Email", items, [(_("Escribir email"), "open", t)]

    if low.startswith("matmsg:"):
        f = dict(_split_fields(t[7:]))
        items = [(_(l), f[k]) for k, l in (("TO", "Email"), ("SUB", N_("Asunto")), ("BODY", N_("Mensaje")))
                 if f.get(k)]
        q = urllib.parse.urlencode({k: v for k, v in (("subject", f.get("SUB")), ("body", f.get("BODY"))) if v},
                                   quote_via=urllib.parse.quote)
        mailto = f"mailto:{f.get('TO', '')}" + (f"?{q}" if q else "")
        return "email", "Email", items, [(_("Escribir email"), "open", mailto)]

    if low.startswith("tel:"):
        return "phone", _("Teléfono"), [(_("Número"), t[4:])], [(_("Llamar"), "open", t)]

    if low.startswith(("smsto:", "sms:")):
        parts = t.split(":", 2)
        items = [(_("Número"), parts[1])] if len(parts) > 1 else []
        if len(parts) > 2 and parts[2]:
            items.append((_("Mensaje"), parts[2]))
        actions = []
        if len(parts) > 1 and parts[1]:
            body = f"?body={urllib.parse.quote(parts[2])}" if len(parts) > 2 and parts[2] else ""
            actions.append((_("Enviar SMS"), "open", f"sms:{parts[1]}{body}"))
        return "sms", "SMS", items, actions

    if low.startswith("geo:"):
        lat_lon = t[4:].split("?")[0].split(",")[:2]
        actions = []
        if len(lat_lon) == 2:
            actions.append((_("Ver en el mapa ↗"), "open", f"https://www.google.com/maps?q={','.join(lat_lon)}"))
        return "geo", _("Ubicación"), [(_("Coordenadas"), ",".join(lat_lon))], actions

    if re.match(r"^https?://", t, re.I):
        u = urllib.parse.urlparse(t)
        host = (u.hostname or u.netloc).lower()
        items = [(_("Dominio"), registrable_domain(host))]  # el dominio real, no los subdominios de delante
        if host not in (items[0][1], "www." + items[0][1]):
            items.append((_("Servidor"), host))
        return "link", _("Enlace"), items, [(_("Abrir enlace ↗"), "open", t)]

    if re.match(r"^(\d{8}|\d{12,14})$", t):  # EAN / UPC / GTIN de un producto
        return "product", _("Producto"), [(_("Código"), t)], [
            (_("Buscar producto ↗"), "open", "https://www.google.com/search?q=" + t)]

    if re.match(r"^www\.\S+$", t, re.I):
        return "link", _("Enlace"), [], [(_("Abrir enlace ↗"), "open", "https://" + t)]

    # texto libre: extraer emails / urls sueltos
    items, actions = [], []
    for m in re.findall(r"https?://\S+", t):
        items.append(("URL", m))
        if not actions:
            actions.append((_("Abrir enlace ↗"), "open", m))
    for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", t):
        items.append(("Email", m))
    if not actions and len(t) <= 200:
        actions.append((_("Buscar en Google ↗"), "open", "https://www.google.com/search?q=" + urllib.parse.quote(t)))
    return "text", _("Texto"), items, actions
