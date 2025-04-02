import ctypes

from warpd.platform import platform

v0 = vf = vd = a = a0 = a1 = ctypes.c_double(0)
inc = ctypes.c_int(0)
sw = sh = ctypes.c_int(0)

left = right = up = down = ctypes.c_int(0)
resting = ctypes.c_int(1)
mode_slow = ctypes.c_int(0)

cx = cy = ctypes.c_double(0)
v = ctypes.c_double(0)

opnum = ctypes.c_int(0)

cursor_size = ctypes.c_int(0)

# TODO:
# static int tonum(uint8_t code)
# {
# 	const char *name = platform->input_lookup_name(code, 0);

# 	if (!name)
# 		return -1;

# 	if (name[0] > '9' || name[0] < '0')
# 		return -1;

# 	return name[0] - '0';
# }


def update_cursor_position(screen_ptr):
    global cy, cx
    ix = iy = ctypes.c_int()

    platform.mouse_get_position(screen_ptr, ctypes.byref(ix), ctypes.byref(iy))
    platform.screen_get_dimensions(screen_ptr, ctypes.byref(sw), ctypes.byref(sh))

    cx = ctypes.c_double(ix.value)
    cy = ctypes.c_double(iy.value)


def tick():
    global maxy, miny, minx, dx, dy
    ...


def mouse_process_key(*args, **kwargs) -> int: ...


def mouse_fast():
    a = a1


def mouse_normal():
    v = v0
    a = a0
    mode_slow = 0


def mouse_slow():
    v = vd
    a = 0
    mode_slow = 1


def mouse_reset(screen_ptr):
    opnum = 0
    left = 0
    right = 0
    up = 0
    down = 0
    a = a0
    v = v0

    update_cursor_position(screen_ptr)

    tick()


def init_mouse():
    ...
    # inc = 15 // TODO: make this configurable

    # /* pixels/ms */

    # cursor_size = (config_get_int("cursor_size") * sh) / 1080;

    # v0 = (double)config_get_int("speed") / 1000.0;
    # vf = (double)config_get_int("max_speed") / 1000.0;
    # vd = (double)config_get_int("decelerator_speed") / 1000.0;
    # a0 = (double)config_get_int("acceleration") / 1000000.0;
    # a1 = (double)config_get_int("accelerator_acceleration") / 1000000.0;

    # a = a0;
