import ctypes

from warpy.config import config_get, config_get_int
from warpy.platform import platform
from warpy.schemas import Hint

MAX_HINTS = 2048
MAX_BOXES = 64


hints = ctypes.POINTER(Hint)()
matched = (Hint * MAX_HINTS)()

nr_hints = ctypes.c_size_t()
nr_matched = ctypes.c_size_t()

last_selected_hint = ctypes.create_string_buffer(32)


def init_hints():
    platform.init_hint(
        config_get("hint_bgcolor").encode("utf-8"),
        config_get("hint_fgcolor").encode("utf-8"),
        config_get_int("hint_border_radius"),
        config_get("hint_font").encode("utf-8"),
    )


def filter(scr, s: str, matched, nr_matched):
    # global matched, nr_matched

    matched = [hint for hint in hints if hint.label.startswith(s)]
    nr_matched = len(matched)

    platform.screen_clear(scr)
    platform.hint_draw(scr, matched, nr_matched)
    platform.commit()


def get_hint_size(scr):
    sw = ctypes.c_int()
    sh = ctypes.c_int()
    platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))
    if sw.value < sh.value:
        sw, sh = sh, sw

    w = sw.value * config_get_int("hint_size") / 1000
    h = sh.value * config_get_int("hint_size") / 1000
    return w, h


def generate_fullscreen_hints(scr, hints):
    return


def hint_selection(scr, hints, nr_hints):
    return


def sift():
    return


def hintspec_mode():
    return


def full_hint_mode(second_pass: int):
    return 0


def history_hint_mode():
    return 0
