from ctypes import c_int
import sys
import time

from warpy import platform

SCROLL_DOWN = 1
SCROLL_RIGHT = 2
SCROLL_LEFT = 3
SCROLL_UP = 4


class ScrollManager:
    """Manages scrolling behavior with physics-based acceleration and deceleration."""

    def __init__(self, platform):
        """
        Initialize the scroll manager.

        Args:
            platform: Platform object with scroll method
        """
        self.platform = platform

        # Determine factor based on platform
        self.factor = 1 if sys.platform == "darwin" else 50

        # Load configuration
        self.vt = self._get_config_float("scroll_max_speed")  # terminal velocity
        self.v0 = self._get_config_float("scroll_speed")  # initial velocity
        self.da0 = self._get_config_float("scroll_deceleration")  # deceleration
        self.a0 = self._get_config_float("scroll_acceleration")  # acceleration
        self.fling_velocity = 2000.0 / self.factor

        # State variables
        self.last_tick = 0
        self.v = 0.0  # velocity in scroll units per second
        self.a = 0.0  # acceleration
        self.d = 0.0  # total distance
        self.direction = 0  # scroll direction
        self.traveled = 0  # scroll units emitted

    def _get_config_float(self, key: str) -> float:
        """Get configuration value as float adjusted by factor."""
        # This would be replaced with actual config mechanism
        config_values = {
            "scroll_max_speed": 1000,
            "scroll_speed": 100,
            "scroll_deceleration": -500,
            "scroll_acceleration": 500,
        }
        return float(config_values.get(key, 0)) / self.factor

    def _get_time_ms(self) -> int:
        """Get current time in milliseconds."""
        return int(time.time() * 1000)

    def tick(self) -> None:
        """Process scroll physics and emit scroll events."""
        current_time = self._get_time_ms()

        # First tick initialization
        if self.last_tick == 0:
            self.last_tick = current_time
            return

        # Time elapsed since last tick in milliseconds
        t = float(current_time - self.last_tick)
        self.last_tick = current_time

        # Time in seconds for physics calculations
        t_sec = t / 1000.0

        # Update distance and velocity
        self.d += self.v * t_sec + 0.5 * self.a * t_sec * t_sec
        self.v += self.a * t_sec

        # Handle minimum velocity threshold
        if self.v < 0:
            self.v = 0
            self.d = 0
            self.traveled = 0

        # Handle maximum velocity threshold
        if self.v >= self.vt:
            self.v = self.vt
            self.a = 0

        # Emit scroll events for the distance traveled since last tick
        scroll_units = int(self.d) - self.traveled
        for _ in range(scroll_units):
            self.platform.scroll(c_int(self.direction))

        self.traveled = int(self.d)

    def stop(self) -> None:
        """Stop scrolling completely."""
        self.v = 0
        self.a = 0
        self.traveled = 0
        self.d = 0

    def decelerate(self) -> None:
        """Begin decelerating the scroll."""
        self.a = self.da0

    def accelerate(self, direction: int) -> None:
        """
        Begin accelerating the scroll in the specified direction.

        Args:
            direction: Direction to scroll (positive or negative)
        """
        self.direction = direction
        self.a = self.a0

        if self.v == 0:
            self.d = 0
            self.traveled = 0
            self.v = self.v0

    def impart_impulse(self) -> None:
        """Add a sudden boost to velocity (like a 'fling')."""
        self.v += self.fling_velocity


_scroll_manager = ScrollManager(platform)


# Original API functions as thin wrappers
def scroll_tick() -> None:
    """Process scroll physics and emit scroll events."""
    _scroll_manager.tick()


def scroll_stop() -> None:
    """Stop scrolling completely."""
    _scroll_manager.stop()


def scroll_decelerate() -> None:
    """Begin decelerating the scroll."""
    _scroll_manager.decelerate()


def scroll_accelerate(direction: int) -> None:
    """
    Begin accelerating the scroll in the specified direction.

    Args:
        direction: Direction to scroll (positive or negative)
    """
    _scroll_manager.accelerate(direction)


def scroll_impart_impulse() -> None:
    """Add a sudden boost to velocity (like a 'fling')."""
    _scroll_manager.impart_impulse()
