"""Application state management for curv."""

from dataclasses import dataclass, field
from typing import Literal

__all__ = [
    "Point",
    "BezierState",
    "X_BOUNDS",
    "Y_BOUNDS",
    "default_state",
]


@dataclass(frozen=True)
class Point:
    """Immutable 2D point with clamping and movement operations."""

    x: float
    y: float

    def clamp(
        self, x_range: tuple[float, float], y_range: tuple[float, float]
    ) -> "Point":
        """Return a new Point with coordinates clamped to the given ranges."""
        x_min, x_max = x_range
        y_min, y_max = y_range
        clamped_x = max(x_min, min(x_max, self.x))
        clamped_y = max(y_min, min(y_max, self.y))
        return Point(clamped_x, clamped_y)

    def moved(self, dx: float, dy: float) -> "Point":
        """Return a new Point with the given deltas applied."""
        return Point(self.x + dx, self.y + dy)


@dataclass(frozen=True)
class BezierState:
    """Immutable application state."""

    p0: Point
    p1: Point
    p2: Point
    p3: Point
    selected: Literal["p0", "p1", "p2", "p3"]
    preset_name: str
    flash_message: str
    flash_until: float
    show_help: bool
    show_animation: bool

    # New fields for Elite features
    show_preset_browser: bool = False
    preset_query: str = ""
    preset_search_results: list[str] = field(default_factory=list)
    preset_search_index: int = 0

    # DNA / Mutation
    intensity: float = 1.0
    mutation_type: Literal["none", "sharp", "soft", "extreme"] = "none"

    @property
    def dna_p1(self) -> Point:
        """Apply DNA intensity mutation to p1 relative to center (0.5, 0.5)."""
        if self.intensity == 1.0:
            return self.p1
        return Point(
            0.5 + (self.p1.x - 0.5) * self.intensity,
            0.5 + (self.p1.y - 0.5) * self.intensity,
        ).clamp(X_BOUNDS, Y_BOUNDS)

    @property
    def dna_p2(self) -> Point:
        """Apply DNA intensity mutation to p2 relative to center (0.5, 0.5)."""
        if self.intensity == 1.0:
            return self.p2
        return Point(
            0.5 + (self.p2.x - 0.5) * self.intensity,
            0.5 + (self.p2.y - 0.5) * self.intensity,
        ).clamp(X_BOUNDS, Y_BOUNDS)

    # Engagement features
    history: list[tuple[Point, Point]] = field(default_factory=list)
    tip_index: int = 0


# Movement clamp boundaries for editable control points
X_BOUNDS: tuple[float, float] = (0.0, 1.0)
Y_BOUNDS: tuple[float, float] = (-0.5, 1.5)


def default_state() -> BezierState:
    """Create the default application state."""
    return BezierState(
        p0=Point(0.0, 0.0),
        p1=Point(0.42, 0.0),
        p2=Point(0.58, 1.0),
        p3=Point(1.0, 1.0),
        selected="p1",
        preset_name="custom",
        flash_message="",
        flash_until=0.0,
        show_help=False,
        show_animation=True,
    )
