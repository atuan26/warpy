import os
import struct
import sys
from typing import List, Tuple


def get_data_path(file="history"):
    """Get path to data file, creating directories if needed."""
    if os.getenv("XDG_DATA_DIR"):
        path = os.path.join(os.getenv("XDG_DATA_DIR", ""), "warpd")
        os.makedirs(path, mode=0o700, exist_ok=True)
    else:
        path = os.path.join(os.getenv("HOME", ""), ".local")
        os.makedirs(path, mode=0o700, exist_ok=True)
        path = os.path.join(path, "share")
        os.makedirs(path, mode=0o700, exist_ok=True)
        path = os.path.join(path, "warpd")
        os.makedirs(path, mode=0o700, exist_ok=True)

    return os.path.join(path, file)


def get_config_path(file="config"):
    """Get path to config file, creating directories if needed."""
    if os.getenv("XDG_CONFIG_HOME"):
        path = os.path.join(os.getenv("XDG_CONFIG_HOME", ""), "warpd")
        os.makedirs(path, mode=0o700, exist_ok=True)
    else:
        path = os.path.join(os.getenv("HOME", ""), ".config")
        os.makedirs(path, mode=0o700, exist_ok=True)
        path = os.path.join(path, "warpd")
        os.makedirs(path, mode=0o700, exist_ok=True)

    return os.path.join(path, file)


MAX_HIST_ENTS = 100  # Assuming this value based on the C code


class HistfileEntry:
    """Represents a single history entry with x and y coordinates."""

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y


class Histfile:
    """Main class for handling history file operations."""

    def __init__(self):
        self.sz = 0
        self.ents: List[HistfileEntry] = [HistfileEntry() for _ in range(MAX_HIST_ENTS)]

    def read_hist(self, path: str) -> None:
        """Read history from file at the specified path."""
        try:
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    pass

            # Open for reading and writing
            with open(path, "rb") as f:
                # Read sz (integer)
                data = f.read(4)  # Assuming int is 4 bytes
                if data:
                    self.sz = struct.unpack("i", data)[0]

                    # Read entries
                    for i in range(min(self.sz, MAX_HIST_ENTS)):
                        entry_data = f.read(
                            8
                        )  # Assuming two ints (x, y) at 4 bytes each
                        if entry_data and len(entry_data) == 8:
                            x, y = struct.unpack("ii", entry_data)
                            self.ents[i] = HistfileEntry(x, y)
                        else:
                            break  # Not enough data
                else:
                    self.sz = 0  # Empty file

        except Exception as e:
            print(f"Error opening history file: {e}", file=sys.stderr)
            sys.exit(-1)

    def write_hist(self, path: str) -> None:
        """Write history to file at the specified path."""
        try:
            with open(path, "wb") as f:
                # Write sz
                f.write(struct.pack("i", self.sz))

                # Write entries
                for i in range(self.sz):
                    f.write(struct.pack("ii", self.ents[i].x, self.ents[i].y))

        except Exception as e:
            print(f"Error writing history file: {e}", file=sys.stderr)
            sys.exit(-1)

    def histfile_read(self) -> Tuple[List[HistfileEntry], int]:
        """Read history entries and return them along with count."""
        self.read_hist(get_data_path("history"))
        return self.ents, self.sz

    def histfile_add(self, x: int, y: int) -> None:
        """Add a new entry to the history file."""
        histpath = get_data_path("history")
        self.read_hist(histpath)

        # Filter out entries close to the new one
        n = 0
        for i in range(self.sz):
            if not ((abs(self.ents[i].x - x) < 30) and (abs(self.ents[i].y - y) < 30)):
                if n != i:  # Only copy if needed
                    self.ents[n] = self.ents[i]
                n += 1

        # Handle full history list
        if n == MAX_HIST_ENTS:
            # Move entries to make room
            self.ents = self.ents[1:] + [HistfileEntry()]
            n -= 1

        # Add new entry
        self.ents[n] = HistfileEntry(x, y)
        self.sz = n + 1

        # Write updated history
        self.write_hist(histpath)


# Global instance
_histfile = Histfile()


def histfile_read():
    """Return history entries and count."""
    entries, count = _histfile.histfile_read()
    return entries[:count], count


def histfile_add(x: int, y: int):
    """Add a new entry to the history file."""
    _histfile.histfile_add(x, y)
