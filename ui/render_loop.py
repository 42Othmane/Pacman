"""Base render loop (pygame, MLX-compatible subset only).

Owner: Person B (Lot B). See docs/project-management/CAHIER_DES_CHARGES.md.

MLX-compatible function usage (document actual usage in README as you go):
    pygame.display.set_mode      -> mlx_new_window
    pygame.display.flip          -> mlx_loop / window refresh
    pygame.display.set_caption   -> window title (cosmetic, no MLX needed)
    surface.fill                 -> mlx_clear_window / fill via mlx_pixel_put
    pygame.draw.rect / .circle   -> manual pixel drawing (mlx_pixel_put loop)
    surface.blit                 -> mlx_put_image_to_window
    pygame.event.get + KEYDOWN   -> mlx_key_hook / mlx_hook
    pygame.time.Clock().tick     -> mlx_loop_hook (frame timing)
    pygame.font.Font + .render   -> mlx_string_put

Forbidden: pygame.mixer, pygame.sprite collision helpers, joystick, network.
"""
from typing import Optional, Dict, Type

import pygame

from ui.screens.base import Screen, ScreenName
from ui.screens.menu_screen import MenuScreen
from ui.screens.highscores_screen import HighscoresScreen
from ui.screens.instructions_screen import InstructionsScreen
from ui.screens.pause_screen import PauseScreen
from ui.screens.game_over_screen import GameOverScreen
from ui.screens.victory_screen import VictoryScreen

FPS = 60
WINDOW_TITLE = "Pac-Man"

# Colors (RGB) — kept here until a proper theming module exists.
COLOR_BACKGROUND = (0, 0, 0)


class RenderLoop:
    """Owns the pygame window and drives the main update/draw loop."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize pygame and open the game window.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Screen management
        self.screens: Dict[ScreenName, Screen] = {}
        self.current_screen: Optional[ScreenName] = None
        self.playing_screen_backup: Optional[Screen] = None
        
        # Initialize all screens
        self._init_screens()
        
        # Start with menu
        self.switch_to_screen(ScreenName.MENU)

    def _init_screens(self) -> None:
        """Initialize all available screens."""
        # Menu screen
        self.screens[ScreenName.MENU] = MenuScreen()
        
        # Highscores screen
        self.screens[ScreenName.HIGHSCORES] = HighscoresScreen([])
        
        # Instructions screen
        self.screens[ScreenName.INSTRUCTIONS] = InstructionsScreen()
        
        # Pause sceen
        self.screens[ScreenName.PAUSED] = PauseScreen()

        # Game Over screen
        self.screens[ScreenName.GAME_OVER] = GameOverScreen(0)

        # Victory screen
        self.screens[ScreenName.VICTORY] = VictoryScreen(0)

        # TODO: Add other screens as they are implemented
        # self.screens[ScreenName.PLAYING] = PlayingScreen()
        # self.screens[ScreenName.GAME_OVER] = GameOverScreen()
        # self.screens[ScreenName.VICTORY] = VictoryScreen()

    def switch_to_screen(self, screen_name: ScreenName) -> None:
        """Switch to a different screen."""
        if screen_name == ScreenName.EXIT:
            self.running = False
            return
        
        if screen_name == ScreenName.PAUSED and self.current_screen == ScreenName.PLAYING:
            self.playing_screen_backup = self.screens.get(ScreenName.PLAYING)
        
        if self.current_screen == ScreenName.PAUSED and screen_name == ScreenName.PLAYING:
            if self.playing_screen_backup:
                self.screens[ScreenName.PLAYING] = self.playing_screen_backup

        if screen_name == ScreenName.GAME_OVER:
            self.screens[ScreenName.GAME_OVER] = GameOverScreen(1234)
        elif screen_name == ScreenName.VICTORY:
            self.screens[ScreenName.VICTORY] = VictoryScreen(5678)
            
        if screen_name in self.screens:
            self.current_screen = screen_name
            screen = self.screens.get(screen_name)
            if screen and hasattr(screen, 'reset'):
                screen.reset()
        else:
            print(f"Warning: Screen {screen_name} not found, switching to menu")
            self.current_screen = ScreenName.MENU

    def handle_events(self) -> None:
        """Poll pending events and dispatch them to the current screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Dispatch event to current screen
            if self.current_screen:
                screen = self.screens.get(self.current_screen)
                if screen:
                    screen.handle_event(event)

    def update(self) -> None:
        """Update game state for this frame."""
        if not self.current_screen:
            return
            
        screen = self.screens.get(self.current_screen)
        if not screen:
            return
            
        # Update the current screen (dt = 1/60 for now, will be improved)
        dt = 1.0 / FPS
        next_screen = screen.update(dt)
        
        # Handle screen transitions
        if next_screen is not None:
            old_screen = screen
            self.switch_to_screen(next_screen)
            if hasattr(old_screen, 'reset_flags'):
                old_screen.reset_flags()

    def draw(self) -> None:
        """Clear the screen and redraw the current frame."""
        if self.current_screen == ScreenName.PAUSED and self.playing_screen_backup:
            # Dessiner le jeu figé
            self.screen.fill(COLOR_BACKGROUND)
            self.playing_screen_backup.draw(self.screen)
            # Puis dessiner l'overlay de pause par-dessus
            pause_screen = self.screens.get(ScreenName.PAUSED)
            if pause_screen:
                pause_screen.draw(self.screen)
        else:
            # Comportement normal
            self.screen.fill(COLOR_BACKGROUND)
            if self.current_screen:
                screen = self.screens.get(self.current_screen)
                if screen:
                    screen.draw(self.screen)
        
        pygame.display.flip()

    def run(self) -> None:
        """Run the main loop until the window is closed."""
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


def build_render_loop(width: int, height: int) -> RenderLoop:
    """Factory used by main.py to create the render loop.

    Args:
        width: Window width in pixels.
        height: Window height in pixels.

    Returns:
        A ready-to-run RenderLoop instance.
    """
    return RenderLoop(width, height)