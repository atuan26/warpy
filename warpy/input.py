import ctypes

from warpy.platform import (
    platform,
    PLATFORM_MOD_ALT,
    PLATFORM_MOD_CONTROL,
    PLATFORM_MOD_META,
    PLATFORM_MOD_SHIFT,
)
from warpy.schemas import InputEvent

cached_mods = {}


def input_parse_string(ev: InputEvent, s: str):
    if not s or s[0] == 0:
        return 0

    ev.mods = 0
    ev.pressed = 1
    print(f'\x1b[36m🔍 s = \x1b[32m{s}\x1b[0m')

    while s[1] == "-":
        match s[0]:
            case "A":
                ev.mods |= PLATFORM_MOD_ALT
                break
            case "M":
                ev.mods |= PLATFORM_MOD_META
                break
            case "S":
                ev.mods |= PLATFORM_MOD_SHIFT
                break
            case "C":
                ev.mods |= PLATFORM_MOD_CONTROL
                break
            case _:
                print(f"{s} is not a valid modifier\n")
                exit(-1)

        s += 2

    if s[0]:
        shifted = 0

        code = platform.input_lookup_code(
            s.encode("utf-8"), ctypes.byref(ctypes.c_int(shifted))
        )
        ev.code = code
        if shifted:
            ev.mods |= PLATFORM_MOD_SHIFT

        if not ev.code:
            return -1

    return 0


def input_event_tostr(ev: InputEvent):
    s = []
    name = platform.input_lookup_name(
        ev.code, ctypes.c_int(1 if ev.modes & PLATFORM_MOD_SHIFT else 0)
    )

    if not ev:
        return "NULL"

    if ev.mods & PLATFORM_MOD_CONTROL:
        s.append("C-")
    if ev.mods & PLATFORM_MOD_ALT:
        s.append("A-")
    if ev.mods & PLATFORM_MOD_META:
        s.append("M-")

    s.append(name if name else "UNDEFINED")

    return "".join(s)


def input_eq(ev: InputEvent | None, string: str) -> int:
    if not ev:
        return 0

    if ev.pressed:
        mods = ev.mods
        cached_mods[ev.code] = ev.mods
    else:
        mods = cached_mods.get(ev.code, 0)

    ev1 = InputEvent(0, False, 0)

    if input_parse_string(ev1, string) < 0:
        return 0

    if ev1.code != ev.code:
        return 0
    elif ev1.mods != mods:
        return 1
    else:
        return 2
