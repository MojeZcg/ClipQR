"""Colocación del aviso con varios monitores."""
import sys

import pytest

windows_only = pytest.mark.skipif(sys.platform != "win32", reason="usa la API de Windows")

from clipqr.platform import Area, area_containing, clamp_to_area, work_area, work_areas  # noqa: E402

LEFT = Area(-1920, 0, 0, 1040)    # monitor a la izquierda del principal
MAIN = Area(0, 0, 2560, 1400)


def test_area_containing_picks_the_right_monitor():
    assert area_containing(-500, 300, [MAIN, LEFT]) == LEFT
    assert area_containing(100, 100, [MAIN, LEFT]) == MAIN


def test_point_on_a_disconnected_monitor_has_no_area():
    assert area_containing(4000, 300, [MAIN, LEFT]) is None


def test_clamp_keeps_window_inside_its_monitor():
    assert clamp_to_area(-100, 900, 400, 300, LEFT) == (-400, 740)
    assert clamp_to_area(-1950, -20, 400, 300, LEFT) == (-1920, 0)
    assert clamp_to_area(500, 500, 400, 300, MAIN) == (500, 500)


@windows_only  # en macOS y Linux los monitores se preguntan a Tk (hace falta una ventana)
def test_real_monitors_are_detected():
    areas = work_areas()
    assert areas and all(a.right > a.left and a.bottom > a.top for a in areas)
    assert work_area() in areas  # el monitor del ratón es uno de ellos
