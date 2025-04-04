import ctypes
from ctypes import byref, c_int
from typing import Optional

from warpy import schemas
from warpy.config import config_input_match, config_input_whitelist
from warpy.grid import grid_mode
from warpy.hint import full_hint_mode, hintspec_mode, history_hint_mode
from warpy.histfile import histfile_add
from warpy.normal import normal_mode
from warpy.schemas import InputEvent
from warpy.screen import screen_selection_mode


def mode_loop(scr, platform, initial_mode: int, oneshot: int, record_history: int):
    mode = initial_mode
    rc = 0
    ev: Optional[InputEvent] = None

    while 1:
        btn = 0
        print("NEW LOOP")

        config_input_whitelist([], 0)
        match mode:
            case schemas.MODE_HISTORY:
                if history_hint_mode(scr) < 0:
                    return rc
                ev = None
                mode = schemas.MODE_NORMAL
            case schemas.MODE_HINTSPEC:
                hintspec_mode()
            case schemas.MODE_NORMAL:
                ev = normal_mode(scr, ev, oneshot)

                if config_input_match(ev, "history"):
                    mode = schemas.MODE_HISTORY
                elif config_input_match(ev, "hint"):
                    mode = schemas.MODE_HINT
                elif config_input_match(ev, "hint2"):
                    mode = schemas.MODE_HINT2
                elif config_input_match(ev, "grid"):
                    mode = schemas.MODE_GRID
                elif config_input_match(ev, "screen"):
                    mode = schemas.MODE_SCREEN_SELECTION
                elif rc := config_input_match(ev, "oneshot_buttons") or not ev:
                    return rc
                elif config_input_match(ev, "exit") or not ev:
                    return 0
            case schemas.MODE_HINT2:
                ...
            case schemas.MODE_HINT:
                if full_hint_mode(mode == schemas.MODE_HINT2) < 2:
                    return rc
                ev = None
                mode = schemas.MODE_NORMAL
            case schemas.MODE_GRID:
                ev = grid_mode()
                if config_input_match(ev, "grid_exit"):
                    ev = None
                mode = schemas.MODE_NORMAL
            case schemas.MODE_SCREEN_SELECTION:
                screen_selection_mode()
                mode = schemas.MODE_NORMAL
                ev = None
            case schemas.MODE_SMART_HINT:
                ...

        if (
            oneshot
            and initial_mode != schemas.MODE_NORMAL
            or (btn := config_input_match(ev, "buttons"))
        ):
            x = c_int()
            y = c_int()
            platform.mouse_get_position(ctypes.byref(scr), None, None)
            platform.mouse_get_position(None, byref(x), byref(y))

            if record_history:
                histfile_add(x.value, y.value)

            if mode == schemas.MODE_HINTSPEC:
                ...
            else:
                print(x, y)

            return btn
