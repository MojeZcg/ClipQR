"""Atajos de teclado globales (funcionan aunque ClipQR no tenga el foco).

Los atajos se guardan como texto («Win+Shift+Q»). En Windows los registra RegisterHotKey
(clipqr/platform/windows.py); en macOS y Linux, pynput si está instalado: en macOS «Win» es ⌘ y hace
falta el permiso de Accesibilidad; en Linux funciona con X11, no con Wayland.
"""
import threading

MODS = {"ctrl": 0x2, "control": 0x2, "alt": 0x1, "shift": 0x4, "win": 0x8}
MOD_NOREPEAT = 0x4000
KEYS = {"espacio": 0x20, "space": 0x20, "enter": 0x0D, "tab": 0x09, "esc": 0x1B, "insert": 0x2D,
        "imprpant": 0x2C, "printscreen": 0x2C, "pausa": 0x13}
KEYS.update({f"f{i}": 0x6F + i for i in range(1, 13)})

# nombres de pynput (https://pynput.readthedocs.io): «Win» es ⌘ en macOS y Súper en Linux
PYNPUT_MODS = {"ctrl": "<ctrl>", "control": "<ctrl>", "alt": "<alt>", "shift": "<shift>", "win": "<cmd>"}
PYNPUT_KEYS = {"espacio": "<space>", "space": "<space>", "enter": "<enter>", "tab": "<tab>", "esc": "<esc>",
               "insert": "<insert>", "imprpant": "<print_screen>", "printscreen": "<print_screen>",
               "pausa": "<pause>"}
PYNPUT_KEYS.update({f"f{i}": f"<f{i}>" for i in range(1, 13)})


def _split(text):
    parts = [p.strip().lower() for p in text.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError(f"Atajo incompleto: {text!r}")
    *mods, key = parts
    for m in mods:
        if m not in MODS:
            raise ValueError(f"Modificador desconocido: {m!r}")
    if key not in KEYS and not (len(key) == 1 and key.isalnum()):
        raise ValueError(f"Tecla desconocida: {key!r}")
    return mods, key


def parse_hotkey(text):
    """«Ctrl+Alt+Q» -> (modificadores, código de tecla). Exige al menos un modificador."""
    mods, key = _split(text)
    flags = 0
    for m in mods:
        flags |= MODS[m]
    vk = KEYS[key] if key in KEYS else ord(key.upper())
    return flags | MOD_NOREPEAT, vk


def to_pynput(text):
    """«Win+Shift+Q» -> «<cmd>+<shift>+q» (formato de pynput.keyboard.GlobalHotKeys)."""
    mods, key = _split(text)
    seen = []
    for m in mods:
        if PYNPUT_MODS[m] not in seen:
            seen.append(PYNPUT_MODS[m])
    return "+".join(seen + [PYNPUT_KEYS.get(key, key)])


class PynputHotkeyManager:
    """Atajos globales con pynput (macOS y Linux X11). Misma interfaz que el de Windows: set() reemplaza
    todos los atajos y devuelve los que no se pudieron activar. Si pynput no está, `available` es False y
    set() no hace nada."""

    def __init__(self, unavailable_reason=None, trusted=None):
        self._listener = None
        self._trusted = trusted  # macOS: función que dice si hay permiso de Accesibilidad
        self._lock = threading.Lock()
        self.reason = unavailable_reason
        self.available = unavailable_reason is None
        if self.available:
            try:
                from pynput import keyboard
                self._keyboard = keyboard
            except Exception:  # sin pynput, o sin servidor X al que conectarse
                self.available = False
                self.reason = "missing"

    def set(self, hotkeys):
        """hotkeys: {texto del atajo: función}. Devuelve la lista de atajos que no se pudieron activar."""
        self.stop()
        if not self.available:
            return []
        mapping, failed = {}, []
        for text, fn in hotkeys.items():
            try:
                mapping[to_pynput(text)] = self._safe(fn)
            except ValueError:
                failed.append(text)
        if mapping:
            with self._lock:
                try:
                    self._listener = self._keyboard.GlobalHotKeys(mapping)
                    self._listener.daemon = True
                    self._listener.start()
                except Exception:
                    self._listener = None
                    return list(hotkeys)
            # macOS: sin el permiso de Accesibilidad el listener arranca pero no recibe ninguna tecla
            if self._trusted is not None and not self._trusted():
                self.reason = "accessibility"
        return failed

    @staticmethod
    def _safe(fn):
        def call():
            try:
                fn()
            except Exception:
                pass
        return call

    def stop(self):
        with self._lock:
            if self._listener is not None:
                try:
                    self._listener.stop()
                except Exception:
                    pass
                self._listener = None
