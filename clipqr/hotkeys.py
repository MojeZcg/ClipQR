"""Atajos de teclado globales (funcionan aunque ClipQR no tenga el foco), con RegisterHotKey.

Windows entrega WM_HOTKEY al hilo que registró el atajo, así que un hilo propio registra los atajos y
espera mensajes; al pulsarse uno, llama a su función (que debe pasar el trabajo al hilo de Tk).
"""
import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

MODS = {"ctrl": 0x2, "control": 0x2, "alt": 0x1, "shift": 0x4, "win": 0x8}
MOD_NOREPEAT = 0x4000
KEYS = {"espacio": 0x20, "space": 0x20, "enter": 0x0D, "tab": 0x09, "esc": 0x1B, "insert": 0x2D,
        "imprpant": 0x2C, "printscreen": 0x2C, "pausa": 0x13}
KEYS.update({f"f{i}": 0x6F + i for i in range(1, 13)})
WM_HOTKEY, WM_QUIT, WM_APP = 0x0312, 0x0012, 0x8000


def parse_hotkey(text):
    """«Ctrl+Alt+Q» -> (modificadores, código de tecla). Exige al menos un modificador."""
    parts = [p.strip().lower() for p in text.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError(f"Atajo incompleto: {text!r}")
    *mods, key = parts
    flags = 0
    for m in mods:
        if m not in MODS:
            raise ValueError(f"Modificador desconocido: {m!r}")
        flags |= MODS[m]
    if key in KEYS:
        vk = KEYS[key]
    elif len(key) == 1 and key.isalnum():
        vk = ord(key.upper())
    else:
        raise ValueError(f"Tecla desconocida: {key!r}")
    return flags | MOD_NOREPEAT, vk


class HotkeyManager:
    """Registra atajos en un hilo propio. set() reemplaza todos los atajos; devuelve los que fallaron
    (por ejemplo, porque otra aplicación ya usa esa combinación)."""

    def __init__(self):
        self._thread_id = None
        self._ready = threading.Event()
        self._pending = None
        self._result = None
        self._done = threading.Event()
        self._callbacks = {}
        threading.Thread(target=self._loop, daemon=True).start()
        self._ready.wait(2)

    def set(self, hotkeys):
        """hotkeys: {texto del atajo: función}. Devuelve la lista de atajos que no se pudieron registrar."""
        self._pending = dict(hotkeys)
        self._done.clear()
        user32.PostThreadMessageW(self._thread_id, WM_APP, 0, 0)
        self._done.wait(2)
        return self._result or []

    def stop(self):
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def _apply(self):
        for hid in list(self._callbacks):
            user32.UnregisterHotKey(None, hid)
        self._callbacks.clear()
        failed = []
        for hid, (text, fn) in enumerate(self._pending.items(), start=1):
            try:
                mods, vk = parse_hotkey(text)
            except ValueError:
                failed.append(text)
                continue
            if user32.RegisterHotKey(None, hid, mods, vk):
                self._callbacks[hid] = fn
            else:
                failed.append(text)
        self._result = failed
        self._done.set()

    def _loop(self):
        self._thread_id = kernel32.GetCurrentThreadId()
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)  # crea la cola de mensajes del hilo
        self._ready.set()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_APP:
                self._apply()
            elif msg.message == WM_HOTKEY and msg.wParam in self._callbacks:
                try:
                    self._callbacks[msg.wParam]()
                except Exception:
                    pass
        for hid in list(self._callbacks):
            user32.UnregisterHotKey(None, hid)
