import ctypes


MODE_RESERVED = 1
MODE_HISTORY = 2
MODE_HINT = 3
MODE_HINT2 = 4
MODE_GRID = 5
MODE_NORMAL = 6
MODE_HINTSPEC = 7
MODE_SCREEN_SELECTION = 8
MODE_SMART_HINT = 9


MAX_BOXES = 64
class InputEvent(ctypes.Structure):
    _fields_ = [
        ('code', ctypes.c_uint8),
        ('mods', ctypes.c_uint8),
        ('pressed', ctypes.c_uint8)
    ]

class Hint(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('w', ctypes.c_int),
        ('h', ctypes.c_int),
        ('label', ctypes.c_char * 16)
    ]

class Box(ctypes.Structure):
    _fields_ = [
        ('win', ctypes.c_ulong),    # X11 Window is unsigned long
        ('color', ctypes.c_char * 32)
    ]

class Screen(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int),
        ('w', ctypes.c_int),
        ('h', ctypes.c_int),
        ('buf', ctypes.c_void_p),  # Pixmap can be treated as a pointer
        ('hintwin', ctypes.c_void_p),  # Window as pointer
        ('cached_hintwin', ctypes.c_void_p),  # Window as pointer
        ('cached_hintbuf', ctypes.c_void_p),  # Pixmap can be treated as pointer
        ('cached_hints', Hint * 32),  # Array of hint structures
        ('nr_cached_hints', ctypes.c_size_t),
        ('boxes', Box * MAX_BOXES),
        ('nr_boxes', ctypes.c_size_t)
    ]
class Platform(ctypes.Structure):
    _fields_ = [
        # Input method pointers
        ('input_grab_keyboard', ctypes.CFUNCTYPE(None)),
        ('input_ungrab_keyboard', ctypes.CFUNCTYPE(None)),
        ('input_next_event', ctypes.CFUNCTYPE(ctypes.POINTER(InputEvent), ctypes.c_int)),
        ('input_lookup_code', ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int))),
        ('input_lookup_name', ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_uint8, ctypes.c_int)),
        ('input_wait', ctypes.CFUNCTYPE(ctypes.POINTER(InputEvent), ctypes.POINTER(InputEvent), ctypes.c_size_t)),

        # Mouse method pointers
        ('mouse_move', ctypes.CFUNCTYPE(None, ctypes.POINTER(Screen), ctypes.c_int, ctypes.c_int)),
        ('mouse_down', ctypes.CFUNCTYPE(None, ctypes.c_int)),
        ('mouse_up', ctypes.CFUNCTYPE(None, ctypes.c_int)),
        ('mouse_click', ctypes.CFUNCTYPE(None, ctypes.c_int)),
        ('mouse_get_position', ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.POINTER(Screen)), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))),
        ('mouse_show', ctypes.CFUNCTYPE(None)),
        ('mouse_hide', ctypes.CFUNCTYPE(None)),

        # Screen method pointers
        ('screen_get_dimensions', ctypes.CFUNCTYPE(None, ctypes.POINTER(Screen), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))),
        ('screen_draw_box', ctypes.CFUNCTYPE(None, ctypes.POINTER(Screen), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p)),
        ('screen_clear', ctypes.CFUNCTYPE(None, ctypes.POINTER(Screen))),
        ('screen_list', ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.POINTER(Screen)), ctypes.POINTER(ctypes.c_size_t))),

        # Hint method pointers
        ('init_hint', ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)),
        ('monitor_file', ctypes.CFUNCTYPE(None, ctypes.c_char_p)),
        ('hint_draw', ctypes.CFUNCTYPE(None, ctypes.POINTER(Screen), ctypes.POINTER(Hint), ctypes.c_size_t)),

        # Other method pointers
        ('scroll', ctypes.CFUNCTYPE(None, ctypes.c_int)),
        ('copy_selection', ctypes.CFUNCTYPE(None)),
        ('commit', ctypes.CFUNCTYPE(None))
    ]

MAX_SCREENS = 32

class XScreens(ctypes.Structure):
    _fields_ = [
        ('screens', Screen * MAX_SCREENS),
        ('nr_screens', ctypes.c_int)
    ]
