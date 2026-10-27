"""Lo que depende del sistema operativo, con una sola API para Windows, macOS y Linux.

El resto de ClipQR importa de aquí (from clipqr.platform import …) y nunca usa ctypes.windll, winreg ni
AppKit directamente. Cada sistema tiene su módulo (windows.py, macos.py, linux.py) y se elige con imports
normales dentro de un if: nada de importlib, que PyInstaller no vería.

API común:
  SYSTEM                         «windows», «macos» o «linux»
  FROZEN, PACKAGED               empaquetado con PyInstaller / instalado desde la Microsoft Store (MSIX)
  config_dir()                   carpeta de ajustes
  clipboard_token()              cambia cuando cambia el portapapeles (None si no se puede saber)
  CLIPBOARD_POLL_MS              cada cuánto mirarlo
  copy_image_to_clipboard(img)   copia una imagen PIL
  grab_screen()                  captura de toda la pantalla (lanza excepción si el sistema no lo permite)
  system_theme(), tray_is_dark() tema del sistema y de la barra donde va el icono
  style_window(win, …)           bordes y barra de título (solo Windows)
  work_area(), work_areas(), monitor_area(), virtual_screen(), cursor_pos()
  bring_to_front(win)            trae al frente una ventana de Tk aunque ClipQR esté en segundo plano
  screenshots_folder(), send_to_trash(path), open_path(ruta_o_url)
  single_instance(), release_single_instance()
  autostart_entry(argv), autostart_current(), autostart_set(argv), autostart_remove()
  connect_wifi(), current_wifi()
  HotkeyManager(), hotkeys_unavailable_reason()
  start_tray(icon, on_error), tray_options()
"""
import sys

from clipqr.platform.common import Area, FROZEN, area_containing, clamp_to_area, config_dir, bind_tk

if sys.platform == "win32":
    SYSTEM = "windows"
    from clipqr.platform.windows import (
        CLIPBOARD_POLL_MS, FONT_SCALE, PACKAGED, HotkeyManager, autostart_current, autostart_entry,
        autostart_remove, autostart_set, beep, bring_to_front, clipboard_token, clipboard_tools_missing,
        connect_wifi, copy_image_to_clipboard, current_wifi, cursor_pos, enable_dpi_awareness, grab_screen,
        gui_python, hotkeys_unavailable_reason, installed_by_setup, monitor_area, msix_set_startup,
        msix_startup_state, open_path, pick_fonts, prepare_app, release_single_instance, screen_scale,
        screenshots_folder, send_to_trash, shortcut_paths, single_instance, start_tray, style_window,
        system_theme, tray_is_dark, tray_options, ui_langid, ui_locale_name, uninstall_program,
        uninstall_registration, virtual_screen, work_area, work_areas)
elif sys.platform == "darwin":
    SYSTEM = "macos"
    from clipqr.platform.common import gui_python
    from clipqr.platform.macos import (
        CLIPBOARD_POLL_MS, FONT_SCALE, PACKAGED, HotkeyManager, autostart_current, autostart_entry,
        autostart_remove, autostart_set, beep, bring_to_front, clipboard_token, clipboard_tools_missing,
        connect_wifi, copy_image_to_clipboard, current_wifi, cursor_pos, enable_dpi_awareness, grab_screen,
        hotkeys_unavailable_reason, installed_by_setup, monitor_area, msix_set_startup,
        msix_startup_state, open_path, pick_fonts, prepare_app, release_single_instance, screen_scale,
        screenshots_folder, send_to_trash, shortcut_paths, single_instance, start_tray, style_window,
        system_theme, tray_is_dark, tray_options, ui_langid, ui_locale_name, uninstall_program,
        uninstall_registration, virtual_screen, work_area, work_areas)
else:
    SYSTEM = "linux"
    from clipqr.platform.common import gui_python
    from clipqr.platform.linux import (
        CLIPBOARD_POLL_MS, FONT_SCALE, PACKAGED, HotkeyManager, autostart_current, autostart_entry,
        autostart_remove, autostart_set, beep, bring_to_front, clipboard_token, clipboard_tools_missing,
        connect_wifi, copy_image_to_clipboard, current_wifi, cursor_pos, enable_dpi_awareness, grab_screen,
        hotkeys_unavailable_reason, installed_by_setup, monitor_area, msix_set_startup,
        msix_startup_state, open_path, pick_fonts, prepare_app, release_single_instance, screen_scale,
        screenshots_folder, send_to_trash, shortcut_paths, single_instance, start_tray, style_window,
        system_theme, tray_is_dark, tray_options, ui_langid, ui_locale_name, uninstall_program,
        uninstall_registration, virtual_screen, work_area, work_areas)

__all__ = [
    "SYSTEM", "FROZEN", "PACKAGED", "CLIPBOARD_POLL_MS", "FONT_SCALE", "Area", "area_containing", "clamp_to_area",
    "config_dir", "bind_tk", "gui_python", "HotkeyManager", "autostart_current", "autostart_entry",
    "autostart_remove", "autostart_set", "beep", "bring_to_front", "clipboard_token", "clipboard_tools_missing",
    "connect_wifi", "copy_image_to_clipboard", "current_wifi", "cursor_pos", "enable_dpi_awareness", "grab_screen",
    "hotkeys_unavailable_reason", "installed_by_setup", "monitor_area", "msix_set_startup", "msix_startup_state",
    "open_path", "pick_fonts", "prepare_app", "release_single_instance", "screen_scale", "screenshots_folder",
    "send_to_trash", "shortcut_paths", "single_instance", "start_tray", "style_window", "system_theme",
    "tray_is_dark", "tray_options", "ui_langid", "ui_locale_name", "uninstall_program", "uninstall_registration",
    "virtual_screen", "work_area", "work_areas",
]
