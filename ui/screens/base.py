from abc import ABC, abstractmethod
from typing import Optional
import pygame
from enum import Enum

class ScreenName(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    HIGHSCORES = "highscores"
    INSTRUCTIONS = "instructions"
    EXIT = "exit"

class Screen(ABC):
    """Common interface every game screen must implement.

    The RenderLoop only talks to screens through this interface: it does
    not know whether it is currently showing the menu, the game, or the
    pause overlay.
    """
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """React to a single pygame event (keypress, click, etc.).

        Args:
            event: The pygame event to process.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> Optional[ScreenName]:
        """Advance this screen's logic by one frame.

        Args:
            dt: Time elapsed since the last frame, in seconds.

        Returns:
            None to stay on this screen, or the ScreenName of the next
            screen to transition to.
        """
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Render this screen onto the given surface.

        Args:
            surface: The pygame surface to draw on (the window surface).
        """
        pass
    