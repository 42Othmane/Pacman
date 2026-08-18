"""Playing screen (spec 6.1-6.4, 6.6-6.8).

Renders the maze, player, ghosts, and HUD; drives gameplay updates each
frame; detects pause/game-over/victory transitions.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName


class PlayingScreen(Screen):
    """Active gameplay: maze, player, ghosts, HUD."""

    def __init__(self) -> None:
        """Initialize gameplay state for the current run.

        Expected inputs (finalize with Lot A's interface contract):
            - GameConfig (from Lot A's config loader)
            - shared game state (score, lives, level, timer, maze, ...)
        """
        # TODO: receive/construct shared game state object here.
        raise NotImplementedError

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle movement keys (arrows/WASD) and the pause key."""
        raise NotImplementedError

    def update(self, dt: float) -> Optional[ScreenName]:
        """Advance player/ghost logic; return PAUSED, GAME_OVER, or
        VICTORY when the corresponding condition is met, else None.
        """
        # TODO: move player, move ghosts (Lot B), check collisions,
        # check pacgum count / timer for level completion (Lot A hooks).
        # TODO: apply active cheat-mode effects (spec 6.5).
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the maze, player, ghosts, and the always-visible HUD."""
        raise NotImplementedError