import ctypes

from warpy.schemas import InputEvent, Platform

from .lib import lib

PLATFORM_MOD_CONTROL = 1
PLATFORM_MOD_SHIFT = 2
PLATFORM_MOD_META = 4
PLATFORM_MOD_ALT = 8


x_init = lib.x_init
x_init.argtypes = [ctypes.POINTER(Platform)]
x_init.restype = None

platform = Platform()
platform.input_next_event.restype = ctypes.POINTER(InputEvent)


def platform_run(main):
    global platform
    x_init(ctypes.byref(platform))
    exit(main(platform))
