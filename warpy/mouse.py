import ctypes
from typing import Optional

from warpy import lib
from warpy.config import config_get_int, config_input_match
from warpy.platform import platform
from warpy.schemas import InputEvent, Screen


class MouseController:
    """
    Main controller class for mouse movement.
    """

    def __init__(self):
        # Constants
        self.v0 = 0.0
        self.vf = 0.0
        self.vd = 0.0
        self.a0 = 0.0
        self.a1 = 0.0
        self.inc = 15

        # State variables
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.resting = True
        self.mode_slow = False
        self.cx = 0.0  # Current x position
        self.cy = 0.0  # Current y position
        self.v = 0.0  # Current velocity
        self.a = 0.0  # Current acceleration
        self.opnum = 0  # Operation number
        self.last_update = 0  # Time of last update
        self.sw = 0  # Screen width
        self.sh = 0  # Screen height
        self.cursor_size = 0

    def tonum(self, code: int) -> int:
        """Convert input code to number if it's a digit"""
        name = platform.input_lookup_name(ctypes.c_uint8(code), ctypes.c_int(0))
        if not name:
            return -1

        try:
            first_char = str(name)[0]
            if first_char < "0" or first_char > "9":
                return -1
            return ord(first_char) - ord("0")
        except (TypeError, IndexError):
            return -1

    def update_cursor_position(self, scr):
        """Update cursor position from platform"""
        ix = ctypes.c_int(0)
        iy = ctypes.c_int(0)
        sw = ctypes.c_int(0)
        sh = ctypes.c_int(0)
        platform.mouse_get_position(
            ctypes.byref(scr), ctypes.byref(ix), ctypes.byref(iy)
        )
        platform.screen_get_dimensions(scr, ctypes.byref(sw), ctypes.byref(sh))

        self.sw, self.sh = sw.value, sh.value

        self.cx = float(ix.value)
        self.cy = float(iy.value)

    def tick(self, scr):
        """Update cursor position based on current state"""
        t = lib.get_time_us()
        elapsed = (t - self.last_update) / 1000.0  # convert to ms
        self.last_update = t

        dx = self.right - self.left
        dy = self.down - self.up

        maxx = self.sw - self.cursor_size
        maxy = self.sh - self.cursor_size // 2
        miny = self.cursor_size // 2
        minx = 1

        if not dx and not dy:
            self.resting = True
            return

        if self.resting:
            self.update_cursor_position(scr)
            if not self.mode_slow:
                self.v = self.v0
            self.resting = False

        self.cx += self.v * elapsed * dx
        self.cy += self.v * elapsed * dy
        self.v += elapsed * self.a

        if self.v > self.vf:
            self.v = self.vf

        # Constrain position within screen bounds
        self.cx = max(minx, self.cx)
        self.cy = max(miny, self.cy)
        self.cy = min(maxy, self.cy)
        self.cx = min(maxx, self.cx)

        platform.mouse_move(scr, ctypes.c_int(int(self.cx)), ctypes.c_int(int(self.cy)))

    def process_key(
        self,
        ev: Optional[InputEvent],
        up_key: str,
        down_key: str,
        left_key: str,
        right_key: str,
        scr: Screen,
    ) -> bool:
        """
        Process key events for mouse movement.
        Returns True if cursor position was updated.
        """
        ret = False

        # Handle timeout case
        if not ev:
            self.tick(scr)
            return self.left or self.right or self.up or self.down

        # Handle numeric keys
        n = self.tonum(ev.code)
        if n != -1 and ev.mods == 0:
            if ev.pressed:
                self.opnum = self.opnum * 10 + n

            # Allow 0 on its own to propagate as a special case
            if self.opnum == 0:
                return False
            else:
                return True

        # Handle direction keys
        if config_input_match(ev, down_key):
            self.down = ev.pressed
            ret = True
        elif config_input_match(ev, left_key):
            self.left = ev.pressed
            ret = True
        elif config_input_match(ev, right_key):
            self.right = ev.pressed
            ret = True
        elif config_input_match(ev, up_key):
            self.up = ev.pressed
            ret = True

        # Handle operation number
        if self.opnum and ret:
            x = self.right - self.left
            y = self.down - self.up
            self.update_cursor_position(scr)
            self.cx += self.inc * self.opnum * x
            self.cy += self.inc * self.opnum * y
            platform.mouse_move(scr, int(self.cx), int(self.cy))
            self.opnum = 0
            self.left = False
            self.right = False
            self.up = False
            self.down = False
            return True

        self.tick(scr)
        return ret

    def fast(self):
        """Set fast acceleration mode"""
        self.a = self.a1

    def normal(self):
        """Set normal speed mode"""
        self.v = self.v0
        self.a = self.a0
        self.mode_slow = False

    def slow(self):
        """Set slow speed mode"""
        self.v = self.vd
        self.a = 0
        self.mode_slow = True

    def reset(self, scr):
        """Reset mouse state"""
        self.opnum = 0
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.a = self.a0
        self.v = self.v0
        self.update_cursor_position(scr)
        self.tick(scr)

    def init(self):
        """Initialize mouse settings from config"""
        # Get screen dimensions to calculate cursor size
        self.inc = 15

        # pixels/ms
        self.cursor_size = (config_get_int("cursor_size") * self.sh) // 1080
        self.v0 = config_get_int("speed") / 1000.0
        self.vf = config_get_int("max_speed") / 1000.0
        self.vd = config_get_int("decelerator_speed") / 1000.0
        self.a0 = config_get_int("acceleration") / 1000000.0
        self.a1 = config_get_int("accelerator_acceleration") / 1000000.0
        self.a = self.a0


# Create a singleton instance
_controller = MouseController()


def tonum(code):
    return _controller.tonum(code)


def update_cursor_position(scr):
    _controller.update_cursor_position(scr)


def tick(scr):
    _controller.tick(scr)


def mouse_process_key(ev, up_key, down_key, left_key, right_key, scr):
    return _controller.process_key(ev, up_key, down_key, left_key, right_key, scr)


def mouse_fast():
    _controller.fast()


def mouse_normal():
    _controller.normal()


def mouse_slow():
    _controller.slow()


def mouse_reset(scr):
    _controller.reset(scr)


def init_mouse():
    _controller.init()
