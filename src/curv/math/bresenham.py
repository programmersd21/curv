"""Bresenham's line algorithm for rasterization."""

__all__ = ["line"]


def line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """
    Bresenham's line algorithm.

    Returns every integer coordinate point along a line from (x0, y0) to (x1, y1)
    inclusive, handling all eight octants correctly.

    Args:
        x0: Starting x coordinate
        y0: Starting y coordinate
        x1: Ending x coordinate
        y1: Ending y coordinate

    Returns:
        List of (x, y) tuples representing all points on the line
    """
    points: list[tuple[int, int]] = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    # Handle the case where the line is more horizontal than vertical
    if dx > dy:
        err = dx / 2.0
        y = y0
        x = x0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        points.append((x1, y1))
    else:
        # The line is more vertical than horizontal
        err = dy / 2.0
        x = x0
        y = y0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        points.append((x1, y1))

    return points
