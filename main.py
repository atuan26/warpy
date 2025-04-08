# Compile shared object
"""
gcc -shared -o src/linux_X.so -fPIC \
src/config.c src/daemon.c src/grid.c src/grid_drw.c src/hint.c \
src/histfile.c src/history.c src/input.c src/mode-loop.c \
src/mouse.c src/normal.c src/screen.c src/scroll.c src/warpd.c \
src/platform/linux/linux.c \
src/platform/linux/X/X.c src/platform/linux/X/input.c src/platform/linux/X/hint.c \
src/platform/linux/X/mouse.c src/platform/linux/X/screen.c \
-I/usr/include/freetype2 -I/usr/include/X11/extensions \
-lm -lX11 -lXft -lXrender -lXinerama -lXi -lXtst -lXfixes
"""

import argparse
import fcntl
import logging
import os
import sys

from warpy import lib, schemas
from warpy.config import config_get_int, config_print_options, parse_config
from warpy.daemon import daemon_loop
from warpy.hint import init_hints
from warpy.histfile import get_config_path
from warpy.mode_loop import mode_loop
from warpy.mouse import init_mouse
from warpy.platform import platform_run

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def lock():
    """Create lock file to prevent multiple instances."""
    path = f"/tmp/warpd_{os.getuid()}.lock"
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CREAT, 0o600)
        try:
            # LOCK_EX | LOCK_NB in Python
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(
                "ERROR: Another instance of warpd is already running.", file=sys.stderr
            )
            sys.exit(-1)
    except OSError as e:
        print(f"flock open: {e}", file=sys.stderr)
        sys.exit(-1)


def daemonize():
    """Daemonize the process by double forking."""
    if os.fork():
        os._exit(0)
    if os.fork():
        os._exit(0)

    # Redirect stdout and stderr to /dev/null
    with open("/dev/null", "w") as devnull:
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())


def print_usage():
    print(
        "warpd: [options]\n\n"
        "  -f, --foreground            Run warpd in the foreground (useful for debugging).\n"
        "  -h, --help                  Print this help message.\n"
        "  -v, --version               Print the version and exit.\n"
        "  -c, --config <config file>  Use the supplied config file.\n"
        "  -l, --list-keys             Print all valid keys.\n"
        "  --list-options              Print all available config options.\n"
        "  --hint                      Start warpd in hint mode and exit after the end of the session.\n"
        "  --hint2                     Start warpd in two pass hint mode and exit after the end of the session.\n"
        "  --normal                    Start warpd in normal mode and exit after the end of the session.\n"
        "  --grid                      Start warpd in hint grid and exit after the end of the session.\n"
        "  --screen                    Start warpd in screen selection mode and exit after the end of the session.\n"
        "  --oneshot                   When paired with one of the mode flags, exit warpd as soon as the mode is complete (i.e don't drop into normal mode). Principally useful for scripting.\n"
        "  --move '<x> <y>'            Move the pointer to the specified coordinates.\n"
        "  --click <button>            Send a mouse click corresponding to the supplied button and exit. May be paired with --move.\n"
        "  -q, --query                 Consumes a list of hints from stdin and presents a one off hint selection.\n"
        "  --record                    When used with --click, records the event in warpd's hint history.\n\n"
    )


def print_version(): ...
def print_keys_main(platform):
    for i in range(256):
        name = platform.input_lookup_name(i, 0)

        if name and name[0]:
            print(name.decode())

        name = platform.input_lookup_name(i, 1)
        if name and name[0]:
            print(name.decode())
    return 0


def daemon_main(platform: schemas.Platform):
    parse_config(CONFIG_PATH)
    init_mouse()
    init_hints()

    daemon_loop(platform, CONFIG_PATH)


drag_flag = 0
oneshot_flag = 0
click_flag = 0
x_flag = -1
y_flag = -1
record_flag = 0
mode = 0

CONFIG_PATH = get_config_path()


def oneshot_main(platform: schemas.Platform):
    ret = 0

    scr = lib.get_screen(0)  # TODO
    parse_config(CONFIG_PATH)
    init_mouse()
    init_hints()

    platform.mouse_get_position(scr, None, None)
    if x_flag == -1 and y_flag == -1:
        if drag_flag:
            platform.mouse_down(config_get_int("drag_button"))

        ret = mode_loop(scr, platform, mode, oneshot_flag, record_flag)

        if drag_flag:
            platform.mouse_up(config_get_int("drag_button"))
    else:
        platform.mouse_move(scr, x_flag, y_flag)

    if click_flag:
        platform.mouse_click(click_flag)

    return ret


def main():
    foreground = 0
    config_path = get_config_path("config")

    global drag_flag, oneshot_flag, click_flag, x_flag, y_flag, record_flag, mode
    parser = argparse.ArgumentParser(
        description="Command-line options parser", add_help=False
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Print version and exit"
    )
    parser.add_argument("-h", "--help", action="store_true", help="Print help and exit")
    parser.add_argument("-q", "--query", action="store_true", help="Query mode")
    parser.add_argument("-l", "--list-keys", action="store_true", help="List keys")
    parser.add_argument(
        "-f", "--foreground", action="store_true", help="Run in foreground"
    )
    parser.add_argument("-c", "--config", type=str, help="Specify config file")

    # Additional long options without short versions
    parser.add_argument("--hint", action="store_true", help="Enable hint mode")
    parser.add_argument("--grid", action="store_true", help="Enable grid mode")
    parser.add_argument("--normal", action="store_true", help="Enable normal mode")
    parser.add_argument("--hint2", action="store_true", help="Enable hint2 mode")
    parser.add_argument("--history", action="store_true", help="Enable history mode")
    parser.add_argument("--list-options", action="store_true", help="List options")
    parser.add_argument("--oneshot", action="store_true", help="Enable oneshot mode")
    parser.add_argument("--click", type=str, help="Click action")
    parser.add_argument("--move", type=str, help="Move action")
    parser.add_argument("--record", action="store_true", help="Record mode")
    parser.add_argument("--drag", action="store_true", help="Drag mode")
    parser.add_argument("--screen", action="store_true", help="Screen mode")

    args = parser.parse_args()
    # Handle arguments
    if args.version:
        print_version()
        exit(0)

    if args.help:
        print_usage()
        exit(0)

    if args.list_keys:
        platform_run(print_keys_main)
        exit(0)

    if args.config:
        config_path = args.config
        _ = config_path

    if args.foreground:
        foreground = True

    if args.query:
        mode = schemas.MODE_HINTSPEC
        oneshot_flag = True

    if args.hint:
        mode = schemas.MODE_HINT

    if args.grid:
        mode = schemas.MODE_GRID

    if args.normal:
        mode = schemas.MODE_NORMAL

    if args.hint2:
        mode = schemas.MODE_HINT2

    if args.history:
        mode = schemas.MODE_HISTORY

    if args.screen:
        mode = schemas.MODE_SCREEN_SELECTION

    if args.oneshot:
        if mode is None:
            mode = schemas.MODE_NORMAL
        oneshot_flag = True

    if args.click is not None:
        click_flag = args.click
        oneshot_flag = True

    if args.move:
        x_flag, y_flag = args.move
        oneshot_flag = True

    if args.record:
        record_flag = True

    if args.drag:
        drag_flag = True

    if args.list_options:
        config_print_options()
        exit(0)

    if mode or oneshot_flag:
        platform_run(oneshot_main)
    else:
        lock()

        if not foreground:
            daemonize()
        # setvbuf(stdout, NULL, _IOLBF, 0);
        platform_run(daemon_main)


if __name__ == "__main__":
    main()
