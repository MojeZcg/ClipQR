"""Enlaces conocidos con una tarjeta propia: WhatsApp, Telegram, redes sociales, tiendas de apps,
calendarios .ics, pagos UPI y direcciones de criptomonedas (estas dos, solo para copiar)."""
import re
from urllib.parse import parse_qs, unquote, urlsplit

from clipqr.linksafety import link_warnings
from clipqr.structured import Result, format_money, register, to_decimal

SOCIAL = {
    "instagram.com": "Instagram", "x.com": "X (Twitter)", "twitter.com": "X (Twitter)",
    "tiktok.com": "TikTok", "facebook.com": "Facebook", "fb.com": "Facebook", "linkedin.com": "LinkedIn",
    "github.com": "GitHub", "threads.net": "Threads", "threads.com": "Threads", "youtube.com": "YouTube",
    "youtu.be": "YouTube", "bsky.app": "Bluesky", "twitch.tv": "Twitch", "pinterest.com": "Pinterest",
}
# rutas que no son un perfil
NOT_PROFILE = {"p", "reel", "reels", "explore", "share", "sharer", "watch", "status", "home", "login", "intent",
               "search", "hashtag", "stories", "groups", "events", "pages", "settings", "tv", "shorts", "embed"}
CRYPTO = {"bitcoin": "Bitcoin", "ethereum": "Ethereum", "litecoin": "Litecoin", "bitcoincash": "Bitcoin Cash",
          "dogecoin": "Dogecoin", "monero": "Monero", "solana": "Solana", "tron": "Tron", "lightning": "Lightning"}
CRYPTO_WARNING = ("Los pagos con criptomonedas no se pueden revertir: comprueba la dirección completa "
                  "antes de pagar")


def _host(url):
    host = (url.hostname or "").lower()
    return host[4:] if host.startswith("www.") else host[2:] if host.startswith("m.") else host


def _link(title, url, items, actions, headline, subtitle=None):
    return Result("link", title, items, actions, link_warnings(url), headline, subtitle)


def _phone(digits):
    return "+" + digits if digits else ""


def whatsapp(url, text):
    host, path, q = _host(url), url.path.strip("/"), parse_qs(url.query)
    if host == "chat.whatsapp.com" and path:
        return _link("WhatsApp · grupo", text, [("Invitación", path)],
                     [("Unirse al grupo en WhatsApp ↗", "open", text)], ("Invitación a un grupo", "WhatsApp"))
    if host == "wa.me" and re.fullmatch(r"\d{6,15}", path):
        number = path
    elif host == "api.whatsapp.com" and path == "send":
        number = re.sub(r"\D", "", (q.get("phone") or [""])[0])
    else:
        return None
    message = (q.get("text") or [""])[0]
    items = [("Teléfono", _phone(number))] if number else []
    if message:
        items.append(("Mensaje", message))
    actions = [("Abrir chat en WhatsApp ↗", "open", text)]
    if number:
        actions.append(("Copiar número", "copy", _phone(number)))
    return _link("WhatsApp", text, items, actions, ("Chat", _phone(number) or "WhatsApp"),
                 "Abre el chat; el mensaje no se envía hasta que lo mandes tú" if message else None)


def telegram(url, text):
    path = url.path.strip("/")
    if not path:
        return None
    first = path.split("/")[0]
    if first.startswith("+") or first == "joinchat":
        return _link("Telegram · grupo", text, [("Invitación", path)],
                     [("Unirse en Telegram ↗", "open", text)], ("Invitación a un grupo", "Telegram"))
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{3,31}", first):
        return None
    return _link("Telegram", text, [("Usuario", "@" + first)],
                 [("Abrir en Telegram ↗", "open", text), ("Copiar usuario", "copy", "@" + first)],
                 ("Usuario", "@" + first))


def social(url, text, network):
    host, parts = _host(url), [unquote(p) for p in url.path.split("/") if p]
    if host == "youtu.be" and parts:
        return _link("YouTube · vídeo", text, [("Vídeo", parts[0])], [("Ver en YouTube ↗", "open", text)],
                     ("Vídeo de YouTube", parts[0]))
    if network == "YouTube" and parts[:1] == ["watch"]:
        video = (parse_qs(url.query).get("v") or [""])[0]
        return _link("YouTube · vídeo", text, [("Vídeo", video)], [("Ver en YouTube ↗", "open", text)],
                     ("Vídeo de YouTube", video))
    if not parts:
        return None
    if network == "LinkedIn":
        if len(parts) < 2 or parts[0] not in ("in", "company"):
            return None
        user, label = parts[1], "Empresa" if parts[0] == "company" else "Perfil"
    elif network == "Facebook" and parts[0] == "profile.php":
        user, label = (parse_qs(url.query).get("id") or [""])[0], "Perfil"
    elif network == "GitHub" and len(parts) >= 2:
        repo = f"{parts[0]}/{parts[1]}"
        return _link("GitHub · repositorio", text, [("Repositorio", repo)],
                     [("Abrir en GitHub ↗", "open", text), ("Copiar «git clone»", "copy",
                                                            f"git clone https://github.com/{repo}.git")],
                     ("Repositorio", repo))
    else:
        if parts[0].lower() in NOT_PROFILE or len(parts) > 1 and network not in ("YouTube", "TikTok"):
            return _link(f"{network} · publicación", text, [("Red", network)],
                         [(f"Abrir en {network} ↗", "open", text)], ("Publicación", network))
        user, label = parts[0], "Perfil"
    if not user:
        return None
    shown = user if user.startswith("@") or network in ("LinkedIn", "Facebook") else "@" + user
    return _link(f"{network} · {label.lower()}", text, [("Usuario", shown), ("Red", network)],
                 [(f"Abrir en {network} ↗", "open", text), ("Copiar usuario", "copy", shown)],
                 ("Usuario", shown))


def app_store(url, text):
    host, parts = _host(url), [p for p in url.path.split("/") if p]
    if host == "apps.apple.com":
        app_id = next((p for p in parts if re.fullmatch(r"id\d+", p)), None)
        if not app_id:
            return None
        name = parts[parts.index(app_id) - 1].replace("-", " ").title() if parts.index(app_id) > 0 else ""
        store = "App Store"
    elif host == "play.google.com" and parts[:3] == ["store", "apps", "details"]:
        app_id = (parse_qs(url.query).get("id") or [""])[0]
        if not app_id:
            return None
        name, store = "", "Google Play"
    elif host == "apps.microsoft.com" and len(parts) >= 2 and parts[0] == "detail":
        app_id, name, store = parts[1], "", "Microsoft Store"
    else:
        return None
    items = ([("App", name)] if name and name != "App" else []) + [("Tienda", store), ("Identificador", app_id)]
    return _link(f"App · {store}", text, items, [(f"Abrir en {store} ↗", "open", text)],
                 ("App", name or app_id))


@register
def parse_known_link(text):
    t = text.strip()
    low = t.lower()
    if low.startswith("webcal://") or re.match(r"^https?://\S+\.ics(\?\S*)?$", low):
        url = "https://" + t[9:] if low.startswith("webcal://") else t
        return Result("event", "Calendario", [("Calendario", _host(urlsplit(url)) or url)],
                      [("Suscribirse al calendario ↗", "open", t), ("Copiar enlace", "copy", url)],
                      link_warnings(url), ("Calendario", _host(urlsplit(url))))
    if low.startswith("upi://pay"):
        return upi(t)
    scheme = low.split(":", 1)[0]
    if scheme in CRYPTO and ":" in t:
        return crypto(t, scheme)
    if not re.match(r"^https?://", t, re.I):
        return None
    url = urlsplit(t)
    host = _host(url)
    if host in ("wa.me", "api.whatsapp.com", "chat.whatsapp.com"):
        return whatsapp(url, t)
    if host in ("t.me", "telegram.me"):
        return telegram(url, t)
    if host in ("apps.apple.com", "play.google.com", "apps.microsoft.com"):
        return app_store(url, t)
    if host in SOCIAL:
        return social(url, t, SOCIAL[host])
    return None


def upi(text):
    """Pago UPI de la India: upi://pay?pa=<VPA>&pn=<nombre>&am=<importe>&cu=INR&tn=<nota>."""
    q = {k: v[0] for k, v in parse_qs(urlsplit(text).query).items()}
    vpa, name = q.get("pa", ""), q.get("pn", "")
    amount = to_decimal(q.get("am")) if q.get("am") else None
    items = [i for i in (("Cobra", name), ("Dirección UPI", vpa), ("Concepto", q.get("tn", ""))) if i[1]]
    warnings = [] if re.fullmatch(r"[\w.\-]+@[\w.\-]+", vpa) else ["La dirección UPI no tiene la forma usuario@banco"]
    headline = ("Importe", format_money(amount, q.get("cu", "INR"), "US")) if amount is not None \
        else ("Cobra", name or vpa)
    return Result("payment", "Pago QR · UPI", items, [("Copiar dirección UPI", "copy", vpa)], warnings, headline,
                  f"Para {name}" if name and amount is not None else None)


def crypto(text, scheme):
    """bitcoin:<dirección>?amount=0.01&label=… (BIP 21) y equivalentes: solo se muestra y se copia."""
    rest = text.split(":", 1)[1].lstrip("/")
    address, _, query = rest.partition("?")
    q = {k: v[0] for k, v in parse_qs(query).items()}
    coin = CRYPTO[scheme]
    if not address:
        return None
    items = [("Dirección", address), ("Red", coin)]
    for key, label in (("label", "Destinatario"), ("message", "Mensaje"), ("amount", "Importe")):
        if q.get(key):
            items.append((label, f"{q[key]} {coin}" if key == "amount" else q[key]))
    headline = ("Importe", f"{q['amount']} {coin}") if q.get("amount") else ("Dirección", address)
    return Result("payment", f"Cripto · {coin}", items, [("Copiar dirección", "copy", address)],
                  [CRYPTO_WARNING], headline, q.get("label"))
