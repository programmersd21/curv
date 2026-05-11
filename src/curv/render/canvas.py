"""Braille dot canvas for high-resolution curve rendering."""

from rich.text import Text

from curv.math import bresenham

__all__ = ["BrailleCanvas"]

# Unicode braille character base
BRAILLE_BASE = 0x2800

# Braille dot bit positions (standard Unicode braille numbering)
BRAILLE_DOT_MAP = {
    (0, 0): 1,  # column 0, row 0 → bit 1
    (1, 0): 8,  # column 1, row 0 → bit 8
    (0, 1): 2,  # column 0, row 1 → bit 2
    (1, 1): 16,  # column 1, row 1 → bit 16
    (0, 2): 4,  # column 0, row 2 → bit 4
    (1, 2): 32,  # column 1, row 2 → bit 32
    (0, 3): 64,  # column 0, row 3 → bit 64
    (1, 3): 128,  # column 1, row 3 → bit 128
}

# Formal, high-contrast colors
LAYER_COLORS = {
    "guide": "grey23",
    "curve": "bright_cyan",
    "handle": "bright_magenta",
}

LAYER_PRIORITY = {"handle": 3, "curve": 2, "guide": 1}


class BrailleCanvas:
    """High-resolution braille character canvas for rendering curves."""

    def __init__(self, cell_cols: int, cell_rows: int) -> None:
        """
        Initialize a braille canvas.
        """
        self.cell_cols = cell_cols
        self.cell_rows = cell_rows
        self.dot_width = cell_cols * 2
        self.dot_height = cell_rows * 4
        # Dictionary mapping (dot_x, dot_y) to layer name
        self.dots: dict[tuple[int, int], str] = {}

    def clear(self) -> None:
        """Clear all dots from the canvas."""
        self.dots.clear()

    def set_dot(self, dot_x: int, dot_y: int, layer: str) -> None:
        """
        Set a dot at the given position in the specified layer.
        """
        if (
            dot_x < 0
            or dot_x >= self.dot_width
            or dot_y < 0
            or dot_y >= self.dot_height
        ):
            return

        current = self.dots.get((dot_x, dot_y), "")
        new_priority = LAYER_PRIORITY.get(layer, 0)
        current_priority = LAYER_PRIORITY.get(current, 0)

        if new_priority >= current_priority:
            self.dots[(dot_x, dot_y)] = layer

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, layer: str) -> None:
        """
        Draw a line in the specified layer using Bresenham's algorithm.
        """
        points = bresenham.line(x0, y0, x1, y1)
        for x, y in points:
            self.set_dot(x, y, layer)

    def render(self) -> list[Text]:
        """
        Render the canvas as a list of Text objects.
        """
        rows: list[Text] = []

        for cell_row in range(self.cell_rows):
            row_text = Text()

            for cell_col in range(self.cell_cols):
                braille_value = 0
                dominant_layer = ""
                dominant_priority = 0

                for dot_row in range(4):
                    for dot_col in range(2):
                        dot_x = cell_col * 2 + dot_col
                        dot_y = cell_row * 4 + dot_row
                        layer = self.dots.get((dot_x, dot_y), "")

                        if layer:
                            bit = BRAILLE_DOT_MAP.get((dot_col, dot_row), 0)
                            braille_value |= bit
                            priority = LAYER_PRIORITY.get(layer, 0)
                            if priority > dominant_priority:
                                dominant_priority = priority
                                dominant_layer = layer

                if braille_value == 0:
                    row_text.append(" ")
                else:
                    braille_char = chr(BRAILLE_BASE + braille_value)
                    color = LAYER_COLORS.get(dominant_layer, "white")
                    row_text.append(braille_char, style=color)

            rows.append(row_text)

        return rows
