"""Tests for Bresenham's line algorithm."""

from curv.math.bresenham import line


class TestLine:
    """Tests for the line function."""

    def test_line_horizontal(self) -> None:
        """Test a horizontal line."""
        points = line(0, 0, 5, 0)
        assert len(points) == 6
        assert points[0] == (0, 0)
        assert points[-1] == (5, 0)
        # All points should have the same y coordinate
        for x, y in points:
            assert y == 0

    def test_line_vertical(self) -> None:
        """Test a vertical line."""
        points = line(0, 0, 0, 5)
        assert len(points) == 6
        assert points[0] == (0, 0)
        assert points[-1] == (0, 5)
        # All points should have the same x coordinate
        for x, y in points:
            assert x == 0

    def test_line_diagonal_45_degrees(self) -> None:
        """Test a 45-degree diagonal line."""
        points = line(0, 0, 5, 5)
        assert len(points) == 6
        assert points[0] == (0, 0)
        assert points[-1] == (5, 5)

    def test_line_reverse_direction(self) -> None:
        """Test a line going in reverse direction."""
        points = line(5, 5, 0, 0)
        assert len(points) == 6
        assert points[0] == (5, 5)
        assert points[-1] == (0, 0)

    def test_line_zero_length(self) -> None:
        """Test a zero-length line (single point)."""
        points = line(3, 3, 3, 3)
        assert len(points) == 1
        assert points[0] == (3, 3)

    def test_line_octant_0_45(self) -> None:
        """Test line in octant 0-45 degrees (east-northeast)."""
        points = line(0, 0, 8, 4)
        assert points[0] == (0, 0)
        assert points[-1] == (8, 4)
        # Verify continuity
        for i in range(len(points) - 1):
            dx = abs(points[i + 1][0] - points[i][0])
            dy = abs(points[i + 1][1] - points[i][1])
            assert dx + dy >= 1  # At least one step in some direction

    def test_line_octant_45_90(self) -> None:
        """Test line in octant 45-90 degrees (north-northeast)."""
        points = line(0, 0, 4, 8)
        assert points[0] == (0, 0)
        assert points[-1] == (4, 8)

    def test_line_octant_90_135(self) -> None:
        """Test line in octant 90-135 degrees (north-northwest)."""
        points = line(8, 0, 0, 8)
        assert points[0] == (8, 0)
        assert points[-1] == (0, 8)

    def test_line_octant_135_180(self) -> None:
        """Test line in octant 135-180 degrees (west-northwest)."""
        points = line(8, 4, 0, 0)
        assert points[0] == (8, 4)
        assert points[-1] == (0, 0)

    def test_line_octant_180_225(self) -> None:
        """Test line in octant 180-225 degrees (west-southwest)."""
        points = line(8, 4, 0, 8)
        assert points[0] == (8, 4)
        assert points[-1] == (0, 8)

    def test_line_octant_225_270(self) -> None:
        """Test line in octant 225-270 degrees (south-southwest)."""
        points = line(8, 8, 0, 0)
        assert points[0] == (8, 8)
        assert points[-1] == (0, 0)

    def test_line_octant_270_315(self) -> None:
        """Test line in octant 270-315 degrees (south-southeast)."""
        points = line(0, 8, 8, 0)
        assert points[0] == (0, 8)
        assert points[-1] == (8, 0)

    def test_line_octant_315_360(self) -> None:
        """Test line in octant 315-360 degrees (east-southeast)."""
        points = line(0, 4, 8, 0)
        assert points[0] == (0, 4)
        assert points[-1] == (8, 0)

    def test_line_continuity(self) -> None:
        """Test that consecutive points are one step apart."""
        points = line(0, 0, 10, 7)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            # Each step should move exactly 1 in at least one direction
            assert 1 <= dx + dy <= 2

    def test_line_endpoints_included(self) -> None:
        """Test that both endpoints are included."""
        start = (2, 3)
        end = (10, 8)
        points = line(start[0], start[1], end[0], end[1])
        assert points[0] == start
        assert points[-1] == end
