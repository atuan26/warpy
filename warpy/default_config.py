DEFAULT_CONFIG = {
    "hint_activation_key": {
        "val": "A-M-x",
        "description": "Activates hint mode.",
        "option_type": 3,
    },
    "hint2_activation_key": {
        "val": "A-M-X",
        "description": "Activate two pass hint mode.",
        "option_type": 3,
    },
    "grid_activation_key": {
        "val": "A-M-g",
        "description": "Activates grid mode and allows for further manipulation of the pointer using the mapped keys.",
        "option_type": 3,
    },
    "history_activation_key": {
        "val": "A-M-h",
        "description": "Activate history mode.",
        "option_type": 3,
    },
    "screen_activation_key": {
        "val": "A-M-s",
        "description": "Activate (s)creen selection mode.",
        "option_type": 3,
    },
    "activation_key": {
        "val": "A-M-c",
        "description": "Activate normal movement mode (manual (c)ursor movement).",
        "option_type": 3,
    },
    "hint_oneshot_key": {
        "val": "A-M-l",
        "description": "Activate hint mode and exit upon selection.",
        "option_type": 3,
    },
    "hint2_oneshot_key": {
        "val": "A-M-L",
        "description": "Activate two pass hint mode and exit upon selection.",
        "option_type": 3,
    },
    "exit": {
        "val": "esc",
        "description": "Exit the currently active warpd session.",
        "option_type": 3,
    },
    "drag": {
        "val": "v",
        "description": "Toggle drag mode (mnemonic (v)isual mode).",
        "option_type": 3,
    },
    "copy_and_exit": {
        "val": "c",
        "description": "Send the copy key and exit (useful in combination with v).",
        "option_type": 3,
    },
    "accelerator": {
        "val": "a",
        "description": "Increase the acceleration of the pointer while held.",
        "option_type": 3,
    },
    "decelerator": {
        "val": "d",
        "description": "Decrease the speed of the pointer while held.",
        "option_type": 3,
    },
    "buttons": {
        "val": "m , .",
        "description": "A space separated list of mouse buttons (2 is middle click).",
        "option_type": 4,
    },
    "drag_button": {
        "val": "1",
        "description": "The mouse buttton used for dragging.",
        "option_type": 2,
    },
    "oneshot_buttons": {
        "val": "n - /",
        "description": "Oneshot mouse buttons (deactivate on click).",
        "option_type": 4,
    },
    "print": {
        "val": "p",
        "description": "Print the current mouse coordinates to stdout (useful for scripts).",
        "option_type": 3,
    },
    "history": {
        "val": ";",
        "description": "Activate hint history mode while in normal mode.",
        "option_type": 3,
    },
    "hint": {
        "val": "x",
        "description": "Activate hint mode while in normal mode (mnemonic: x marks the spot?).",
        "option_type": 3,
    },
    "hint2": {
        "val": "X",
        "description": "Activate two pass hint mode.",
        "option_type": 3,
    },
    "grid": {
        "val": "g",
        "description": "Activate (g)rid mode while in normal mode.",
        "option_type": 3,
    },
    "screen": {
        "val": "s",
        "description": "Activate (s)creen selection while in normal mode.",
        "option_type": 3,
    },
    "left": {
        "val": "h",
        "description": "Move the cursor left in normal mode.",
        "option_type": 3,
    },
    "down": {
        "val": "j",
        "description": "Move the cursor down in normal mode.",
        "option_type": 3,
    },
    "up": {
        "val": "k",
        "description": "Move the cursor up in normal mode.",
        "option_type": 3,
    },
    "right": {
        "val": "l",
        "description": "Move the cursor right in normal mode.",
        "option_type": 3,
    },
    "top": {
        "val": "H",
        "description": "Moves the cursor to the top of the screen in normal mode.",
        "option_type": 3,
    },
    "middle": {
        "val": "M",
        "description": "Moves the cursor to the middle of the screen in normal mode.",
        "option_type": 3,
    },
    "bottom": {
        "val": "L",
        "description": "Moves the cursor to the bottom of the screen in normal mode.",
        "option_type": 3,
    },
    "start": {
        "val": "0",
        "description": "Moves the cursor to the leftmost corner of the screen in normal mode.",
        "option_type": 3,
    },
    "end": {
        "val": "$",
        "description": "Moves the cursor to the rightmost corner of the screen in normal mode.",
        "option_type": 3,
    },
    "scroll_down": {"val": "e", "description": "Scroll down key.", "option_type": 3},
    "scroll_up": {"val": "r", "description": "Scroll up key.", "option_type": 3},
    "cursor_color": {
        "val": "#FF4500",
        "description": "The color of the pointer in normal mode (rgba hex value).",
        "option_type": 1,
    },
    "cursor_size": {
        "val": "7",
        "description": "The height of the pointer in normal mode.",
        "option_type": 2,
    },
    "repeat_interval": {
        "val": "20",
        "description": "The number of milliseconds before repeating a movement event.",
        "option_type": 2,
    },
    "speed": {
        "val": "220",
        "description": "Pointer speed in pixels/second.",
        "option_type": 2,
    },
    "max_speed": {
        "val": "1600",
        "description": "The maximum pointer speed.",
        "option_type": 2,
    },
    "decelerator_speed": {
        "val": "50",
        "description": "Pointer speed while decelerator is depressed.",
        "option_type": 2,
    },
    "acceleration": {
        "val": "700",
        "description": "Pointer acceleration in pixels/second^2.",
        "option_type": 2,
    },
    "accelerator_acceleration": {
        "val": "2900",
        "description": "Pointer acceleration while the accelerator is depressed.",
        "option_type": 2,
    },
    "oneshot_timeout": {
        "val": "300",
        "description": "The length of time in milliseconds to wait for a second click after a oneshot key has been pressed.",
        "option_type": 2,
    },
    "hist_hint_size": {
        "val": "2",
        "description": "History hint size as a percentage of screen height.",
        "option_type": 2,
    },
    "grid_nr": {
        "val": "2",
        "description": "The number of rows in the grid.",
        "option_type": 2,
    },
    "grid_nc": {
        "val": "2",
        "description": "The number of columns in the grid.",
        "option_type": 2,
    },
    "hist_back": {
        "val": "C-o",
        "description": "Move to the last position in the history stack.",
        "option_type": 3,
    },
    "hist_forward": {
        "val": "C-i",
        "description": "Move to the next position in the history stack.",
        "option_type": 3,
    },
    "grid_up": {"val": "w", "description": "Move the grid up.", "option_type": 3},
    "grid_left": {"val": "a", "description": "Move the grid left.", "option_type": 3},
    "grid_down": {"val": "s", "description": "Move the grid down.", "option_type": 3},
    "grid_right": {"val": "d", "description": "Move the grid right.", "option_type": 3},
    "grid_cut_up": {"val": "W", "description": "Cut the grid up.", "option_type": 3},
    "grid_cut_left": {
        "val": "A",
        "description": "Cut the grid left.",
        "option_type": 3,
    },
    "grid_cut_down": {
        "val": "S",
        "description": "Cut the grid down.",
        "option_type": 3,
    },
    "grid_cut_right": {
        "val": "D",
        "description": "Cut the grid right.",
        "option_type": 3,
    },
    "grid_keys": {
        "val": "u i j k",
        "description": "A sequence of comma delimited keybindings which are ordered bookwise with respect to grid position.",
        "option_type": 3,
    },
    "grid_exit": {
        "val": "c",
        "description": "Exit grid mode and return to normal mode.",
        "option_type": 3,
    },
    "grid_size": {
        "val": "4",
        "description": "The thickness of grid lines in pixels.",
        "option_type": 2,
    },
    "grid_border_size": {
        "val": "0",
        "description": "The thickness of the grid border in pixels.",
        "option_type": 2,
    },
    "grid_color": {
        "val": "#1c1c1e",
        "description": "The color of the grid.",
        "option_type": 1,
    },
    "grid_border_color": {
        "val": "#ffffff",
        "description": "The color of the grid border.",
        "option_type": 1,
    },
    "hint_bgcolor": {
        "val": "#1c1c1e",
        "description": "The background hint color.",
        "option_type": 1,
    },
    "hint_fgcolor": {
        "val": "#a1aba7",
        "description": "The foreground hint color.",
        "option_type": 1,
    },
    "hint_chars": {
        "val": "abcdefghijklmnopqrstuvwxyz",
        "description": "The character set from which hints are generated. The total number of hints is the square of the size of this string. It may be desirable to increase this for larger screens or trim it to increase gaps between hints.",
        "option_type": 1,
    },
    "hint_font": {
        "val": "Arial",
        "description": "The font name used by hints. Note: This is platform specific, in X it corresponds to a valid xft font name, on macos it corresponds to a postscript name.",
        "option_type": 1,
    },
    "hint_size": {
        "val": "20",
        "description": "Hint size (range: 1-1000)",
        "option_type": 2,
    },
    "hint_border_radius": {
        "val": "3",
        "description": "Border radius.",
        "option_type": 2,
    },
    "hint_exit": {
        "val": "esc",
        "description": "The exit key used for hint mode.",
        "option_type": 3,
    },
    "hint_undo": {
        "val": "backspace",
        "description": "undo last selection step in one of the hint based modes.",
        "option_type": 3,
    },
    "hint_undo_all": {
        "val": "C-u",
        "description": "undo all selection steps in one of the hint based modes.",
        "option_type": 3,
    },
    "hint2_chars": {
        "val": "hjkl;asdfgqwertyuiopzxcvb",
        "description": "The character set used for the second hint selection, should consist of at least hint2_grid_size^2 characters.",
        "option_type": 1,
    },
    "hint2_size": {
        "val": "20",
        "description": "The size of hints in the secondary grid (range: 1-1000).",
        "option_type": 2,
    },
    "hint2_gap_size": {
        "val": "1",
        "description": "The spacing between hints in the secondary grid. (range: 1-1000)",
        "option_type": 2,
    },
    "hint2_grid_size": {
        "val": "3",
        "description": "The size of the secondary grid.",
        "option_type": 2,
    },
    "screen_chars": {
        "val": "jkl;asdfg",
        "description": "The characters used for screen selection.",
        "option_type": 1,
    },
    "scroll_speed": {
        "val": "300",
        "description": "Initial scroll speed in units/second (unit varies by platform).",
        "option_type": 2,
    },
    "scroll_max_speed": {
        "val": "9000",
        "description": "Maximum scroll speed.",
        "option_type": 2,
    },
    "scroll_acceleration": {
        "val": "1600",
        "description": "Scroll acceleration in units/second^2.",
        "option_type": 2,
    },
    "scroll_deceleration": {
        "val": "-3400",
        "description": "Scroll deceleration.",
        "option_type": 2,
    },
    "indicator": {
        "val": "none",
        "description": "Specifies an optional visual indicator to be displayed while normal mode is active, must be one of: topright, topleft, bottomright, bottomleft, none",
        "option_type": 1,
    },
    "indicator_color": {
        "val": "#00ff00",
        "description": "The color of the visual indicator color.",
        "option_type": 1,
    },
    "indicator_size": {
        "val": "12",
        "description": "The size of the visual indicator in pixels.",
        "option_type": 2,
    },
    "normal_system_cursor": {
        "val": "0",
        "description": "If set to non-zero, use the system cursor instead of warpd's internal one.",
        "option_type": 2,
    },
    "normal_blink_interval": {
        "val": "0",
        "description": "If set to non-zero, the blink interval of the normal mode cursor in miliseconds. If two values are supplied, the first corresponds to the time the cursor is visible, and the second corresponds to the amount of time it is invisible",
        "option_type": 1,
    },
}
