from typing import Optional
import pygame
from ui.screens.base import Screen, ScreenName

COLOR_TEXT = (255, 255, 255)
COLOR_TITLE = (255, 255, 0)
FONT_SIZE_TITLE = 48
FONT_SIZE_LINE = 26
LINE_SPACING = 34

INSTRUCTIONS_LINES = [
    "Move: Arrow keys or WASD",
    "Pause: P",
    "Eat all pacgums to complete a level",
    "Eat a super-pacgum to make ghosts edible",
    "Avoid ghosts unless they are edible",
    "",
    "Press ENTER or ESCAPE to go back",
]


class InstructionsScreen(Screen):
    """Read-only screen showing controls and rules."""

    def __init__(self) -> None:
        """Initialize screen state (static content, nothing to load)."""
        self.ret_menu = False
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_line = pygame.font.Font(None, FONT_SIZE_LINE)
    
    def reset_flags(self) -> None:
        """Reset flags after transition is triggered."""
        self.ret_menu = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Return to the menu on Escape, Enter, or Space."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.ret_menu = True

    def update(self, dt: float) -> Optional[ScreenName]:
        """Return MENU once the player asks to go back, else None."""
        if self.ret_menu:
            return ScreenName.MENU
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title and the static list of instructions."""
        surface.fill((0, 0, 0))
        width = surface.get_width()

        title_surf = self.font_title.render("Instructions", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(width // 2, 60))
        surface.blit(title_surf, title_rect)

        hint_surf = self.font_line.render("Press ENTER/SPACE/ESC to return", True, (128, 128, 128))
        hint_rect = hint_surf.get_rect(center=(width // 2, surface.get_height() - 40))
        surface.blit(hint_surf, hint_rect)

        start_y = 140
        for i, line in enumerate(INSTRUCTIONS_LINES):
            line_surf = self.font_line.render(line, True, COLOR_TEXT)
            line_rect = line_surf.get_rect(
                center=(width // 2, start_y + i * LINE_SPACING)
            )
            surface.blit(line_surf, line_rect)
