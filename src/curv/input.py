"""Keyboard input handling and state mutations."""

import dataclasses
import sys
from time import monotonic
from typing import Literal

# Load ctypes on Windows for modifier key detection
if sys.platform == "win32":
    import ctypes

import readchar

from curv.clipboard import copy as copy_to_clipboard
from curv.math.bezier import css_string
from curv.presets import get_preset, get_preset_names, search_presets
from curv.state import X_BOUNDS, Y_BOUNDS, BezierState, Point

__all__ = ["handle_key", "STEP_COARSE", "STEP_FINE"]

STEP_COARSE = 0.05
STEP_FINE = 0.005


def handle_key(state: BezierState, key: str) -> tuple[BezierState, bool]:
    """
    Enhanced input handling for elite features.
    """
    # ─── PRESET BROWSER MODE ──────────────────────────────────────────────────
    if state.show_preset_browser:
        if key in ("\r", "\n"):
            if state.preset_search_results:
                selected_name = state.preset_search_results[state.preset_search_index]
                p1, p2 = get_preset(selected_name)
                # Note: presets define p1, p2. p0 and p3 are reset for consistency.
                return (
                    dataclasses.replace(
                        state,
                        p0=Point(0.0, 0.0),
                        p1=Point(p1[0], p1[1]),
                        p2=Point(p2[0], p2[1]),
                        p3=Point(1.0, 1.0),
                        preset_name=selected_name,
                        show_preset_browser=False,
                        preset_query="",
                    ),
                    True,
                )
            return dataclasses.replace(state, show_preset_browser=False), True

        if key == "\x1b":
            return dataclasses.replace(state, show_preset_browser=False), True

        if key == readchar.key.UP:
            res_len = len(state.preset_search_results)
            new_idx = (state.preset_search_index - 1) % max(1, res_len)
            return dataclasses.replace(state, preset_search_index=new_idx), True
        if key == readchar.key.DOWN:
            res_len = len(state.preset_search_results)
            new_idx = (state.preset_search_index + 1) % max(1, res_len)
            return dataclasses.replace(state, preset_search_index=new_idx), True

        if key in ("\x7f", "\x08"):
            new_query = state.preset_query[:-1]
            results = search_presets(new_query)
            return (
                dataclasses.replace(
                    state,
                    preset_query=new_query,
                    preset_search_results=results,
                    preset_search_index=0,
                ),
                True,
            )

        if len(key) == 1 and key.isprintable():
            new_query = state.preset_query + key
            results = search_presets(new_query)
            return (
                dataclasses.replace(
                    state,
                    preset_query=new_query,
                    preset_search_results=results,
                    preset_search_index=0,
                ),
                True,
            )

        return state, True

    # ─── NORMAL MODE ──────────────────────────────────────────────────────────

    # / : open preset browser
    if key == "/":
        results = get_preset_names()
        return (
            dataclasses.replace(
                state,
                show_preset_browser=True,
                preset_search_results=results,
                preset_search_index=0,
                preset_query="",
            ),
            True,
        )

    # [ ] : Change DNA Intensity
    if key == "[":
        new_intensity = max(0.1, state.intensity - 0.1)
        return dataclasses.replace(state, intensity=new_intensity), True
    if key == "]":
        new_intensity = min(3.0, state.intensity + 0.1)
        return dataclasses.replace(state, intensity=new_intensity), True

    # Arrows for movement
    dx = 0.0
    dy = 0.0
    step = STEP_COARSE

    if key == readchar.key.UP:
        dy = step
    elif key == readchar.key.DOWN:
        dy = -step
    elif key == readchar.key.LEFT:
        dx = -step
    elif key == readchar.key.RIGHT:
        dx = step
    elif key == "\x1b[1;2A":  # Shift+Up
        dy = STEP_FINE
    elif key == "\x1b[1;2B":  # Shift+Down
        dy = -STEP_FINE
    elif key == "\x1b[1;2D":  # Shift+Left
        dx = -STEP_FINE
    elif key == "\x1b[1;2C":  # Shift+Right
        dx = STEP_FINE

    if dx != 0.0 or dy != 0.0:
        target_point = getattr(state, state.selected)
        new_point = target_point.moved(dx, dy).clamp(X_BOUNDS, Y_BOUNDS)

        # Explicit update to satisfy mypy type checking
        if state.selected == "p0":
            new_state = dataclasses.replace(state, p0=new_point)
        elif state.selected == "p1":
            new_state = dataclasses.replace(state, p1=new_point)
        elif state.selected == "p2":
            new_state = dataclasses.replace(state, p2=new_point)
        else:  # p3
            new_state = dataclasses.replace(state, p3=new_point)

        return new_state, True

    # Tab / Shift+Tab: cycle selected point
    if key == "\t":
        is_shift = False
        if sys.platform == "win32":
            # 0x10 is VK_SHIFT; high-order bit indicates if key is down
            is_shift = (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) != 0

        order: list[Literal["p0", "p1", "p2", "p3"]] = ["p0", "p1", "p2", "p3"]
        curr_idx = order.index(state.selected)

        if is_shift:
            next_point = order[(curr_idx - 1) % len(order)]
        else:
            next_point = order[(curr_idx + 1) % len(order)]

        return dataclasses.replace(state, selected=next_point), True

    # Shift+Tab (ANSI Sequence for Unix/Linux/Mac)
    if key in ("\x1b[Z", "\x00\x0f"):
        order = ["p0", "p1", "p2", "p3"]
        curr_idx = order.index(state.selected)
        prev_point = order[(curr_idx - 1) % len(order)]
        return dataclasses.replace(state, selected=prev_point), True

    # P: quick cycle presets
    if key.lower() == "p":
        names = get_preset_names()
        try:
            idx = names.index(state.preset_name)
        except ValueError:
            idx = -1
        next_name = names[(idx + 1) % len(names)]
        p1, p2 = get_preset(next_name)
        return (
            dataclasses.replace(
                state,
                p0=Point(0.0, 0.0),
                p1=Point(p1[0], p1[1]),
                p2=Point(p2[0], p2[1]),
                p3=Point(1.0, 1.0),
                preset_name=next_name,
            ),
            True,
        )

    # C: copy to clipboard
    if key.lower() == "c":
        css = css_string(
            (state.dna_p1.x, state.dna_p1.y), (state.dna_p2.x, state.dna_p2.y)
        )
        copy_to_clipboard(css)
        return (
            dataclasses.replace(
                state, flash_message="css copied", flash_until=monotonic() + 1.5
            ),
            True,
        )

    # A: toggle animation
    if key.lower() == "a":
        return dataclasses.replace(state, show_animation=not state.show_animation), True

    # H: toggle help
    if key.lower() == "h":
        return dataclasses.replace(state, show_help=not state.show_help), True

    # Q or Ctrl+C: quit
    if key.lower() == "q" or key == "\x03":
        return state, False

    return state, True
