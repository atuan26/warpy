import ctypes

from warpy.schemas import InputEvent, Screen

lib = ctypes.CDLL("/home/tuanna/Documents/warpd/warpd/lib/linux_X.so")

get_time_us = lib.get_time_us
get_time_us.argtypes = []
get_time_us.restype = ctypes.c_uint64

lib.get_nr_screens.restype = ctypes.c_size_t
n_screens = lib.get_nr_screens()

lib.get_screen.argtypes = [ctypes.c_int]
lib.get_screen.restype = ctypes.POINTER(Screen)

lib.input_eq.argtypes = [ctypes.POINTER(InputEvent), ctypes.c_char_p]
lib.input_eq.restype = ctypes.c_int
