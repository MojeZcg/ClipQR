"""Colores de los temas y de cada tipo de código."""

THEMES = {
    "dark": dict(bg="#202020", card="#2b2b2b", border="#3d3d3d", fg="#f3f3f3", muted="#a3a3a3",
                 textbg="#1c1c1c", btn="#383838", btn_hover="#454545", ok="#2e7d32"),
    "light": dict(bg="#f3f3f3", card="#ffffff", border="#d6d6d6", fg="#1b1b1b", muted="#5f5f5f",
                  textbg="#f7f7f7", btn="#e8e8e8", btn_hover="#dadada", ok="#2e7d32"),
}

KINDS = {
    "link": ("", "🔗", "#4f8cff"),
    "wifi": ("", "📶", "#22a06b"),
    "contact": ("", "👤", "#a66cff"),
    "otp": ("", "🔑", "#e8a317"),
    "email": ("", "✉", "#e5484d"),
    "phone": ("", "📞", "#12a594"),
    "sms": ("", "💬", "#12a594"),
    "geo": ("", "📍", "#f76b15"),
    "event": ("", "📅", "#e54666"),
    "text": ("", "📄", "#8b8d98"),
    "product": ("", "🛒", "#0ea5e9"),
}

def _shade(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))
