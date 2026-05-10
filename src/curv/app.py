"""Main application class."""

import queue
import sys
import threading
from time import monotonic, sleep

import readchar
from rich.console import Console
from rich.live import Live

from curv.input import handle_key
from curv.math.bezier import css_string, hypr_string
from curv.render.layout import build_layout
from curv.state import default_state

__all__ = ["App"]


class App:
    """Main curv application."""

    def __init__(self) -> None:
        """Initialize the application."""
        self._console = Console()
        self._state = default_state()
        self._input_queue: queue.Queue[str] = queue.Queue()
        self._running = False

    def _input_listener(self) -> None:
        """Background thread to listen for keyboard input."""
        while self._running:
            try:
                key = readchar.readkey()
                self._input_queue.put(key)
            except Exception:
                break

    def run(self) -> None:
        """Run the main application loop optimized for high FPS."""
        self._running = True
        input_thread = threading.Thread(target=self._input_listener, daemon=True)
        input_thread.start()

        # Target 120 FPS for that "smooth af" feel
        target_fps = 120
        frame_duration = 1.0 / target_fps

        try:
            with Live(
                screen=True,
                refresh_per_second=target_fps,
                transient=False,
                console=self._console,
                auto_refresh=False,  # We will manually refresh for tighter control
            ) as live:
                while self._running:
                    start_time = monotonic()

                    # Get current console dimensions
                    width = self._console.width
                    height = self._console.height

                    # Process all pending input
                    while not self._input_queue.empty():
                        key = self._input_queue.get_nowait()
                        new_state, should_continue = handle_key(self._state, key)
                        self._state = new_state
                        if not should_continue:
                            self._running = False
                            break

                    if not self._running:
                        break

                    # Build and render layout
                    layout = build_layout(self._state, width, height)
                    live.update(layout, refresh=True)

                    # High-precision frame timing
                    elapsed = monotonic() - start_time
                    sleep_time = frame_duration - elapsed
                    if sleep_time > 0:
                        sleep(sleep_time)

        finally:
            self._running = False

        # Print final output to scrollback
        p1 = (self._state.p1.x, self._state.p1.y)
        p2 = (self._state.p2.x, self._state.p2.y)

        css = css_string(p1, p2).lower()
        hypr = hypr_string(p1, p2).lower()
        swift = (
            f"animation.timingcurve({p1[0]:.3f}, {p1[1]:.3f}, {p2[0]:.3f}, {p2[1]:.3f})"
        )

        self._console.print()
        self._console.print(f" css:   {css}")
        self._console.print(f" hypr:  {hypr}")
        self._console.print(f" swift: {swift}")
        self._console.print()
        sys.stdout.flush()
