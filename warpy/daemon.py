from warpy.config import config_input_whitelist, parse_config
from warpy.hint import init_hints
from warpy.mode_loop import mode_loop
from warpy.mouse import init_mouse
from warpy.schemas import Platform

activation_keys = {
    "activation_key",
    "hint_activation_key",
    "grid_activation_key",
    "hint_oneshot_key",
    "screen_activation_key",
    "hint2_activation_key",
    "hint2_oneshot_key",
    "history_activation_key",
}


def reload_config(config_path):
    parse_config(config_path)
    init_hints()
    init_mouse()
    # TODO
    #  	for (i = 0; i < sizeof activation_keys / sizeof activation_keys[0]; i++)
    # input_parse_string(&activation_events[i], config_get(activation_keys[i]));


def daemon_loop(platform: Platform, config_path=None):
    platform.monitor_file(config_path)

    reload_config(config_path)

    while 1:
        mode = 0
        ev = platform.input_wait()

        if not ev:
            reload_config(config_path)
            continue

        config_input_whitelist(list(activation_keys), len(activation_keys))

        # ... TODO

        mode_loop(platform, mode, 0, 1)
