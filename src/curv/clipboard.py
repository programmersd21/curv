"""Clipboard operations with graceful degradation."""

import pyperclip

__all__ = ["copy", "is_available"]


def is_available() -> bool:
    """
    Check if clipboard operations are available.

    Returns:
        True if clipboard access is expected to work
    """
    try:
        # Try a dummy operation to test availability
        pyperclip.copy("")
        return True
    except Exception:  # noqa: BLE001
        return False


def copy(text: str) -> bool:
    """
    Copy text to the clipboard.

    Args:
        text: The text to copy

    Returns:
        True if successful, False if clipboard access is unavailable
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception:  # noqa: BLE001
        return False
