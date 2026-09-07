"""Bundled resource path resolution.

In development, assets sit in the project folder. Inside a PyInstaller
build they are unpacked to a temporary directory exposed as
sys._MEIPASS, so relative paths written for development would not
resolve. resource_path() handles both cases.
"""
import os
import sys


def resource_path(relative: str) -> str:
    """Return the absolute path of a bundled read-only resource.

    Args:
        relative: Path relative to the project root, e.g.
            os.path.join("assets", "pacman.png").

    Returns:
        An absolute path usable by pygame.image.load() or open().
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, relative)
