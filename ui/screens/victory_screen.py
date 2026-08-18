"""Victory screen (spec 6.7-6.8).

Displays the final score, a congratulatory message, and prompts the
player to enter their name to save it in the highscore list.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName


class VictoryScreen(Screen):
    """Shown when the player completes all levels."""

    def __init__(self, final_score: int) -> None:
        """Store the final score and prepare the name-entry input.

        Args:
            final_score: The player's score at the end of the last level.
        """
        # TODO: init a text-input state for the player name
        # (max 10 chars, alphanumeric + spaces only — see spec 5.5).
        raise NotImplementedError

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle text input for the player name and confirmation key."""
        raise NotImplementedError

    def update(self, dt: float) -> Optional[ScreenName]:
        """Save the highscore (via Lot A's module) and return MENU once
        the name is confirmed, else None.
        """
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the final score, congratulatory message, and name prompt."""
        raise NotImplementedError