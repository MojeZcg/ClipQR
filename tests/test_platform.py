"""Capa de plataforma: la lógica pura de macOS y Linux (se prueba en cualquier sistema) y la API común."""
import os
import plistlib
import sys

import pytest

from clipqr import platform as plat
from clipqr import settings
from clipqr.hotkeys import parse_hotkey, to_pynput
from clipqr.platform import common, linux, macos


# --- carpeta de ajustes ------------------------------------------------------------------------------------

def test_config_dir_windows():
    assert common.config_dir("win32", {"APPDATA": r"C:\Users\ana\AppData\Roaming"}, home="C:\\Users\\ana") == \
        os.path.join(r"C:\Users\ana\AppData\Roaming", "ClipQR")


def test_config_dir_macos():
    assert common.config_dir("darwin", {}, home="/Users/ana") == \
        os.path.join("/Users/ana", "Library", "Application Support", "ClipQR")


def test_config_dir_linux_xdg_and_default():
    assert common.config_dir("linux", {"XDG_CONFIG_HOME": "/x/conf"}, home="/home/ana") == \
        os.path.join("/x/conf", "ClipQR")
    assert common.config_dir("linux", {}, home="/home/ana") == os.path.join("/home/ana", ".config", "ClipQR")


def test_settings_use_the_platform_folder():
    assert settings.CONFIG_DIR == plat.config_dir()


# --- atajos de teclado -------------------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("Win+Shift+Q", "<cmd>+<shift>+q"),
    ("Ctrl+Shift+Space", "<ctrl>+<shift>+<space>"),
    ("Ctrl+Alt+Win+Q", "<ctrl>+<alt>+<cmd>+q"),
    ("ctrl + espacio", "<ctrl>+<space>"),
    ("Alt+Shift+F9", "<alt>+<shift>+<f9>"),
    ("Win+Alt+7", "<cmd>+<alt>+7"),
])
def test_hotkeys_in_pynput_syntax(text, expected):
    assert to_pynput(text) == expected


@pytest.mark.parametrize("text", ["Q", "Ctrl+", "Hyper+Q", "Ctrl+Flecha"])
def test_invalid_hotkeys_for_pynput(text):
    with pytest.raises(ValueError):
        to_pynput(text)


def test_mac_defaults_avoid_system_shortcuts():
    mac = settings.default_settings("macos")
    taken = {"Win+Shift+Q", "Win+Shift+3", "Win+Shift+4", "Win+Shift+5", "Ctrl+Win+Q", "Ctrl+Win+Space",
             "Alt+Win+Q", "Win+Space"}
    for key in ("hotkey_focus", "hotkey_region", "hotkey_create"):
        assert mac[key] not in taken
        parse_hotkey(mac[key])  # válidos
    for choices in settings.HOTKEY_CHOICES["macos"].values():
        assert not set(choices) & taken
    # Windows no cambia
    assert settings.default_settings("windows")["hotkey_region"] == "Win+Shift+Q"
    assert settings.default_settings("linux")["hotkey_create"] == "Win+Shift+G"


def test_hotkey_labels_per_system():
    assert settings.hotkey_label("Ctrl+Alt+Win+Q", "macos") == "⌃⌥⌘Q"
    assert settings.hotkey_label("Win+Shift+Space", "macos") == "⇧⌘Espacio"
    assert settings.hotkey_label("Win+Shift+Q", "linux") == "Super+Shift+Q"
    assert settings.hotkey_label("Win+Shift+Q", "windows") == "Win+Shift+Q"


def test_pynput_manager_without_pynput_is_harmless():
    m = linux.PynputHotkeyManager("wayland")
    assert not m.available and m.reason == "wayland"
    assert m.set({"Win+Shift+Q": lambda: None}) == []
    m.stop()


def test_wayland_has_no_global_hotkeys():
    assert linux.hotkeys_unavailable_reason({"XDG_SESSION_TYPE": "wayland"}) == "wayland"
    assert linux.hotkeys_unavailable_reason({"WAYLAND_DISPLAY": "wayland-0"}) == "wayland"
    assert linux.hotkeys_unavailable_reason({"DISPLAY": ":0", "XDG_SESSION_TYPE": "x11"}) is None


# --- iniciar al iniciar sesión -----------------------------------------------------------------------------

def test_windows_run_value_keeps_its_format():
    if sys.platform != "win32":
        pytest.skip("windows.py solo se importa en Windows")
    from clipqr.platform import windows
    assert windows.autostart_entry([r"C:\Apps\ClipQR.exe", "--autostart"]) == r'"C:\Apps\ClipQR.exe" --autostart'
    assert windows.autostart_entry([r"C:\Py\pythonw.exe", r"C:\src\main.py", "--autostart"]) == \
        r'"C:\Py\pythonw.exe" "C:\src\main.py" --autostart'


def test_launch_agent_plist():
    text = macos.autostart_entry(["/Applications/ClipQR.app/Contents/MacOS/ClipQR", "--autostart"])
    data = plistlib.loads(text.encode("utf-8"))
    assert data == {"Label": "io.github.mojezcg.clipqr", "RunAtLoad": True, "ProcessType": "Interactive",
                    "ProgramArguments": ["/Applications/ClipQR.app/Contents/MacOS/ClipQR", "--autostart"]}
    assert macos.LAUNCH_AGENT.endswith(os.path.join("Library", "LaunchAgents", "io.github.mojezcg.clipqr.plist"))


def test_linux_autostart_desktop_file():
    text = linux.autostart_entry(["/home/ana/.local/share/ClipQR/ClipQR", "--autostart"])
    assert text.startswith("[Desktop Entry]\n")
    assert "\nType=Application\n" in text and "\nName=ClipQR\n" in text
    assert "\nExec=/home/ana/.local/share/ClipQR/ClipQR --autostart\n" in text
    assert "\nIcon=clipqr\n" in text and "\nX-GNOME-Autostart-enabled=true\n" in text
    assert linux.AUTOSTART_FILE.endswith(os.path.join("autostart", "clipqr.desktop"))


def test_desktop_exec_quoting():
    assert linux.desktop_exec(["/usr/bin/python3", "/home/ana/Mis cosas/main.py", "--autostart"]) == \
        '/usr/bin/python3 "/home/ana/Mis cosas/main.py" --autostart'
    assert linux.desktop_exec(['/opt/a"b$c']) == '"/opt/a\\"b\\$c"'


def test_autostart_roundtrip_in_a_temporary_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(linux, "AUTOSTART_FILE", str(tmp_path / "autostart" / "clipqr.desktop"))
    argv = ["/opt/ClipQR/ClipQR", "--autostart"]
    assert linux.autostart_current() is None
    linux.autostart_set(argv)
    assert linux.autostart_current() == linux.autostart_entry(argv)
    linux.autostart_remove()
    assert linux.autostart_current() is None


# --- Wi‑Fi ----------------------------------------------------------------------------------------------------

def test_nmcli_connect_command():
    assert linux.nmcli_connect_args("Casa", "secreta", "WPA") == \
        ["nmcli", "device", "wifi", "connect", "Casa", "password", "secreta"]
    assert linux.nmcli_connect_args("Bar", "", "nopass") == ["nmcli", "device", "wifi", "connect", "Bar"]
    assert linux.nmcli_connect_args("Oculta", "x1", "WPA", hidden=True)[-2:] == ["hidden", "yes"]
    assert linux.nmcli_connect_args("Vieja", "abcde", "WEP")[-2:] == ["wep-key-type", "key"]


def test_nmcli_parsing():
    assert linux.parse_nmcli_active("no:Vecino\nyes:Mi\\:Red\nno:Otra\n") == "Mi:Red"
    assert linux.parse_nmcli_active("no:Vecino\n") is None
    assert linux.security_for_key_mgmt("wpa-psk", "x") == "WPA"
    assert linux.security_for_key_mgmt("sae", "x") == "WPA"
    assert linux.security_for_key_mgmt("none", "abcde") == "WEP"
    assert linux.security_for_key_mgmt("", "") == "nopass"


PORTS = """
Hardware Port: Ethernet
Device: en1
Ethernet Address: aa:bb:cc:dd:ee:ff

Hardware Port: Wi-Fi
Device: en0
Ethernet Address: 11:22:33:44:55:66
"""


def test_networksetup_command():
    assert macos.parse_wifi_device(PORTS) == "en0"
    assert macos.parse_wifi_device("Hardware Port: Ethernet\nDevice: en1\n") is None
    assert macos.networksetup_join_args("en0", "Casa", "secreta") == \
        ["networksetup", "-setairportnetwork", "en0", "Casa", "secreta"]
    assert macos.networksetup_join_args("en0", "Bar", "") == ["networksetup", "-setairportnetwork", "en0", "Bar"]
    assert macos.parse_airport_network("Current Wi-Fi Network: Mi Red\n") == "Mi Red"
    assert macos.parse_airport_network("You are not associated with an AirPort network.") is None


# --- tema, idioma, pantalla, papelera -----------------------------------------------------------------------

def test_system_theme_parsing():
    assert macos.parse_interface_style("Dark\n", 0) == "dark"
    assert macos.parse_interface_style("The domain/default pair does not exist", 1) == "light"
    assert linux.parse_color_scheme("'prefer-dark'") == "dark"
    assert linux.parse_color_scheme("'default'") == "light"
    assert linux.parse_color_scheme("'Adwaita-dark'") == "dark"


def test_mac_preferred_language():
    assert macos.parse_apple_languages('(\n    "es-AR",\n    "en-US"\n)') == "es-AR"
    assert macos.parse_apple_languages("(\n    \"pt-BR\"\n)") == "pt-BR"
    assert macos.parse_apple_languages("") is None


def test_linux_work_area():
    assert linux.parse_workarea("_NET_WORKAREA = 0, 32, 1920, 1048, 0, 32, 1920, 1048") == \
        common.Area(0, 32, 1920, 1080)
    assert linux.parse_workarea("_NET_WORKAREA:  not found.") is None


def test_freedesktop_trash(tmp_path):
    f = tmp_path / "Captura.png"
    f.write_bytes(b"png")
    trash = tmp_path / "Trash"
    assert linux.trash_manually(str(f), str(trash))
    assert not f.exists()
    assert (trash / "files" / "Captura.png").read_bytes() == b"png"
    info = (trash / "info" / "Captura.png.trashinfo").read_text(encoding="utf-8")
    assert info.startswith("[Trash Info]\nPath=") and "Captura.png" in info and "DeletionDate=" in info
    # otro archivo con el mismo nombre no pisa al primero
    f.write_bytes(b"otro")
    linux.trash_manually(str(f), str(trash))
    assert (trash / "files" / "Captura.2.png").read_bytes() == b"otro"


def test_posix_single_instance(tmp_path):
    if sys.platform == "win32":
        pytest.skip("en Windows se usa un mutex")
    assert common.posix_single_instance(str(tmp_path))
    common.posix_release_single_instance()
    assert common.posix_single_instance(str(tmp_path))
    common.posix_release_single_instance()


def test_common_api_is_complete():
    for name in plat.__all__:
        assert hasattr(plat, name), name
    assert plat.SYSTEM in ("windows", "macos", "linux")


def test_backends_offer_the_same_api():
    names = {n for n in plat.__all__ if n not in ("SYSTEM", "FROZEN", "Area", "area_containing", "clamp_to_area",
                                                   "config_dir", "bind_tk", "gui_python")}
    for backend in (macos, linux):
        missing = [n for n in names if not hasattr(backend, n)]
        assert not missing, (backend.__name__, missing)
