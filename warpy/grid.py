import ctypes

from warpy.config import (
    config_get,
    config_get_int,
    config_input_match,
    config_input_whitelist,
)
from warpy.mouse import mouse_process_key, mouse_reset


class Grid:
    def __init__(self, platform, scr):
        self.platform = platform
        self.grid_width: int = 0
        self.grid_height: int = 0
        self.scr = scr

    def draw_grid(
        self, color: str, sz: int, nc: int, nr: int, x: int, y: int, w: int, h: int
    ) -> None:
        ygap = (h - ((nr + 1) * sz)) // nr
        xgap = (w - ((nc + 1) * sz)) // nc

        if xgap < 0 or ygap < 0:
            return

        for i in range(nr + 1):
            self.platform.screen_draw_box(
                self.scr, x, y + (ygap + sz) * i, w, sz, color.encode("utf-8")
            )

        for i in range(nc + 1):
            self.platform.screen_draw_box(
                self.scr, x + (xgap + sz) * i, y, sz, h, color.encode("utf-8")
            )

    def redraw(self, mx: int, my: int, force: bool = False) -> None:
        x = mx - self.grid_width // 2
        y = my - self.grid_height // 2

        nc = config_get_int("grid_nc")
        nr = config_get_int("grid_nr")
        cursz = config_get_int("cursor_size")
        gsz = config_get_int("grid_size")
        gbsz = config_get_int("grid_border_size")
        gbcol = config_get("grid_border_color")
        gcol = config_get("grid_color")

        gh = self.grid_height
        gw = self.grid_width

        # Using class variables to maintain state between calls
        if not hasattr(self, "omx") or not hasattr(self, "omy"):
            self.omx = 0
            self.omy = 0

        # Avoid unnecessary redraws
        if not force and self.omx == mx and self.omy == my:
            return

        self.omx = mx
        self.omy = my

        self.platform.screen_clear(self.scr)

        # Draw the border
        self.draw_grid(gbcol, gsz + gbsz * 2, nc, nr, x, y, gw, gh)

        # Draw the grid
        self.draw_grid(
            gcol, gsz, nc, nr, x + gbsz, y + gbsz, gw - gbsz * 2, gh - gbsz * 2
        )

        self.platform.screen_draw_box(
            self.scr,
            x + gw // 2 - cursz // 2,
            y + gh // 2 - cursz // 2,
            cursz,
            cursz,
            config_get("cursor_color").encode("utf-8"),
        )

        self.platform.commit()

    def grid_mode(self):
        mx: int = 0
        my: int = 0
        ev = None

        nc = config_get_int("grid_nc")
        nr = config_get_int("grid_nr")

        self.platform.input_grab_keyboard()
        self.platform.mouse_hide()
        mouse_reset(self.scr)

        self.platform.mouse_get_position(ctypes.byref(self.scr), None, None)
        width_ptr = ctypes.c_int()
        height_ptr = ctypes.c_int()
        self.platform.screen_get_dimensions(
            self.scr, ctypes.byref(width_ptr), ctypes.byref(height_ptr)
        )
        self.grid_width = width_ptr.value
        self.grid_height = height_ptr.value

        mx = self.grid_width // 2
        my = self.grid_height // 2
        self.platform.mouse_move(self.scr, mx, my)
        self.redraw(mx, my, True)

        keys = [
            "grid_up",
            "grid_down",
            "grid_right",
            "grid_left",
            "grid_cut_up",
            "grid_cut_down",
            "grid_cut_right",
            "grid_cut_left",
            "grid_keys",
            "buttons",
            "oneshot_buttons",
            "grid",
            "hint",
            "exit",
            "drag",
            "grid_exit",
        ]

        config_input_whitelist(keys, len(keys))

        while True:
            ev = self.platform.input_next_event(10)
            x_ptr = ctypes.c_int()
            y_ptr = ctypes.c_int()
            self.platform.mouse_get_position(
                None, ctypes.byref(x_ptr), ctypes.byref(y_ptr)
            )
            mx, my = x_ptr.value, y_ptr.value

            if not ev:
                continue
            else:
                ev = ev.contents

            if mouse_process_key(
                ev, "grid_up", "grid_down", "grid_left", "grid_right", self.scr
            ):
                self.redraw(mx, my, False)
                continue

            if ev and not ev.pressed:
                continue

            if (idx := config_input_match(ev, "grid_keys")) and idx <= nc * nr:
                my = (my - self.grid_height // 2) + (self.grid_height // nr) * (
                    (idx - 1) // nc
                )
                mx = (mx - self.grid_width // 2) + (self.grid_width // nc) * (
                    (idx - 1) % nc
                )

                self.grid_height //= nr
                self.grid_width //= nc
                mx += self.grid_width // 2
                my += self.grid_height // 2

                self.platform.mouse_move(self.scr, mx, my)
                self.redraw(mx, my, False)

            if config_input_match(ev, "grid_cut_up"):
                my -= self.grid_height // 4
                self.grid_height //= 2

                self.platform.mouse_move(self.scr, mx, my)
                self.redraw(mx, my, False)

            elif config_input_match(ev, "grid_cut_down"):
                my += self.grid_height // 4
                self.grid_height //= 2

                self.platform.mouse_move(self.scr, mx, my)
                self.redraw(mx, my, False)

            elif config_input_match(ev, "grid_cut_left"):
                mx -= self.grid_width // 4
                self.grid_width //= 2

                self.platform.mouse_move(self.scr, mx, my)
                self.redraw(mx, my, False)

            elif config_input_match(ev, "grid_cut_right"):
                mx += self.grid_width // 4
                self.grid_width //= 2

                self.platform.mouse_move(self.scr, mx, my)
                self.redraw(mx, my, False)

            elif config_input_match(ev, "buttons") or config_input_match(
                ev, "oneshot_buttons"
            ):
                break

            if (
                config_input_match(ev, "grid")
                or config_input_match(ev, "hint")
                or config_input_match(ev, "exit")
                or config_input_match(ev, "drag")
                or config_input_match(ev, "grid_exit")
            ):
                break

            self.redraw(mx, my, False)

        config_input_whitelist(None, 0)
        self.platform.screen_clear(self.scr)
        self.platform.mouse_show()

        self.platform.input_ungrab_keyboard()

        self.platform.commit()
        return ev


def grid_mode(platform, scr):
    grid = Grid(platform, scr)
    return grid.grid_mode()
