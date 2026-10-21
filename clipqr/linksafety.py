"""Avisos de seguridad para enlaces de QR (contra el «quishing»). Todo es local: no se consulta ningún
servicio ni se abre el enlace. Los avisos informan; nunca bloquean."""
import ipaddress
import re
import urllib.parse

SHORTENERS = {
    "bit.ly", "bitly.com", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "v.gd", "buff.ly", "cutt.ly",
    "rebrand.ly", "shorturl.at", "s.id", "rb.gy", "tiny.cc", "lnkd.in", "t.ly", "bit.do", "short.io",
    "qrco.de", "qr.codes", "me-qr.com", "qrfy.io", "l.ead.me", "linktr.ee", "acortar.link", "shorturl.gg",
}
# sufijos de dos niveles habituales: el dominio real es el nivel anterior (ejemplo.com.ar)
SECOND_LEVEL = {
    "com.ar", "gob.ar", "net.ar", "org.ar", "edu.ar", "mil.ar", "int.ar", "tur.ar",
    "com.br", "gov.br", "net.br", "org.br", "edu.br", "com.mx", "gob.mx", "org.mx", "edu.mx", "net.mx",
    "com.co", "gov.co", "org.co", "edu.co", "com.pe", "gob.pe", "org.pe", "edu.pe", "com.uy", "gub.uy",
    "org.uy", "edu.uy", "com.ve", "gob.ve", "com.ec", "gob.ec", "com.py", "gov.py", "com.bo", "gob.bo",
    "co.cl", "gob.cl", "gob.es", "com.es", "org.es", "edu.es", "nom.es",
    "co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "gov.au", "co.jp", "co.nz", "co.in", "com.cn",
}
COMMON_TLDS = {"com", "net", "org", "es", "ar", "mx", "br", "co", "cl", "pe", "uy", "io", "app", "gov", "edu"}


def registrable_domain(host):
    """«login.banco.com.ar» -> «banco.com.ar»; «a.b.example.com» -> «example.com»."""
    host = host.lower().rstrip(".")
    labels = host.split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in SECOND_LEVEL:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:]) if len(labels) >= 2 else host


def _is_ip(host):
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return bool(re.fullmatch(r"\d+", host))  # http://3232235777 también es una IP


def link_warnings(url):
    """Lista de avisos (textos cortos) para mostrar antes de abrir el enlace. Vacía si no hay nada raro."""
    try:
        u = urllib.parse.urlsplit(url.strip())
    except ValueError:
        return ["El enlace está mal formado."]
    host = (u.hostname or "").lower()
    warnings = []
    if u.scheme.lower() == "http":
        warnings.append("La conexión no está cifrada (http).")
    if u.username or "@" in u.netloc:
        warnings.append(f"El enlace no lleva a donde parece: el destino real es {host or '?'}.")
    if not host:
        return warnings
    if _is_ip(host):
        warnings.append("Lleva a una dirección IP en vez de a un dominio.")
        return warnings
    if host.startswith("xn--") or ".xn--" in host or not host.isascii():
        try:
            shown = host.encode("ascii").decode("idna") if host.isascii() else host
        except UnicodeError:
            shown = host
        warnings.append(f"El dominio usa caracteres de otros alfabetos que pueden imitar a otro ({shown}).")
    real = registrable_domain(host)
    if real in SHORTENERS or host in SHORTENERS:
        warnings.append("Enlace acortado: no se sabe a dónde lleva hasta abrirlo.")
    sub = host[: -len(real)].rstrip(".")
    # «banco.com.ar.cuenta-segura.xyz»: lo de delante parece un dominio, pero el real es el del final
    if sub and any(label in COMMON_TLDS for label in sub.split(".")):
        warnings.append(f"Ojo: el dominio real es {real}; lo de delante son subdominios.")
    return warnings
