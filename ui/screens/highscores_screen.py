from typing import Optional
import pygame
from ui.screens.base import Screen, ScreenName

COLOR_TEXT = (255, 255, 255)
COLOR_TITLE = (255, 255, 0)
FONT_SIZE_TITLE = 48
FONT_SIZE_ENTRY = 28
LINE_SPACING = 36


class HighscoresScreen(Screen):
    """Read-only screen listing the top 10 scores."""

    def __init__(self, scores: list[tuple[str, int]]) -> None:
        """Store the highscore list to display.

        Args:
            scores: List of (player_name, score) tuples, already sorted
                and truncated to the top 10 by the highscore module.
        """
        self.scores = scores
        self.should_return_to_menu = False
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_entry = pygame.font.Font(None, FONT_SIZE_ENTRY)
    
    def reset_flags(self) -> None:
        """Reset flags after transition is triggered."""
        self.should_return_to_menu = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Return to the menu on Escape, Enter, or Space."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.should_return_to_menu = True

    def update(self, dt: float) -> Optional[ScreenName]:
        """Return MENU once the player asks to go back, else None."""
        if self.should_return_to_menu:
            return ScreenName.MENU
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title and the ranked list of scores."""
        surface.fill((0, 0, 0))
        width = surface.get_width()

        title_surf = self.font_title.render("Highscores", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(width // 2, 60))
        surface.blit(title_surf, title_rect)

        hint_surf = self.font_entry.render("Press ENTER/SPACE/ESC to return", True, (128, 128, 128))
        hint_rect = hint_surf.get_rect(center=(width // 2, surface.get_height() - 40))
        surface.blit(hint_surf, hint_rect)

        if not self.scores:
            empty_surf = self.font_entry.render(
                "No highscores yet.", True, COLOR_TEXT
            )
            empty_rect = empty_surf.get_rect(center=(width // 2, 140))
            surface.blit(empty_surf, empty_rect)
            return

        start_y = 140
        for rank, (name, score) in enumerate(self.scores, start=1):
            line = f"{rank}. {name} - {score} pts"
            line_surf = self.font_entry.render(line, True, COLOR_TEXT)
            line_rect = line_surf.get_rect(
                center=(width // 2, start_y + (rank - 1) * LINE_SPACING)
            )
            surface.blit(line_surf, line_rect)
