"""Pause screen (spec 6.8).

Displays: Resume / Return to main menu. Drawn as an overlay on top of
the frozen game state.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName


class PauseScreen(Screen):
    """Pause overlay shown while gameplay is frozen."""

    def __init__(self) -> None:
        """Initialize the pause menu.

        Needs a reference/snapshot of the underlying PlayingScreen state
        so Resume can hand control back without losing progress.
        """
        # TODO: keep whatever is needed to resume PLAYING cleanly.
        raise NotImplementedError

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle selection between Resume and Return to menu."""
        raise NotImplementedError

    def update(self, dt: float) -> Optional[ScreenName]:
        """Return PLAYING on resume, MENU on return, else None."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the pause overlay (e.g. dimmed background + options)."""
        raise NotImplementedError