"""Interpretación del texto de un código: tipo, datos y acciones (botones)."""
import re
import urllib.parse

from clipqr.linksafety import registrable_domain

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

FORMAT_NAMES = {"QRCode": "Código QR", "MicroQRCode": "Micro QR", "RMQRCode": "rMQR", "DataMatrix": "DataMatrix",
                "Aztec": "Aztec", "PDF417": "PDF417", "EAN13": "EAN-13", "EAN8": "EAN-8", "UPCA": "UPC-A",
                "UPCE": "UPC-E", "Code128": "Code 128", "Code39": "Code 39", "Code93": "Code 93",
                "ITF": "ITF", "Codabar": "Codabar"}

def headline(kind, items, text):
    """(etiqueta, valor) del dato que se muestra en grande en el aviso."""
    want = {"wifi": ("Red (SSID)",), "contact": ("Nombre", "Empresa", "Teléfono", "Email"),
            "email": ("Email",), "phone": ("Número",), "sms": ("Número",), "geo": ("Coordenadas",),
            "event": ("Evento",), "product": ("Código",), "otp": ("Emisor", "Cuenta"), "link": ("Dominio",)}
    for label in want.get(kind, ()):
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
    return FORMAT_NAMES.get(fmt, fmt)

def _vcard_from(items):
    """vCard mínima a partir de [(etiqueta, valor)] (para MeCard)."""
    keys = {"Nombre": "FN", "Teléfono": "TEL", "Email": "EMAIL", "Web": "URL",
            "Dirección": "ADR", "Nota": "NOTE", "Empresa": "ORG"}
    lines = ["BEGIN:VCARD", "VERSION:3.0"] + [f"{keys[l]}:{v}" for l, v in items if l in keys]
    return "\r\n".join(lines + ["END:VCARD"]) + "\r\n"

def _contact_actions(items, card_text):
    actions = [("Guardar contacto", "file", (card_text, ".vcf"))]
    first = lambda label: next((v for l, v in items if l == label), None)
    if first("Teléfono"):
        actions.append(("Llamar", "open", "tel:" + re.sub(r"[^\d+]", "", first("Teléfono"))))
    if first("Email"):
        actions.append(("Escribir email", "open", "mailto:" + first("Email")))
    if first("Web"):
        web = first("Web")
        actions.append(("Abrir web ↗", "open", web if "://" in web else "https://" + web))
    return actions

def parse_payload(text):
    """Devuelve (tipo, titulo, [(etiqueta, valor)], [(texto_boton, accion, arg)]).

    Las acciones son siempre botones: nada se ejecuta sin que el usuario lo pulse.
    accion: "open" (abrir URI), "wifi" (conectar), "file" (guardar y abrir (contenido, extensión)).
    """
    t = text.strip()
    low = t.lower()

    if low.startswith("wifi:"):
        f = dict(_split_fields(t[5:]))
        items = [(l, f[k]) for k, l in (("S", "Red (SSID)"), ("P", "Contraseña"), ("T", "Seguridad")) if f.get(k)]
        wifi = {"ssid": f.get("S", ""), "password": f.get("P", ""), "auth": f.get("T", ""),
                "hidden": f.get("H", "").lower() == "true"}
        return "wifi", "Wi-Fi", items, [("Conectar a la red", "wifi", wifi)] if wifi["ssid"] else []

    if low.startswith("begin:vcard"):
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.split(";")[0].upper()
            val = val.replace("\\,", ",").replace("\\;", ";").strip()
            label = {"FN": "Nombre", "TEL": "Teléfono", "EMAIL": "Email", "ORG": "Empresa",
                     "TITLE": "Cargo", "URL": "Web", "ADR": "Dirección", "NOTE": "Nota"}.get(key)
            if label and val:
                if key == "ADR":
                    val = ", ".join(p for p in val.split(";") if p)
                items.append((label, val))
        return "contact", "Contacto", items, _contact_actions(items, t)

    if low.startswith("mecard:"):
        labels = {"N": "Nombre", "TEL": "Teléfono", "EMAIL": "Email", "URL": "Web",
                  "ADR": "Dirección", "NOTE": "Nota", "ORG": "Empresa"}
        items = [(labels[k], " ".join(reversed(v.split(","))) if k == "N" else v)
                 for k, v in _split_fields(t[7:]) if k in labels and v]
        return "contact", "Contacto", items, _contact_actions(items, _vcard_from(items))

    if "begin:vevent" in low:
        labels = {"SUMMARY": "Evento", "DTSTART": "Inicio", "DTEND": "Fin",
                  "LOCATION": "Lugar", "DESCRIPTION": "Descripción"}
        items = []
        for line in re.split(r"\r?\n", t):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.split(";")[0].upper()
                if key in labels and val.strip():
                    items.append((labels[key], val.strip()))
        ics = t if low.startswith("begin:vcalendar") else f"BEGIN:VCALENDAR\r\nVERSION:2.0\r\n{t}\r\nEND:VCALENDAR\r\n"
        return "event", "Evento", items, [("Añadir al calendario", "file", (ics, ".ics"))]

    if low.startswith("otpauth://"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [("Cuenta", urllib.parse.unquote(u.path.lstrip("/")))]
        if q.get("secret"):
            items.append(("Secreto", q["secret"]))
        if q.get("issuer"):
            items.append(("Emisor", q["issuer"]))
        return "otp", "2FA (OTP)", items, []

    if low.startswith("mailto:"):
        u = urllib.parse.urlparse(t)
        q = dict(urllib.parse.parse_qsl(u.query))
        items = [("Email", urllib.parse.unquote(u.path))]
        if q.get("subject"):
            items.append(("Asunto", q["subject"]))
        if q.get("body"):
            items.append(("Mensaje", q["body"]))
        return "email", "Email", items, [("Escribir email", "open", t)]

    if low.startswith("matmsg:"):
        f = dict(_split_fields(t[7:]))
        items = [(l, f[k]) for k, l in (("TO", "Email"), ("SUB", "Asunto"), ("BODY", "Mensaje")) if f.get(k)]
        q = urllib.parse.urlencode({k: v for k, v in (("subject", f.get("SUB")), ("body", f.get("BODY"))) if v},
                                   quote_via=urllib.parse.quote)
        mailto = f"mailto:{f.get('TO', '')}" + (f"?{q}" if q else "")
        return "email", "Email", items, [("Escribir email", "open", mailto)]

    if low.startswith("tel:"):
        return "phone", "Teléfono", [("Número", t[4:])], [("Llamar", "open", t)]

    if low.startswith(("smsto:", "sms:")):
        parts = t.split(":", 2)
        items = [("Número", parts[1])] if len(parts) > 1 else []
        if len(parts) > 2 and parts[2]:
            items.append(("Mensaje", parts[2]))
        actions = []
        if len(parts) > 1 and parts[1]:
            body = f"?body={urllib.parse.quote(parts[2])}" if len(parts) > 2 and parts[2] else ""
            actions.append(("Enviar SMS", "open", f"sms:{parts[1]}{body}"))
        return "sms", "SMS", items, actions

    if low.startswith("geo:"):
        lat_lon = t[4:].split("?")[0].split(",")[:2]
        actions = []
        if len(lat_lon) == 2:
            actions.append(("Ver en el mapa ↗", "open", f"https://www.google.com/maps?q={','.join(lat_lon)}"))
        return "geo", "Ubicación", [("Coordenadas", ",".join(lat_lon))], actions

    if re.match(r"^https?://", t, re.I):
        u = urllib.parse.urlparse(t)
        host = (u.hostname or u.netloc).lower()
        items = [("Dominio", registrable_domain(host))]  # el dominio real, no los subdominios de delante
        if host not in (items[0][1], "www." + items[0][1]):
            items.append(("Servidor", host))
        return "link", "Enlace", items, [("Abrir enlace ↗", "open", t)]

    if re.match(r"^(\d{8}|\d{12,14})$", t):  # EAN / UPC / GTIN de un producto
        return "product", "Producto", [("Código", t)], [
            ("Buscar producto ↗", "open", "https://www.google.com/search?q=" + t)]

    if re.match(r"^www\.\S+$", t, re.I):
        return "link", "Enlace", [], [("Abrir enlace ↗", "open", "https://" + t)]

    # texto libre: extraer emails / urls sueltos
    items, actions = [], []
    for m in re.findall(r"https?://\S+", t):
        items.append(("URL", m))
        if not actions:
            actions.append(("Abrir enlace ↗", "open", m))
    for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", t):
        items.append(("Email", m))
    if not actions and len(t) <= 200:
        actions.append(("Buscar en Google ↗", "open", "https://www.google.com/search?q=" + urllib.parse.quote(t)))
    return "text", "Texto", items, actions
