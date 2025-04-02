import ctypes

from warpy import lib, platform
from warpy.schemas import Hint, Screen

screen_chars = "jkl;asdfg"


lib.get_screen.argtypes = [ctypes.c_int]
lib.get_screen.restype = ctypes.POINTER(Screen)

def screen_selection_mode():
    # Draw hints on screens
    n_screens = lib.get_nr_screens()
    for i in range(n_screens):
        screen_ptr = lib.get_screen(i)
        hint = Hint()
        w = ctypes.c_int()
        h = ctypes.c_int()

        platform.screen_get_dimensions(screen_ptr, ctypes.byref(w), ctypes.byref(h))

        hint.x = w.value // 2 - 25
        hint.y = h.value // 2 - 25
        hint.w = 50
        hint.h = 50
        hint.label = screen_chars[i].encode("utf-8")

        platform.hint_draw(screen_ptr, ctypes.byref(hint), 1)

    platform.commit()
    platform.input_grab_keyboard()

    # Wait for key press
    while True:
        ev = platform.input_next_event(0)
        if ev.contents.pressed:
            break

    platform.input_ungrab_keyboard()

    # Move mouse to selected screen
    for i in range(n_screens):
        screen_ptr = lib.get_screen(i)

        key = lib.input_event_tostr(ev)
        if key.decode("utf-8") == screen_chars[i]:
            w = ctypes.c_int()
            h = ctypes.c_int()
            platform.screen_get_dimensions(screen_ptr, ctypes.byref(w), ctypes.byref(h))
            platform.mouse_move(screen_ptr, w.value // 2, h.value // 2)

    # Clear screens
    for i in range(n_screens):
        screen_ptr = lib.get_screen(i)
        platform.screen_clear(screen_ptr)

    platform.commit()
