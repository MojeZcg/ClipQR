"""Selección de una zona de la pantalla."""
from clipqr.ui.region import selection_box, to_image_box
from clipqr.winplatform import monitor_area, virtual_screen, work_area


def test_drag_in_any_direction_gives_the_same_box():
    assert selection_box(100, 50, 300, 250) == (100, 50, 300, 250)
    assert selection_box(300, 250, 100, 50) == (100, 50, 300, 250)


def test_tiny_drag_is_a_click():
    assert selection_box(100, 100, 104, 300) is None
    assert selection_box(100, 100, 100, 100) is None


def test_screen_to_image_with_monitor_on_the_left():
    # escritorio virtual que empieza en x=-1920 (monitor a la izquierda del principal)
    assert to_image_box((-1820, 10, -1620, 210), (-1920, 0)) == (100, 10, 300, 210)


def test_virtual_screen_contains_every_monitor():
    vs = virtual_screen()
    m = monitor_area((work_area().left + 1, work_area().top + 1))
    assert vs.left <= m.left and vs.top <= m.top and vs.right >= m.right and vs.bottom >= m.bottom
