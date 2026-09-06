"""Main menu screen (spec 6.8).

Displays: Start Game / View Highscores / Instructions / Exit.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName

COLOR_BACKGROUND = (0, 0, 0)
COLOR_TITLE = (255, 255, 0)         # Pac-Man yellow
COLOR_GHOST_ACCENT = (255, 0, 0)    # classic Blinky red, border accent
COLOR_OPTION = (255, 255, 255)      # unselected option text
COLOR_OPTION_SELECTED = (255, 255, 0)  # selected option text
COLOR_DOT = (255, 184, 174)         # soft pink, pacgum-style decoration

FONT_SIZE_TITLE = 64
FONT_SIZE_OPTION = 36


class MenuScreen(Screen):
    """Landing screen shown at launch and after a game ends."""

    def __init__(self) -> None:
        """Initialize the menu (load highscores for display, etc.)."""
        self.options = ["Start Game", "Highscores", "Instructions", "Exit"]
        self.index = 0
        self.selected_option: Optional[str] = None
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_option = pygame.font.Font(None, FONT_SIZE_OPTION)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu navigation input (select Start/Highscores/etc.)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.selected_option = self.options[self.index]

    def update(self, dt: float) -> Optional[ScreenName]:
        """Return the target screen for the selected option, else None."""
        if self.selected_option == "Start Game":
            self.selected_option = None
            return ScreenName.PLAYING
        elif self.selected_option == "Highscores":
            self.selected_option = None
            return ScreenName.HIGHSCORES
        elif self.selected_option == "Instructions":
            self.selected_option = None
            return ScreenName.INSTRUCTIONS
        elif self.selected_option == "Exit":
            return ScreenName.EXIT
        return None

    def reset(self) -> None:
        """Reset the menu to its initial state (called on re-entry)."""
        self.index = 0
        self.selected_option = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the Pac-Man themed main menu.

        Layout, top to bottom:
            1. Black background.
            2. A yellow Pac-Man icon (circle with a wedge mouth) above
               the title, so it reads as a logo rather than plain
               text.
            3. The "PAC-MAN" title.
            4. A row of small dots as a separator (echoes in-game
               pacgums).
            5. The menu options, with the selected one highlighted in
               yellow and prefixed by a small Pac-Man marker instead
               of a generic arrow/cursor — keeps the whole screen
               on-theme.
        """
        width = surface.get_width()

        surface.fill(COLOR_BACKGROUND)

        # Pac-Man icon: a yellow circle with a black wedge cut out as
        # the mouth. Drawn as a filled circle + a filled black triangle
        # overlapping it — same "manual shape drawing" category as
        # draw.rect/draw.circle already approved in the MLX-subset
        # notes; document draw.polygon there too if kept.
        icon_center = (width // 2, 90)
        icon_radius = 40
        pygame.draw.circle(surface, COLOR_TITLE, icon_center, icon_radius)
        mouth = [
            icon_center,
            (icon_center[0] + icon_radius, icon_center[1] - 18),
            (icon_center[0] + icon_radius, icon_center[1] + 18),
        ]
        pygame.draw.polygon(surface, COLOR_BACKGROUND, mouth)

        title_surf = self.font_title.render("PAC-MAN", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(width // 2, 160))
        surface.blit(title_surf, title_rect)

        # Decorative dot separator (evokes pacgums lining a corridor).
        dot_y = 200
        dot_spacing = 18
        dot_count = 9
        start_x = width // 2 - (dot_count // 2) * dot_spacing
        for i in range(dot_count):
            pygame.draw.circle(
                surface, COLOR_DOT, (start_x + i * dot_spacing, dot_y), 3
            )

        start_y = 260
        spacing = 60
        for i, option in enumerate(self.options):
            is_selected = i == self.index
            color = COLOR_OPTION_SELECTED if is_selected else COLOR_OPTION
            option_surf = self.font_option.render(option, True, color)
            option_rect = option_surf.get_rect(
                center=(width // 2, start_y + i * spacing)
            )
            surface.blit(option_surf, option_rect)

            if is_selected:
                marker_center = (option_rect.left - 24, option_rect.centery)
                pygame.draw.circle(
                    surface, COLOR_TITLE, marker_center, 8
                )
                marker_mouth = [
                    marker_center,
                    (marker_center[0] + 8, marker_center[1] - 4),
                    (marker_center[0] + 8, marker_center[1] + 4),
                ]
                pygame.draw.polygon(
                    surface, COLOR_BACKGROUND, marker_mouth
                )
