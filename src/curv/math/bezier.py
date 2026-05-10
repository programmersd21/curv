"""Pure mathematical functions for cubic bezier curve evaluation."""

__all__ = [
    "Vec2",
    "evaluate",
    "sample_curve",
    "css_string",
    "hypr_string",
    "get_y_at_x",
    "get_velocity_samples",
]

Vec2 = tuple[float, float]


def evaluate(t: float, p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2) -> Vec2:
    """
    Evaluate a cubic bezier curve at parameter t.
    """
    it = 1.0 - t
    it2 = it * it
    it3 = it2 * it
    t2 = t * t
    t3 = t2 * t

    x = it3 * p0[0] + 3 * it2 * t * p1[0] + 3 * it * t2 * p2[0] + t3 * p3[0]
    y = it3 * p0[1] + 3 * it2 * t * p1[1] + 3 * it * t2 * p2[1] + t3 * p3[1]
    return (x, y)


def sample_curve(p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2, n: int = 150) -> list[Vec2]:
    """
    Sample a cubic bezier curve at n evenly spaced points.
    """
    samples: list[Vec2] = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        samples.append(evaluate(t, p0, p1, p2, p3))
    return samples


def get_y_at_x(
    x: float, p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2, tolerance: float = 1e-6
) -> float:
    """
    Find the y value for a given x using binary search.
    Assumes x(t) is monotonic within [p0.x, p3.x].
    """
    # Clamp x to start/end points if outside range
    if x <= p0[0]:
        return p0[1]
    if x >= p3[0]:
        return p3[1]

    low = 0.0
    high = 1.0
    t = 0.5

    for _ in range(20):
        t = (low + high) / 2
        it = 1.0 - t
        xt = (
            it**3 * p0[0] + 3 * it**2 * t * p1[0] + 3 * it * t**2 * p2[0] + t**3 * p3[0]
        )

        if abs(xt - x) < tolerance:
            break
        if xt < x:
            low = t
        else:
            high = t

    it = 1.0 - t
    yt = it**3 * p0[1] + 3 * it**2 * t * p1[1] + 3 * it * t**2 * p2[1] + t**3 * p3[1]
    return yt


def get_velocity_samples(
    p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2, n: int = 50
) -> list[float]:
    """
    Sample the velocity (dy/dx) of the curve at n points.
    """
    samples = sample_curve(p0, p1, p2, p3, n=n + 1)
    velocities = []
    for i in range(len(samples) - 1):
        x0, y0 = samples[i]
        x1, y1 = samples[i + 1]
        dx = x1 - x0
        dy = y1 - y0
        velocities.append(dy / dx if dx != 0 else 0.0)
    return velocities


def css_string(p1: Vec2, p2: Vec2) -> str:
    return f"cubic-bezier({p1[0]:.3f}, {p1[1]:.3f}, {p2[0]:.3f}, {p2[1]:.3f})"


def hypr_string(p1: Vec2, p2: Vec2) -> str:
    return f"{p1[0]:.3f}, {p1[1]:.3f}, {p2[0]:.3f}, {p2[1]:.3f}"
