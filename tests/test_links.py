"""Enlaces conocidos: WhatsApp, Telegram, redes, tiendas, calendarios, UPI y criptomonedas."""
import pytest

from clipqr.payloads import analyze


def test_whatsapp_con_mensaje():
    r = analyze("https://wa.me/5491112345678?text=Hola%20quiero%20info")
    items = dict(r.items)
    assert r.title == "WhatsApp" and r.headline == ("Chat", "+5491112345678")
    assert items["Mensaje"] == "Hola quiero info"
    assert ("Copiar número", "copy", "+5491112345678") in r.actions
    assert "no se envía" in r.subtitle


def test_whatsapp_api_y_grupo():
    assert analyze("https://api.whatsapp.com/send?phone=34600000000").headline == ("Chat", "+34600000000")
    assert analyze("https://chat.whatsapp.com/AbCdEf123").title == "WhatsApp · grupo"


def test_telegram():
    r = analyze("https://t.me/clipqr_bot")
    assert r.headline == ("Usuario", "@clipqr_bot")
    assert analyze("https://t.me/+AbCdEf").title == "Telegram · grupo"


@pytest.mark.parametrize("url, title, user", [
    ("https://www.instagram.com/clipqr/", "Instagram · perfil", "@clipqr"),
    ("https://x.com/clipqr", "X (Twitter) · perfil", "@clipqr"),
    ("https://www.tiktok.com/@clipqr", "TikTok · perfil", "@clipqr"),
    ("https://www.linkedin.com/in/juan-perez", "LinkedIn · perfil", "juan-perez"),
    ("https://www.linkedin.com/company/clipqr", "LinkedIn · empresa", "clipqr"),
    ("https://www.youtube.com/@clipqr", "YouTube · perfil", "@clipqr"),
])
def test_perfiles(url, title, user):
    r = analyze(url)
    assert r.kind == "link" and r.title == title and r.headline == ("Usuario", user)


def test_publicaciones_y_videos():
    assert analyze("https://www.instagram.com/p/ABC123/").title == "Instagram · publicación"
    assert analyze("https://youtu.be/dQw4w9WgXcQ").headline == ("Vídeo de YouTube", "dQw4w9WgXcQ")
    assert analyze("https://www.youtube.com/watch?v=dQw4w9WgXcQ").title == "YouTube · vídeo"
    r = analyze("https://github.com/MojeZcg/ClipQR")
    assert r.headline == ("Repositorio", "MojeZcg/ClipQR")


def test_tiendas_de_apps():
    r = analyze("https://apps.apple.com/ar/app/mercado-pago/id925436649")
    assert r.title == "App · App Store" and r.headline == ("App", "Mercado Pago")
    r = analyze("https://play.google.com/store/apps/details?id=com.mercadopago.wallet")
    assert r.title == "App · Google Play" and dict(r.items)["Identificador"] == "com.mercadopago.wallet"


def test_calendario():
    r = analyze("webcal://example.com/feriados.ics")
    assert r.kind == "event" and r.title == "Calendario"
    assert ("Copiar enlace", "copy", "https://example.com/feriados.ics") in r.actions


def test_upi():
    r = analyze("upi://pay?pa=tienda@okicici&pn=Tienda%20Demo&am=250.00&cu=INR&tn=Pedido%2012")
    items = dict(r.items)
    assert r.kind == "payment" and r.title == "Pago QR · UPI"
    assert r.headline == ("Importe", "₹250.00") and items["Concepto"] == "Pedido 12"
    assert r.actions == [("Copiar dirección UPI", "copy", "tienda@okicici")]


def test_bitcoin_solo_copia():
    r = analyze("bitcoin:bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq?amount=0.001&label=Donaciones")
    assert r.title == "Cripto · Bitcoin" and r.headline == ("Importe", "0.001 Bitcoin")
    assert [a[1] for a in r.actions] == ["copy"]  # nunca un botón que abra la billetera
    assert r.warnings and "revertir" in r.warnings[0]


def test_enlace_normal_sigue_igual():
    r = analyze("https://example.com/2024/01/20240101/nota")
    assert r.kind == "link" and r.title == "Enlace"
    assert analyze("http://wa.me/5491112345678").warnings  # sin https: aviso de siempre
