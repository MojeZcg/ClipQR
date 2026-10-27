"""Textos que nombran cosas del sistema operativo («Iniciar con Windows», el Explorador, Recortes…).
En Windows se usan los de siempre; en macOS y Linux, su variante. Cada texto se escribe entero dentro de _()
para que lo encuentre el test de traducciones."""
from clipqr.i18n import _
from clipqr.platform import SYSTEM


def autostart_label(system=SYSTEM):
    return _("Iniciar con Windows") if system == "windows" else _("Iniciar al iniciar sesión")


def theme_auto_label(system=SYSTEM):
    return _("Como Windows") if system == "windows" else _("Como el sistema")


def copied_files_hint(system=SYSTEM):
    return (_("Imágenes copiadas desde el Explorador de archivos.") if system == "windows"
            else _("Imágenes copiadas desde el gestor de archivos."))


def delete_capture_hint(system=SYSTEM):
    if system == "windows":
        return _("Cuando una captura de pantalla tiene un QR o un código de barras, la envía a la Papelera (se puede "
                 "recuperar) para no llenar Imágenes › Capturas de pantalla. Cada aviso indica que está activo.")
    return _("Cuando una captura de pantalla tiene un QR o un código de barras, la envía a la Papelera (se puede "
             "recuperar) para no llenar la carpeta de capturas. Cada aviso indica que está activo.")


def empty_history_text(system=SYSTEM):
    if system == "macos":
        return _("Aún no se ha detectado ningún código.\n"
                 "Haz una captura de un QR con ⌃⇧⌘4 (la copia al portapapeles).")
    if system == "linux":
        return _("Aún no se ha detectado ningún código.\n"
                 "Haz una captura de un QR (Impr Pant) y cópiala.")
    return _("Aún no se ha detectado ningún código.\n"
             "Haz una captura de un QR (Win+Shift+S o Impr Pant).")


def first_run_text(system=SYSTEM):
    """Primer arranque (cuando ClipQR activa solo el inicio automático)."""
    if system == "macos":
        return _("ClipQR está activo en la barra de menús.\n"
                 "Haz una captura de un QR y aparecerá aquí.\n"
                 "Se iniciará solo al iniciar sesión.")
    if system == "linux":
        return _("ClipQR está activo en la bandeja del sistema.\n"
                 "Haz una captura de un QR y aparecerá aquí.\n"
                 "Se iniciará solo al iniciar sesión.")
    return _("ClipQR está activo en la bandeja (junto al reloj).\n"
             "Haz una captura de un QR y aparecerá aquí.\n"
             "Se iniciará solo con Windows.")


def read_wifi_question(system=SYSTEM):
    if system == "windows":
        return _("Se leerá de Windows la red a la que estás conectado y su contraseña, y se mostrarán aquí. "
                 "¿Continuar?")
    return _("Se leerá del sistema la red a la que estás conectado y su contraseña, y se mostrarán aquí. "
             "¿Continuar?")


def hotkeys_problem(reason):
    """Por qué no funcionan los atajos globales (None si funcionan)."""
    if reason == "wayland":
        return _("En Wayland las aplicaciones no pueden usar atajos de teclado globales.\n"
                 "Usa el menú de ClipQR en la bandeja del sistema.")
    if reason == "accessibility":
        return _("Para usar los atajos de teclado, permite ClipQR en\n"
                 "Ajustes del Sistema › Privacidad y seguridad › Accesibilidad.")
    if reason == "missing":
        return _("Los atajos de teclado globales no están disponibles: falta el módulo pynput.")
    return None
