import ctypes

from warpy.config import config_get, config_get_int, config_input_match, config_input_whitelist
from warpy.histfile import histfile_read
from warpy.history import hist_add
from warpy.input import input_event_tostr
from warpy.platform import platform
from warpy.schemas import Hint

MAX_HINTS = 2048
MAX_BOXES = 64


class HintModel:
    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.w: int = 0
        self.h: int = 0
        self.label: str = ""

    def to_struct(self) -> Hint:
        """Convert Python Hint to C-compatible struct"""
        struct = Hint()
        struct.x = self.x
        struct.y = self.y
        struct.w = self.w
        struct.h = self.h
        struct.label = self.label.encode('utf-8')
        return struct

class HintManager:
    def __init__(self):
        self.hints: list[HintModel] = []
        self.matched: list[HintModel] = []
        self.nr_hints: int = 0
        self.nr_matched: int = 0
        self.last_selected_hint: str = ""
        self.MAX_HINTS: int = 2048

    def filter(self, scr, s: str) -> None:
        self.nr_matched = 0
        self.matched = []

        for i in range(self.nr_hints):
            if self.hints[i].label.startswith(s):
                if self.nr_matched < self.MAX_HINTS:
                    self.matched.append(self.hints[i])
                    self.nr_matched += 1

        platform.screen_clear(scr)
        hint_array = (Hint * self.nr_matched)()

        for i in range(self.nr_matched):
            hint_array[i] = self.matched[i].to_struct()
        platform.hint_draw(scr, hint_array, self.nr_matched)
        platform.commit()

    def get_hint_size(self, scr, w: ctypes.c_int, h: ctypes.c_int) -> tuple[int, int]:
        platform.screen_get_dimensions(scr, ctypes.byref(w), ctypes.byref(h))

        sw_val = w.value
        sh_val = h.value

        if sw_val < sh_val:
            sw_val, sh_val = sh_val, sw_val

        ww = (sw_val * config_get_int("hint_size")) // 1000
        hh = (sh_val * config_get_int("hint_size")) // 1000

        return ww, hh

    def generate_fullscreen_hints(self, scr) -> list[HintModel]:
        sw = ctypes.c_int()
        sh = ctypes.c_int()
        w, h = self.get_hint_size(scr, sw, sh)

        platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))
        sw_val, sh_val = sw.value, sh.value

        chars = config_get("hint_chars")
        nr = len(chars)
        nc = len(chars)

        colgap = sw_val // nc - w
        rowgap = sh_val // nr - h

        x_offset = (sw_val - nc * w - (nc - 1) * colgap) // 2
        y_offset = (sh_val - nr * h - (nr - 1) * rowgap) // 2

        x, y = x_offset, y_offset
        n = 0
        generated_hints = []

        for i in range(nc):
            for j in range(nr):
                hint = HintModel()
                hint.x = x
                hint.y = y
                hint.w = w
                hint.h = h
                hint.label = chars[i] + chars[j]

                generated_hints.append(hint)
                n += 1

                y += rowgap + h

            y = y_offset
            x += colgap + w

        return generated_hints

    def hint_selection(self, scr, _hints: list[HintModel], _nr_hints: int) -> int:
        self.hints = _hints
        self.nr_hints = _nr_hints

        self.filter(scr, "")

        rc = 0
        buf = ""
        platform.input_grab_keyboard()
        platform.mouse_hide()

        keys = ["hint_exit", "hint_undo_all", "hint_undo"]
        config_input_whitelist(keys, len(keys))

        while True:
            ev = platform.input_next_event(0)

            if not ev:
                continue
            elif (ev and not ev.contents.pressed):
                continue
            else:
                ev = ev.contents

            if config_input_match(ev, "hint_exit"):
                rc = -1
                break
            elif config_input_match(ev, "hint_undo_all"):
                buf = ""
            elif config_input_match(ev, "hint_undo"):
                if buf:
                    buf = buf[:-1]
            else:
                name = input_event_tostr(ev)

                if not name or len(name) > 1:
                    continue

                buf += name[0]

            self.filter(scr, buf)

            if self.nr_matched == 1:
                h = self.matched[0]

                platform.screen_clear(scr)

                nx = h.x + h.w // 2
                ny = h.y + h.h // 2

                # Wiggle the cursor a single pixel to accommodate
                # text selection widgets which don't like spontaneous
                # cursor warping.
                platform.mouse_move(scr, nx + 1, ny + 1)
                platform.mouse_move(scr, nx, ny)

                self.last_selected_hint = buf
                break
            elif self.nr_matched == 0:
                break

        platform.input_ungrab_keyboard()
        platform.screen_clear(scr)
        platform.mouse_show()
        platform.commit()

        return rc

    def sift(self) -> int:
        gap = config_get_int("hint2_gap_size")
        hint_sz = config_get_int("hint2_size")

        chars = config_get("hint2_chars")
        chars_len = len(chars)

        grid_sz = config_get_int("hint2_grid_size")

        x = ctypes.c_int()
        y = ctypes.c_int()
        sh = ctypes.c_int()
        sw = ctypes.c_int()

        n = 0
        hints = [HintModel() for _ in range(self.MAX_HINTS)]

        scr = platform.mouse_get_position(ctypes.byref(x), ctypes.byref(y))
        platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

        x_val, y_val = x.value, y.value
        sw_val, sh_val = sw.value, sh.value

        gap = (gap * sh_val) // 1000
        hint_sz = (hint_sz * sh_val) // 1000

        x_val -= ((hint_sz + (gap - 1)) * grid_sz) // 2
        y_val -= ((hint_sz + (gap - 1)) * grid_sz) // 2

        for col in range(grid_sz):
            for row in range(grid_sz):
                idx = (row * grid_sz) + col

                if idx < chars_len:
                    hints[n].x = x_val + (hint_sz + gap) * col
                    hints[n].y = y_val + (hint_sz + gap) * row
                    hints[n].w = hint_sz
                    hints[n].h = hint_sz
                    hints[n].label = chars[idx]

                    n += 1

        return self.hint_selection(scr, hints[:n], n)

_hint_manager = HintManager()

def init_hints():
    platform.init_hint(
        config_get("hint_bgcolor").encode("utf-8"),
        config_get("hint_fgcolor").encode("utf-8"),
        config_get_int("hint_border_radius"),
        config_get("hint_font").encode("utf-8"),
    )


def hintspec_mode():
    scr = None
    sw = ctypes.c_int()
    sh = ctypes.c_int()

    hints = [HintModel() for _ in range(_hint_manager.MAX_HINTS)]
    n = 0

    scr = platform.mouse_get_position(None, None)
    platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

    w, h = _hint_manager.get_hint_size(scr, sw, sh)

    try:
        while True:
            line = input()
            parts = line.split()
            if len(parts) < 3:
                break

            hints[n].label = parts[0][:15]  # Limiting to 15 chars as in the C code
            hints[n].x = int(parts[1])
            hints[n].y = int(parts[2])
            hints[n].w = w
            hints[n].h = h
            hints[n].x -= w // 2
            hints[n].y -= h // 2

            n += 1
    except EOFError:
        pass

    return _hint_manager.hint_selection(scr, hints[:n], n)


def full_hint_mode(second_pass: int):
    mx = ctypes.c_int()
    my = ctypes.c_int()

    scr = platform.mouse_get_position(ctypes.byref(mx), ctypes.byref(my))
    hist_add(mx.value, my.value)

    hints = _hint_manager.generate_fullscreen_hints(scr)
    _hint_manager.nr_hints = len(hints)

    if _hint_manager.hint_selection(scr, hints, _hint_manager.nr_hints) != 0:
        return -1

    if second_pass:
        return _hint_manager.sift()
    else:
        return 0


def history_hint_mode(scr):
    hints = [HintModel() for _ in range(_hint_manager.MAX_HINTS)]
    ents = None
    sw = ctypes.c_int()
    sh = ctypes.c_int()

    platform.mouse_get_position(ctypes.byref(scr), None, None)
    platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

    ents, n = histfile_read()

    w, h = _hint_manager.get_hint_size(scr, sw, sh)

    for i in range(n):
        hints[i].w = w
        hints[i].h = h
        hints[i].x = ents[i].x - w // 2
        hints[i].y = ents[i].y - h // 2
        hints[i].label = chr(ord('a') + i)

    return _hint_manager.hint_selection(scr, hints[:n], n)
