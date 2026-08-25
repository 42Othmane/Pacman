"""Pause screen (spec 6.8).

Displays: Resume / Return to main menu. Drawn as an overlay on top of
the frozen game state.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName


COLOR_OVERLAY = (0, 0, 0, 180)  # Noir semi-transparent
COLOR_TITLE = (100, 100, 255, 200)  # Bleu semi-transparent
COLOR_OPTION = (255, 255, 255)
COLOR_OPTION_SELECTED = (255, 255, 0)

FONT_SIZE_TITLE = 150
FONT_SIZE_OPTION = 36


class PauseScreen(Screen):
    """Pause overlay shown while gameplay is frozen."""

    def __init__(self) -> None:
        """Initialize the pause menu.

        Needs a reference/snapshot of the underlying PlayingScreen state
        so Resume can hand control back without losing progress.
        """
        self.options = ["Resume Game", "Main Menu"]
        self.index = 0
        self.selected_option: Optional[str] = None
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_option = pygame.font.Font(None, FONT_SIZE_OPTION)

        self.overlay_surface = None

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle selection between Resume and Return to menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.selected_option = self.options[self.index]

    def update(self, dt: float) -> Optional[ScreenName]:
        """Return PLAYING on resume, MENU on return, else None."""
        if self.selected_option == "Resume Game":
            self.selected_option = None
            return ScreenName.PLAYING
        if self.selected_option == "Main Menu":
            self.selected_option = None
            return ScreenName.MENU
    
    def reset(self) -> None:
        """Reset the pause menu to its initial state (called on re-entry)."""
        self.index = 0
        self.selected_option = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the pause overlay (e.g. dimmed background + options)."""
        width = surface.get_width()
        height = surface.get_height()

        # Créer une surface temporaire avec support alpha
        if self.overlay_surface is None or self.overlay_surface.get_size() != (width, height):
            self.overlay_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Effacer la surface overlay
        self.overlay_surface.fill((0, 0, 0, 0))
        
        # Dessiner le fond semi-transparent sur la surface overlay
        pygame.draw.rect(self.overlay_surface, COLOR_OVERLAY, (0, 0, width, height))

        title_surf = self.font_title.render("PAUSED", True, (100, 100, 255))
        title_surf.set_alpha(200)  # Semi-transparent
        title_rect = title_surf.get_rect(center=(width // 2, 200))
        self.overlay_surface.blit(title_surf, title_rect)

        # --- Dessiner les options sur la surface overlay ---
        start_y = 400
        spacing = 60
        for i, option in enumerate(self.options):
            is_selected = i == self.index
            color = COLOR_OPTION_SELECTED if is_selected else COLOR_OPTION
            option_surf = self.font_option.render(option, True, color)
            option_rect = option_surf.get_rect(
                center=(width // 2, start_y + i * spacing)
            )
            self.overlay_surface.blit(option_surf, option_rect)

            if is_selected:
                # Small Pac-Man marker
                marker_center = (option_rect.left - 24, option_rect.centery)
                pygame.draw.circle(self.overlay_surface, (255, 255, 0), marker_center, 8)
                marker_mouth = [
                    marker_center,
                    (marker_center[0] + 8, marker_center[1] - 4),
                    (marker_center[0] + 8, marker_center[1] + 4),
                ]
                pygame.draw.polygon(self.overlay_surface, (0, 0, 0, 0), marker_mouth)

        surface.blit(self.overlay_surface, (0, 0))