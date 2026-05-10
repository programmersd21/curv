"""Tests for the braille canvas."""

from rich.text import Text

from curv.render.canvas import BrailleCanvas


class TestBrailleCanvas:
    """Tests for the BrailleCanvas class."""

    def test_canvas_initialization(self) -> None:
        """Test that a canvas can be created."""
        canvas = BrailleCanvas(10, 5)
        assert canvas.cell_cols == 10
        assert canvas.cell_rows == 5
        assert canvas.dot_width == 20
        assert canvas.dot_height == 20

    def test_canvas_renders_without_error(self) -> None:
        """Test that a fresh canvas renders without raising."""
        canvas = BrailleCanvas(10, 5)
        result = canvas.render()
        assert isinstance(result, list)
        assert len(result) == 5
        for row in result:
            assert isinstance(row, Text)

    def test_canvas_render_size(self) -> None:
        """Test that render returns correct number of rows."""
        canvas = BrailleCanvas(15, 8)
        result = canvas.render()
        assert len(result) == 8

    def test_canvas_clear(self) -> None:
        """Test that clear resets all dots."""
        canvas = BrailleCanvas(10, 5)
        canvas.set_dot(5, 5, "curve")
        assert (5, 5) in canvas.dots
        canvas.clear()
        assert len(canvas.dots) == 0

    def test_set_dot_in_bounds(self) -> None:
        """Test that set_dot works for in-bounds coordinates."""
        canvas = BrailleCanvas(10, 5)
        canvas.set_dot(5, 5, "curve")
        assert (5, 5) in canvas.dots
        assert canvas.dots[(5, 5)] == "curve"

    def test_set_dot_out_of_bounds_negative(self) -> None:
        """Test that set_dot with negative coordinates does not raise."""
        canvas = BrailleCanvas(10, 5)
        canvas.set_dot(-1, 5, "curve")
        assert (-1, 5) not in canvas.dots

    def test_set_dot_out_of_bounds_excessive(self) -> None:
        """Test that set_dot with excessive coordinates does not raise."""
        canvas = BrailleCanvas(10, 5)
        canvas.set_dot(100, 100, "curve")
        assert (100, 100) not in canvas.dots

    def test_set_dot_with_layer_priority(self) -> None:
        """Test that layer priority is respected."""
        canvas = BrailleCanvas(10, 5)
        # Set guide layer first
        canvas.set_dot(5, 5, "guide")
        assert canvas.dots[(5, 5)] == "guide"
        # Set curve layer (higher priority)
        canvas.set_dot(5, 5, "curve")
        assert canvas.dots[(5, 5)] == "curve"
        # Set guide layer again (lower priority, should not override)
        canvas.set_dot(5, 5, "guide")
        assert canvas.dots[(5, 5)] == "curve"

    def test_draw_line_horizontal(self) -> None:
        """Test drawing a horizontal line."""
        canvas = BrailleCanvas(10, 5)
        canvas.draw_line(0, 5, 10, 5, "curve")
        # Check that dots were set along the line
        assert len(canvas.dots) > 0

    def test_draw_line_vertical(self) -> None:
        """Test drawing a vertical line."""
        canvas = BrailleCanvas(10, 5)
        canvas.draw_line(5, 0, 5, 10, "curve")
        assert len(canvas.dots) > 0

    def test_draw_line_diagonal(self) -> None:
        """Test drawing a diagonal line."""
        canvas = BrailleCanvas(10, 10)
        canvas.draw_line(0, 0, 10, 10, "curve")
        assert len(canvas.dots) > 0

    def test_render_returns_text_objects(self) -> None:
        """Test that render returns Text objects."""
        canvas = BrailleCanvas(5, 3)
        result = canvas.render()
        for row in result:
            assert isinstance(row, Text)

    def test_render_non_empty_content(self) -> None:
        """Test that render produces non-empty content."""
        canvas = BrailleCanvas(5, 3)
        canvas.set_dot(2, 2, "curve")
        result = canvas.render()
        # At least one row should be non-empty
        has_content = False
        for row in result:
            if len(row) > 0:
                has_content = True
        assert has_content

    def test_canvas_with_different_sizes(self) -> None:
        """Test canvas with various sizes."""
        sizes = [(1, 1), (5, 5), (20, 10), (100, 50)]
        for cols, rows in sizes:
            canvas = BrailleCanvas(cols, rows)
            result = canvas.render()
            assert len(result) == rows

    def test_set_dot_layer_overwrite(self) -> None:
        """Test that set_dot can update layer at same position."""
        canvas = BrailleCanvas(10, 5)
        canvas.set_dot(5, 5, "guide")
        canvas.set_dot(5, 5, "handle")
        # Handle has higher priority
        assert canvas.dots[(5, 5)] == "handle"
