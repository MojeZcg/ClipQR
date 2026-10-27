"""Selección de una zona de la pantalla."""
import sys

import pytest

windows_only = pytest.mark.skipif(sys.platform != "win32", reason="usa la API de Windows")

from clipqr.platform import monitor_area, virtual_screen, work_area  # noqa: E402
from clipqr.ui.region import selection_box, to_image_box  # noqa: E402


def test_drag_in_any_direction_gives_the_same_box():
    assert selection_box(100, 50, 300, 250) == (100, 50, 300, 250)
    assert selection_box(300, 250, 100, 50) == (100, 50, 300, 250)


def test_tiny_drag_is_a_click():
    assert selection_box(100, 100, 104, 300) is None
    assert selection_box(100, 100, 100, 100) is None


def test_screen_to_image_with_monitor_on_the_left():
    # escritorio virtual que empieza en x=-1920 (monitor a la izquierda del principal)
    assert to_image_box((-1820, 10, -1620, 210), (-1920, 0)) == (100, 10, 300, 210)


def test_retina_capture_is_twice_the_points():
    # macOS: la captura viene en píxeles (2 por punto) y la selección en puntos de Tk
    assert to_image_box((110, 20, 210, 120), (10, 0), scale=2) == (200, 40, 400, 240)


@windows_only
def test_virtual_screen_contains_every_monitor():
    vs = virtual_screen()
    m = monitor_area((work_area().left + 1, work_area().top + 1))
    assert vs.left <= m.left and vs.top <= m.top and vs.right >= m.right and vs.bottom >= m.bottom
