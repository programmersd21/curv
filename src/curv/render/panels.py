"""Panel rendering for the UI."""

from time import monotonic

from rich.box import ROUNDED
from rich.panel import Panel
from rich.text import Text

from curv.math.bezier import css_string, get_velocity_samples, get_y_at_x, hypr_string
from curv.presets import get_preset_data
from curv.state import BezierState

__all__ = [
    "build_control_panel",
    "build_preview_panel",
    "build_animation_preview",
    "build_status_bar",
    "build_velocity_panel",
    "build_tips_panel",
    "build_export_cards",
    "build_history_panel",
    "build_stats_panel",
    "build_preset_browser",
    "build_spectrum_panel",
    "build_coordinate_matrix",
    "build_shortcuts_panel",
    "build_physics_panel",
]

# Style constants - formal minimalist
ACCENT = "bright_cyan"
SECONDARY = "bright_magenta"
HIGHLIGHT = "bright_yellow"
MUTED = "grey50"
VALUE_FG = "bright_white"
LABEL_FG = "grey70"
DIM = "grey30"
SUCCESS = "bright_green"
WARNING = "bright_yellow"
ERROR = "bright_red"


def build_velocity_panel(state: BezierState, width: int, height: int) -> Panel:
    """
    Build a panel showing the velocity (dy/dx) graph.
    """
    from curv.render.canvas import BrailleCanvas

    canvas_cols = max(1, width - 4)
    canvas_rows = max(1, height - 3)
    canvas = BrailleCanvas(canvas_cols, canvas_rows)

    p0 = (state.p0.x, state.p0.y)
    p1 = (state.dna_p1.x, state.dna_p1.y)
    p2 = (state.dna_p2.x, state.dna_p2.y)
    p3 = (state.p3.x, state.p3.y)

    velocities = get_velocity_samples(p0, p1, p2, p3, n=canvas.dot_width)
    max_v = max(max(velocities) if velocities else 1.0, 1.0)

    for x, v in enumerate(velocities):
        y = int((v / max_v) * (canvas.dot_height - 1))
        y = max(0, min(canvas.dot_height - 1, (canvas.dot_height - 1) - y))
        canvas.set_dot(x, y, "curve")

    content = Text("\n").join(canvas.render())
    return Panel(
        content,
        title="velocity",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_tips_panel(state: BezierState) -> Panel:
    """
    Build a panel with motion design principles.
    """
    tips = [
        "ease-out is appropriate for entrance animations.",
        "anticipatory curves enhance physical realism.",
        "maintain duration between 200ms and 500ms.",
        "the velocity graph indicates animation momentum.",
        "values exceeding 1.0 signify overshoot.",
    ]
    tip = tips[state.tip_index % len(tips)]
    content = Text(f" {tip}", style=LABEL_FG, justify="left")
    return Panel(
        content,
        title="principles",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_export_cards(state: BezierState) -> Panel:
    """
    Build export configurations.
    """
    p1 = (state.dna_p1.x, state.dna_p1.y)
    p2 = (state.dna_p2.x, state.dna_p2.y)

    css = css_string(p1, p2).lower()
    hypr = hypr_string(p1, p2).lower()
    swift = f"anim.curve({p1[0]:.2f}, {p1[1]:.2f}, {p2[0]:.2f}, {p2[1]:.2f})"

    lines = [
        f"[bold {ACCENT}]web[/]  [grey35]{css}[/]",
        f"[bold {SECONDARY}]hyp[/]  [grey35]{hypr}[/]",
        f"[bold {HIGHLIGHT}]swi[/]  [grey35]{swift[:20]}..[/]",
    ]

    content = Text.from_markup("\n".join(lines))
    return Panel(
        content,
        title="exports",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_control_panel(state: BezierState, height: int) -> Panel:
    """
    Minimalist control panel.
    """
    lines: list[str] = [f"[bold {ACCENT}]curv[/]", f"[{DIM}]─────────────[/]", ""]

    def format_point(name: str, x: float, y: float, is_selected: bool) -> str:
        color = SECONDARY if is_selected else ACCENT
        prefix = ">" if is_selected else " "
        return f"{prefix} [bold]{name.lower()}:[/] [{color}]{x:5.3f}, {y:5.3f}[/]"

    lines.append(format_point("p0", state.p0.x, state.p0.y, state.selected == "p0"))
    lines.append(format_point("p1", state.p1.x, state.p1.y, state.selected == "p1"))
    lines.append(format_point("p2", state.p2.x, state.p2.y, state.selected == "p2"))
    lines.append(format_point("p3", state.p3.x, state.p3.y, state.selected == "p3"))
    lines.append("")
    lines.append(f"[{DIM}]dna:[/] [bold {HIGHLIGHT}]{state.intensity:.1f}x[/]")
    lines.append(f"[{DIM}]pre:[/] [italic {ACCENT}]{state.preset_name.lower()}[/]")

    content = Text.from_markup("\n".join(lines))
    return Panel(content, box=ROUNDED, border_style=DIM, expand=True)


def build_preview_panel(state: BezierState, width: int, height: int) -> Panel:
    """
    Minimal high-contrast visualizer.
    """
    from curv.render.canvas import BrailleCanvas

    # Account for panel border (2), padding left+right (2), and a small safety margin
    canvas_cols = int(max(1, width - 6))
    # Account for panel border (2), padding top+bottom (2), title (1)
    canvas_rows = int(max(1, height - 5))

    canvas = BrailleCanvas(canvas_cols, canvas_rows)

    # Background dot grid
    for x in range(0, canvas.dot_width, 10):
        for y in range(0, canvas.dot_height, 5):
            canvas.set_dot(x, y, "guide")

    p0 = (state.p0.x, state.p0.y)
    p1 = (state.dna_p1.x, state.dna_p1.y)
    p2 = (state.dna_p2.x, state.dna_p2.y)
    p3 = (state.p3.x, state.p3.y)

    # View range with margin so edges don't sit on pixel row 0
    view_min = -0.1
    view_max = 1.1
    view_span = view_max - view_min

    # Render curve column-by-column for gap-free coverage
    prev_dot: tuple[int, int] | None = None
    for x_dot in range(canvas.dot_width):
        # Map dot column back to normalised x
        x_norm = view_min + (x_dot / (canvas.dot_width - 1)) * view_span
        if x_norm < p0[0] or x_norm > p3[0]:
            prev_dot = None
            continue
        y_norm = get_y_at_x(x_norm, p0, p1, p2, p3)
        y_dot = round((view_max - y_norm) / view_span * (canvas.dot_height - 1))
        if 0 <= y_dot < canvas.dot_height:
            canvas.set_dot(x_dot, y_dot, "curve")
            if prev_dot is not None:
                canvas.draw_line(prev_dot[0], prev_dot[1], x_dot, y_dot, "curve")
            prev_dot = (x_dot, y_dot)
        else:
            prev_dot = None

    # Draw control-point handles as small crosshairs (reflecting DNA mutation)
    for pt in [state.p0, state.dna_p1, state.dna_p2, state.p3]:
        hx = round((pt.x - view_min) / view_span * (canvas.dot_width - 1))
        hy = round((view_max - pt.y) / view_span * (canvas.dot_height - 1))
        hx = max(0, min(canvas.dot_width - 1, hx))
        hy = max(0, min(canvas.dot_height - 1, hy))
        canvas.set_dot(hx, hy, "handle")
        canvas.set_dot(hx, hy - 1, "handle")
        canvas.set_dot(hx - 1, hy, "handle")
        canvas.set_dot(hx + 1, hy, "handle")
        canvas.set_dot(hx, hy + 1, "handle")

    content = Text("\n").join(canvas.render())
    return Panel(
        content,
        title="visualizer",
        border_style=DIM,
        box=ROUNDED,
        padding=(1, 1),
        expand=True,
    )


def build_animation_preview(state: BezierState) -> Panel:
    """
    Minimalist animation demo.
    """
    if not state.show_animation:
        return Panel(
            Text.from_markup(f"[{DIM}]inactive[/]"),
            title="demo",
            border_style=DIM,
            box=ROUNDED,
            expand=True,
        )

    cycle_time = 2.0
    duration = 1.5
    current_time = monotonic() % cycle_time
    x = min(1.0, current_time / duration)
    p0 = (state.p0.x, state.p0.y)
    p1 = (state.dna_p1.x, state.dna_p1.y)
    p2 = (state.dna_p2.x, state.dna_p2.y)
    p3 = (state.p3.x, state.p3.y)
    y = get_y_at_x(x, p0, p1, p2, p3)

    lines: list[Text] = []
    width = 40

    def add_demo_row(label: str, progress: float, is_linear: bool = False) -> None:
        style = DIM if is_linear else ACCENT
        row = Text(f"{label.lower():8}", style=LABEL_FG)
        pos = int(progress * (width - 1))
        pos = max(0, min(width - 1, pos))
        track = Text("[", style=DIM)
        track.append("█" * pos, style=style)
        track.append("█", style=f"bold {VALUE_FG}")
        track.append("·" * (width - 1 - pos), style=DIM)
        track.append("]", style=DIM)
        row.append_text(track)
        lines.append(row)

    add_demo_row("linear", x, True)
    lines.append(Text(""))
    add_demo_row("eased", y)

    scale_row = Text("pulse   ", style=LABEL_FG)
    s_width = int(y * (width - 1))
    s_width = max(0, min(width - 1, s_width))
    scale_row.append("█" * s_width, style=SECONDARY)
    scale_row.append("█", style=f"bold {VALUE_FG}")
    scale_row.append("░" * (width - 1 - s_width), style=DIM)
    lines.append(Text(""))
    lines.append(scale_row)

    content = Text("\n").join(lines)
    return Panel(
        content,
        title="preview",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
        padding=(1, 2),
    )


def build_spectrum_panel(state: BezierState) -> Panel:
    """
    Technical momentum spectrum analysis.
    """
    width = 12
    p0 = (state.p0.x, state.p0.y)
    p1 = (state.dna_p1.x, state.dna_p1.y)
    p2 = (state.dna_p2.x, state.dna_p2.y)
    p3 = (state.p3.x, state.p3.y)

    velocities = get_velocity_samples(p0, p1, p2, p3, n=15)
    segments = []
    chunk_size = max(1, len(velocities) // 5)
    for i in range(5):
        chunk = velocities[i * chunk_size : (i + 1) * chunk_size]
        avg = sum(chunk) / len(chunk) if chunk else 0.0
        segments.append(avg)

    max_v = max(max(segments) if segments else 1.0, 1.0)
    bars = []
    for v in segments:
        level = (v / max_v) * width
        filled = int(max(0, min(width, level)))
        bars.append(f" [{'grey30' if filled <= 1 else HIGHLIGHT}]{'█' * filled}[/]")

    content = Text.from_markup("\n").join([Text.from_markup(b) for b in bars])
    return Panel(
        content,
        title="spectrum",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_coordinate_matrix(state: BezierState) -> Panel:
    """
    Dense real-time coordinate readout.
    """
    points = [state.p0, state.p1, state.p2, state.p3]
    lines = []
    for i, p in enumerate(points):
        sel = ">" if state.selected == f"p{i}" else " "
        lines.append(f"{sel}p{i} [bold]{p.x:5.3f}[/] [{DIM}]·[/] [bold]{p.y:5.3f}[/]")

    content = Text.from_markup("\n".join(lines))
    return Panel(
        content,
        title="matrix",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_history_panel(state: BezierState) -> Panel:
    """
    Build history trail.
    """
    lines: list[Text] = []
    history = [
        "0.250, 0.100, 0.250, 0.850",
        "0.420, 0.000, 0.580, 1.000",
        "0.170, 0.670, 0.830, 0.670",
    ]
    for h in history:
        lines.append(Text(f" {h}", style=DIM))
    content = Text("\n").join(lines)
    return Panel(
        content,
        title="history",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_stats_panel(state: BezierState) -> Panel:
    """
    Technical diagnostics.
    """
    lines = [
        f"[bold {ACCENT}]pts[/]  4 (cub)",
        f"[bold {SECONDARY}]dom[/]  [0, 1]",
        f"[bold {HIGHLIGHT}]ran[/]  [-.5, 1.5]",
        f"[bold {VALUE_FG}]sam[/]  150",
    ]
    content = Text.from_markup("\n".join(lines).lower())
    return Panel(
        content,
        title="stats",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_shortcuts_panel(state: BezierState) -> Panel:
    """
    Technical reference of all keybindings.
    """
    lines = [
        f"[{ACCENT}]/[/]     search",
        f"[{ACCENT}]tab[/]   cycle",
        f"[{ACCENT}]p[/]     preset",
        f"[{ACCENT}]arrows[/][{DIM}]move[/]",
        f"[{SECONDARY}][ ][/]   dna",
        f"[{SUCCESS}]c[/]     copy",
        f"[{HIGHLIGHT}]a[/]     anim",
        f"[{ERROR}]q[/]     quit",
    ]
    content = Text.from_markup("\n".join(lines).lower())
    return Panel(
        content,
        title="keybinds",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_physics_panel(state: BezierState) -> Panel:
    """
    Estimated mechanical properties of the curve.
    """
    import math

    # tension: derived from distance p0->p1 and p2->p3
    d1 = math.sqrt((state.dna_p1.x - state.p0.x) ** 2 + (state.dna_p1.y - state.p0.y) ** 2)
    d2 = math.sqrt((state.p3.x - state.dna_p2.x) ** 2 + (state.p3.y - state.dna_p2.y) ** 2)
    tension = (d1 + d2) * 5.0

    # friction: derived from velocity variance
    velocities = get_velocity_samples(
        (state.p0.x, state.p0.y),
        (state.dna_p1.x, state.dna_p1.y),
        (state.dna_p2.x, state.dna_p2.y),
        (state.p3.x, state.p3.y),
        n=20,
    )
    avg_v = sum(velocities) / len(velocities) if velocities else 1.0
    friction = 1.0 / max(0.1, avg_v)

    lines = [
        f"[bold {ACCENT}]tension [/] {tension:5.2f}",
        f"[bold {SECONDARY}]friction[/] {friction:5.2f}",
        f"[bold {HIGHLIGHT}]gravity [/] 9.81",  # constant for aesthetic
    ]
    content = Text.from_markup("\n".join(lines).lower())
    return Panel(
        content,
        title="physics",
        border_style=DIM,
        box=ROUNDED,
        expand=True,
    )


def build_preset_browser(state: BezierState, width: int, height: int) -> Panel:
    """
    Searchable preset browser.
    """
    lines: list[Text] = []

    # Search header
    search_line = Text(" search: ", style=LABEL_FG)
    q = state.preset_query.lower() if state.preset_query else "filter..."
    style = ACCENT if state.preset_query else DIM
    search_line.append(q, style=style)
    lines.append(search_line)
    lines.append(Text("-" * (width - 4), style=DIM))

    results = state.preset_search_results
    max_visible = int(height - 8)

    if not results:
        lines.append(Text("\n no results found", style=ERROR))
    else:
        start_idx = max(0, state.preset_search_index - max_visible // 2)
        end_idx = min(len(results), start_idx + max_visible)

        for i in range(start_idx, end_idx):
            name = results[i].lower()
            data = get_preset_data(results[i])
            is_sel = i == state.preset_search_index

            row = Text()
            if is_sel:
                row.append("> ", style=SECONDARY)
                row.append(f"{name:30}", style=f"bold {VALUE_FG} on {DIM}")
            else:
                row.append("  ", style=DIM)
                row.append(f"{name:30}", style=LABEL_FG)

            row.append(f" {data.category.lower()}", style=DIM)
            lines.append(row)

    content = Text("\n").join(lines)
    return Panel(
        content,
        title="presets",
        border_style=HIGHLIGHT,
        box=ROUNDED,
        padding=(1, 2),
        expand=True,
    )


def build_status_bar(state: BezierState) -> Text:
    """
    Build the status bar.
    """
    point = state.selected.lower()
    curr_point = getattr(state, state.selected)
    px, py = round(curr_point.x, 3), round(curr_point.y, 3)
    selector = f"[{SECONDARY}] {point} [/{SECONDARY}]"
    coords = f" [bold {VALUE_FG}]{px:.3f}, {py:.3f}[/]"
    hints = [
        f"[{HIGHLIGHT}]/[/{HIGHLIGHT}] [{DIM}]search[/]",
        f"[{ACCENT}]tab[/{ACCENT}] [{DIM}]cycle[/]",
        f"[{ACCENT}]p[/{ACCENT}] [{DIM}]preset[/]",
        f"[{SECONDARY}][ ][/{SECONDARY}] [{DIM}]dna {state.intensity:.1f}x[/]",
        f"[{SUCCESS}]c[/{SUCCESS}] [{DIM}]copy[/]",
        f"[{ERROR}]q[/{ERROR}] [{DIM}]quit[/]",
    ]
    status = Text.from_markup(f"{selector}{coords}  |  " + "  ".join(hints))
    return status


def build_y_ruler(state: BezierState, height: int) -> Panel:
    """
    Vertical y-axis ruler scale.
    """
    # Create scale markers from 1.5 down to -0.5
    scale = ["1.5", "1.0", "0.5", "0.0", "-0.5"]
    lines = []

    # Simple vertical interpolation for markers
    for i in range(height - 2):
        progress = i / (height - 3) if height > 3 else 0
        val = 1.5 - (progress * 2.0)

        # Snap to nearest scale point if close
        marker = " "
        for s_val in scale:
            if abs(val - float(s_val)) < 0.1:
                marker = s_val
                break

        lines.append(Text(f"{marker:>4} -", style=DIM))

    return Panel(Text("\n").join(lines), border_style=DIM, padding=0)


def build_data_stream(state: BezierState, height: int) -> Panel:
    """
    Vertical stream of hex-encoded point data.
    """
    import hashlib

    # Generate stable "noise" based on points
    raw = f"{state.p0}{state.p1}{state.p2}{state.p3}"
    seed = hashlib.md5(raw.encode()).hexdigest().lower()

    lines = []
    for i in range(height - 2):
        # Slice seed into 4-char segments
        start = (i * 2) % (len(seed) - 4)
        chunk = seed[start : start + 4]
        lines.append(Text(f"| {chunk}", style=DIM))

    return Panel(Text("\n").join(lines), border_style=DIM, padding=0)
