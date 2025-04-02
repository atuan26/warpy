import json
import re

#!/usr/bin/env python3
import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple

from warpd.input import input_eq, input_parse_string
from warpd.schemas import InputEvent


class OptionType(Enum):
    OPT_INT = 1
    OPT_STRING = 2
    OPT_KEY = 3
    OPT_BUTTON = 4


class ConfigEntry:
    def __init__(self, key: str, value: str, option_type: OptionType):
        self.key = key
        self.value = value
        self.type = option_type
        self.whitelisted = False

    def validate(self) -> bool:
        """Validate the config entry based on its type."""
        print(f'\x1b[36m🔍 self = \x1b[32m{self.__dict__}\x1b[0m')
        if self.type == OptionType.OPT_INT:
            if not re.match(r"^-?\d+$", self.value):
                print(f"ERROR: {self.value} must be a valid int", file=sys.stderr)
                return False

        elif self.type in (OptionType.OPT_BUTTON, OptionType.OPT_KEY):
            return self._validate_key_option()

        return True

    def _validate_key_option(self) -> bool:
        """Validate a key option string."""
        if self.value == "unbind":
            return True

        for tok in self.value.split():
            ev = InputEvent()
            if input_parse_string(ev, tok) is None:
                print(f"ERROR: {tok} is not a valid key name", file=sys.stderr)
                return False
        return True

    def matches_input(self, ev: InputEvent | None, config_key: str) -> Tuple[bool, int]:
        """Check if this entry matches the given input event."""
        if self.key == config_key and self.value == "unbind":
            return False, 0

        if not self.whitelisted or self.type not in (
            OptionType.OPT_KEY,
            OptionType.OPT_BUTTON,
        ):
            return False, 0

        idx, exact = self._key_index(ev)
        if idx > 0:
            if (
                self.type == OptionType.OPT_KEY and exact
            ) or self.type == OptionType.OPT_BUTTON:
                if self.key == config_key:
                    return True, idx

        return False, 0

    def _key_index(self, ev: InputEvent | None) -> Tuple[int, bool]:
        """Find the index of a key in the list."""
        idx = 1

        for tok in self.value.split():
            ret = input_eq(ev, tok)
            if ret:
                return idx, (ret == 2)
            idx += 1

        return 0, False

    def as_int(self) -> int:
        """Get the value as an integer."""
        return int(self.value)


class OptionDefinition:
    def __init__(self, key: str, val: str, description: str, option_type: OptionType):
        self.key = key
        self.val = val
        self.description = description
        self.type = option_type


class ConfigManager:
    def __init__(self, default_config_path: str = "warpd/default_config.json"):
        self.entries: Dict[str, ConfigEntry] = {}
        self.option_definitions: Dict[str, OptionDefinition] = {}
        self.default_config_path = default_config_path
        self._load_default_options()

    def _load_default_options(self) -> None:
        """Load default options from JSON file."""
        try:
            with open(self.default_config_path, "r") as f:
                default_options = json.load(f)

            for key, option_data in default_options.items():
                option_type = OptionType(option_data["option_type"])
                self.option_definitions[key] = OptionDefinition(
                    key=key,
                    val=option_data["val"],
                    description=option_data["description"],
                    option_type=option_type,
                )
        except FileNotFoundError:
            print(
                f"WARNING: Default config file {self.default_config_path} not found",
                file=sys.stderr,
            )
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in {self.default_config_path}", file=sys.stderr)
            sys.exit(-1)
        except KeyError as e:
            print(
                f"ERROR: Missing required key in {self.default_config_path}: {e}",
                file=sys.stderr,
            )
            sys.exit(-1)

    def get_option_type(self, key: str) -> Optional[OptionType]:
        """Get the type of an option by key."""
        if key in self.option_definitions:
            return self.option_definitions[key].type
        return None

    def get(self, key: str) -> str:
        """Get config value by key."""
        breakpoint()
        if key in self.entries:
            return self.entries[key].value

        print(f"FATAL: unrecognized config entry: {key}", file=sys.stderr)
        sys.exit(-1)

    def get_int(self, key: str) -> int:
        """Get config value as integer."""
        return self.entries[key].as_int()

    def add(self, key: str, value: str) -> bool:
        """Add a config entry."""
        option_type = self.get_option_type(key)
        if not option_type:
            return False

        entry = ConfigEntry(key, value, option_type)
        if not entry.validate():
            sys.exit(-1)

        self.entries[key] = entry
        return True

    def parse_config_file(self, path: str) -> None:
        """Parse a config file."""
        # Clear existing entries
        self.entries.clear()

        # Set defaults from option definitions
        for key, option in self.option_definitions.items():
            self.add(key, option.val)

        # Open and parse user config file
        if not path:
            return

        try:
            with open(path, "r") if path != "-" else sys.stdin as fh:
                for line in fh:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split(":", 1)
                    if len(parts) != 2:
                        continue

                    key = parts[0].strip()
                    value = parts[1].strip()

                    self.add(key, value)
        except FileNotFoundError:
            print(f"WARNING: Config file not found: {path}", file=sys.stderr)
            # Continue with defaults

    def whitelist_inputs(self, names: Optional[List[str]] = None) -> None:
        """Set whitelisted config entries."""
        for entry in self.entries.values():
            entry.whitelisted = False

            if entry.type not in (OptionType.OPT_KEY, OptionType.OPT_BUTTON):
                continue

            if names is None:
                entry.whitelisted = True
            elif entry.key in names:
                entry.whitelisted = True

    def match_input(self, ev: InputEvent | None, config_key: str) -> int:
        """Match input event against config keys."""
        for entry in self.entries.values():
            matches, idx = entry.matches_input(ev, config_key)
            if matches:
                return idx

        return 0

    def config_print_options(self):
        for key, option in self.option_definitions.items():
            print(f"{key}: {option.description} (default: {option.val})")


# Global instance for compatibility with original API
config_manager = ConfigManager()


# For backward compatibility with the original C API
def config_get(key: str) -> str:
    return config_manager.get(key)


def config_get_int(key: str) -> int:
    return config_manager.get_int(key)


def parse_config(path: str) -> None:
    config_manager.parse_config_file(path)


def config_input_whitelist(names: Optional[List[str]] = None, n: int = 0) -> None:
    if not names:
        config_manager.whitelist_inputs(None)
    else:
        config_manager.whitelist_inputs(names[:n])


def config_input_match(ev: InputEvent | None, config_key: str) -> int:
    return config_manager.match_input(ev, config_key)


def config_print_options():
    return config_manager.config_print_options()
