"""Layout composition for the terminal UI using Rich Layout."""

from time import monotonic

from rich.layout import Layout
from rich.text import Text

from curv.render.panels import (
    build_animation_preview,
    build_control_panel,
    build_coordinate_matrix,
    build_export_cards,
    build_history_panel,
    build_physics_panel,
    build_preset_browser,
    build_preview_panel,
    build_shortcuts_panel,
    build_spectrum_panel,
    build_stats_panel,
    build_status_bar,
    build_tips_panel,
    build_velocity_panel,
)
from curv.state import BezierState

__all__ = ["build_layout"]

ACCENT = "bright_cyan"
DIM = "grey30"


def build_layout(
    state: BezierState, width: int, height: int, fps: float = 0.0
) -> Layout:
    """
    Build a responsive, high-density 3-column technical layout.
    """
    if state.show_preset_browser:
        # centered modal implementation using layout
        layout = Layout()
        layout.split_column(
            Layout(name="upper", size=height // 6),
            Layout(name="middle"),
            Layout(name="lower", size=height // 6),
        )
        layout["middle"].split_row(
            Layout(name="left", size=width // 4),
            Layout(name="center"),
            Layout(name="right", size=width // 4),
        )
        layout["middle"]["center"].update(
            build_preset_browser(state, width // 2, int(height // 1.5))
        )
        layout["upper"].update("")
        layout["lower"].update("")
        layout["middle"]["left"].update("")
        layout["middle"]["right"].update("")
        return layout

    # root layout
    root = Layout()

    compact = height < 35

    # global vertical structure
    root.split_column(
        Layout(name="header", size=2),
        Layout(name="body"),
        Layout(name="analytics", size=8),
        Layout(name="footer", size=2),
    )

    # header content
    header_text = Text.assemble(
        (" curv v1.0.0", f"bold {ACCENT}"),
        (f" {' ' * (width - 45)}", ""),
        (f"session: {monotonic():.1f}s  fps: {fps:.0f}  ", DIM),
    )
    root["header"].update(header_text)
    root["header"].split_column(
        Layout(header_text), Layout(Text("━" * width, style="grey15"), size=1)
    )

    # footer content
    root["footer"].update(build_status_bar(state))

    # body horizontal structure
    root["body"].split_row(
        Layout(name="left_wing", ratio=25),
        Layout(name="center_stage", ratio=50),
        Layout(name="right_wing", ratio=25),
    )

    # left wing content — reduce panels in compact mode
    left_panels = [
        Layout(build_control_panel(state, height // 4), ratio=2),
    ]
    if not compact:
        left_panels.append(Layout(build_spectrum_panel(state), ratio=1))
    left_panels.append(Layout(build_export_cards(state), ratio=1))
    if not compact:
        left_panels.append(Layout(build_shortcuts_panel(state), ratio=1))
    root["body"]["left_wing"].split_column(*left_panels)

    # center stage (super visualizer)
    c_width = int(width * 0.5)
    c_height = height - 12
    root["body"]["center_stage"].update(build_preview_panel(state, c_width, c_height))

    # right wing content — reduce panels in compact mode
    right_panels = [
        Layout(build_coordinate_matrix(state), ratio=1),
        Layout(build_stats_panel(state), ratio=1),
        Layout(build_physics_panel(state), ratio=1),
    ]
    if not compact:
        right_panels.append(Layout(build_tips_panel(state), ratio=1))
        right_panels.append(Layout(build_history_panel(state), ratio=1))
    root["body"]["right_wing"].split_column(*right_panels)

    # analytics row (velocity + animation)
    root["analytics"].split_row(
        Layout(build_velocity_panel(state, width // 2, 6), ratio=1),
        Layout(build_animation_preview(state), ratio=1),
    )

    return root
