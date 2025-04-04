import ctypes
import logging
import sys
from typing import Optional

from warpy import lib, platform
from warpy.config import (
    config_get,
    config_get_int,
    config_input_match,
    config_input_whitelist,
)
from warpy.histfile import histfile_add
from warpy.history import hist_add, hist_get, hist_next, hist_prev
from warpy.mouse import (
    mouse_fast,
    mouse_normal,
    mouse_process_key,
    mouse_reset,
    mouse_slow,
)
from warpy.schemas import InputEvent
from warpy.scroll import (
    SCROLL_DOWN,
    SCROLL_UP,
    scroll_accelerate,
    scroll_decelerate,
    scroll_stop,
    scroll_tick,
)

platform.mouse_get_position.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
platform.mouse_get_position.restype = None

platform.screen_get_dimensions.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]
platform.screen_get_dimensions.restype = None

platform.input_next_event.argtypes = [ctypes.c_int]
platform.input_next_event.restype = ctypes.POINTER(InputEvent)


def redraw(scr, x: ctypes.c_int, y: ctypes.c_int, hide_cursor):
    sw = ctypes.c_int(0)
    sh = ctypes.c_int(0)

    platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

    gap = 10
    indicator_size = int(config_get_int("indicator_size") * sh.value / 1080)
    indicator_color = config_get("indicator_color")
    curcol = config_get("cursor_color")
    indicator = config_get("indicator")
    cursz = config_get_int("cursor_size")

    platform.screen_clear(scr)

    if not hide_cursor:
        platform.screen_draw_box(
            scr,
            ctypes.c_int(x.value + 1),
            ctypes.c_int(y.value - cursz // 2),
            ctypes.c_int(cursz),
            ctypes.c_int(cursz),
            curcol.encode("utf-8"),
        )

    indicator_positions = {
        "bottomleft": (gap, sh.value - indicator_size - gap),
        "topleft": (gap, gap),
        "topright": (sw.value - indicator_size - gap, gap),
        "bottomright": (
            sw.value - indicator_size - gap,
            sh.value - indicator_size - gap,
        ),
    }

    if indicator in indicator_positions:
        ix, iy = indicator_positions[indicator]
        platform.screen_draw_box(
            scr,
            ctypes.c_int(ix),
            ctypes.c_int(iy),
            ctypes.c_int(indicator_size),
            ctypes.c_int(indicator_size),
            indicator_color.encode("utf-8"),
        )
        platform.commit()
    logging.debug(f'\x1b[36m🔍Current pos: x, y = \x1b[32m{x.value, y.value}\x1b[0m')


def move(scr, x: ctypes.c_int, y: ctypes.c_int, hide_cursor):
    platform.mouse_move(scr, x, y)
    redraw(scr, x, y, hide_cursor)


def normal_mode(scr, start_ev: Optional[InputEvent], oneshot: int) -> Optional[InputEvent]:
    cursz = config_get_int("cursor_size")
    system_cursor = config_get_int("normal_system_cursor")
    blink_interval = config_get("normal_blink_interval")

    ev = InputEvent(0, False, 0)
    on_time = ctypes.c_int()
    off_time = ctypes.c_int()
    sh = ctypes.c_int()
    sw = ctypes.c_int()
    mx = ctypes.c_int()
    my = ctypes.c_int()
    dragging = ctypes.c_int()
    show_cursor = not system_cursor

    blink_values = list(map(int, blink_interval.split()))
    if len(blink_values) == 1:
        on_time, off_time = blink_values[0], blink_values[0]
    else:
        on_time, off_time = blink_values

    keys = [
        "accelerator",
        "bottom",
        "buttons",
        "copy_and_exit",
        "decelerator",
        "down",
        "drag",
        "end",
        "exit",
        "grid",
        "hint",
        "hint2",
        "hist_back",
        "hist_forward",
        "history",
        "left",
        "middle",
        "oneshot_buttons",
        "print",
        "right",
        "screen",
        "scroll_down",
        "scroll_up",
        "start",
        "top",
        "up",
    ]

    platform.input_grab_keyboard()

    platform.mouse_get_position(ctypes.byref(scr), ctypes.byref(mx), ctypes.byref(my))
    platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

    if not system_cursor:
        platform.mouse_hide()

    mouse_reset(scr)
    redraw(scr, mx, my, not show_cursor)

    time = 0
    last_blink_update = 0
    while 1:
        config_input_whitelist(keys, len(keys))
        if start_ev is None:
            ev = platform.input_next_event(ctypes.c_int(10))

            if ev:
                ev = ev.contents
                logging.debug(f'\x1b[36m🔍 Pressed = \x1b[32m{ev.code, ev.mods, ev.pressed}\x1b[0m')
            else:
                ev = None

            time += 10
        else:
            ev = start_ev
            start_ev = None

        platform.mouse_get_position(
            ctypes.byref(scr), ctypes.byref(mx), ctypes.byref(my)
        )

        if not system_cursor and on_time:
            if show_cursor and (time - last_blink_update) >= on_time:
                show_cursor = 0
                redraw(scr, mx, my, not show_cursor)
                last_blink_update = time
            elif not show_cursor and (time - last_blink_update) >= off_time:
                show_cursor = 1
                redraw(scr, mx, my, not show_cursor)
                last_blink_update = time

        scroll_tick()
        if mouse_process_key(ev, "up", "down", "left", "right", scr):
            redraw(scr, mx, my, not show_cursor)
            continue

        if not ev:
            continue
        elif config_input_match(ev, "scroll_down"):
            print(f"\x1b[36m🔍 1 = \x1b[32m{1}\x1b[0m")
            redraw(scr, mx, my, 1)

            if ev.pressed:
                scroll_stop()
                scroll_accelerate(SCROLL_DOWN)
            else:
                scroll_decelerate()
        elif config_input_match(ev, "scroll_up"):
            redraw(scr, mx, my, 1)

            if ev.pressed:
                scroll_stop()
                scroll_accelerate(SCROLL_UP)
            else:
                scroll_decelerate()
        elif config_input_match(ev, "accelerator"):
            if ev.pressed:
                mouse_fast()
            else:
                mouse_normal()
        elif config_input_match(ev, "decelerator"):
            if ev.pressed:
                mouse_slow()
            else:
                mouse_normal()
        elif not ev.pressed:
            next(scr, mx, my)

        if config_input_match(ev, "top"):
            move(scr, mx, ctypes.c_int(cursz // 2), not show_cursor)
        elif config_input_match(ev, "bottom"):
            move(scr, mx, ctypes.c_int(sh.value - cursz // 2), not show_cursor)
        elif config_input_match(ev, "middle"):
            move(scr, mx, ctypes.c_int(sh.value // 2), not show_cursor)
        elif config_input_match(ev, "start"):
            move(scr, ctypes.c_int(1), my, not show_cursor)
        elif config_input_match(ev, "end"):
            move(scr, ctypes.c_int(sw.value - cursz), my, not show_cursor)
        elif config_input_match(ev, "hist_back"):
            hist_add(mx.value, my.value)
            hist_prev()
            get, x, y = hist_get()
            mx = ctypes.c_int(x)
            my = ctypes.c_int(y)

            move(scr, mx, my, not show_cursor)
        elif config_input_match(ev, "hist_forward"):
            hist_next()
            get, x, y = hist_get()
            mx = ctypes.c_int(x)
            my = ctypes.c_int(y)

            move(scr, mx, my, not show_cursor)
        elif config_input_match(ev, "drag"):
            dragging = not dragging
            if dragging:
                platform.mouse_down(config_get_int("drag_button"))
            else:
                platform.mouse_up(config_get_int("drag_button"))
        elif config_input_match(ev, "copy_and_exit"):
            platform.mouse_up(config_get_int("drag_button"))
            platform.copy_selection()
            ev = None
            return exit(scr, ev)
        elif (
            config_input_match(ev, "exit")
            or config_input_match(ev, "grid")
            or config_input_match(ev, "screen")
            or config_input_match(ev, "history")
            or config_input_match(ev, "hint2")
            or config_input_match(ev, "hint")
        ):
            return exit(scr, ev)
        elif config_input_match(ev, "print"):
            print("%d %d %s\n", mx, my, lib.input_event_tostr(ev))
        else:
            if btn:=config_input_match(ev, "buttons"):
                print(f'\x1b[36m🔍 btn = \x1b[32m{btn}\x1b[0m')
                if oneshot:
                    print("%d %d\n", mx, my)
                    sys.exit(btn)

                hist_add(mx.value, my.value)
                histfile_add(mx.value, my.value)
                platform.mouse_click(btn)
            elif btn:=config_input_match(ev, "oneshot_buttons"):
                hist_add(mx.value, my.value)
                platform.mouse_click(btn)

                timeout = config_get_int("oneshot_timeout")

                while 1:
                    ev = platform.input_next_event(timeout)

                    if not ev:
                        break
                    else:
                        ev = ev.contents

                    if ev and ev.pressed and config_input_match(ev, "oneshot_buttons"):
                        platform.mouse_click(btn)

                return exit(scr, ev)


def next(scr, mx, my):
    platform.mouse_get_position(ctypes.byref(scr), ctypes.byref(mx), ctypes.byref(my))
    platform.commit()


def exit(scr, ev: Optional[InputEvent]):
    platform.mouse_show()
    platform.screen_clear(scr)

    platform.input_ungrab_keyboard()

    platform.commit()
    return ev
