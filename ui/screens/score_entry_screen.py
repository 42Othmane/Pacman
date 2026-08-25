"""Base screen for score entry (Game Over / Victory).

Handles player name input and highscore saving.
"""
from typing import Optional
import pygame
from ui.screens.base import Screen, ScreenName
import highscore.manager as hs

# Couleurs communes
COLOR_BACKGROUND = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_INSTRUCTION = (200, 200, 200)
COLOR_ERROR = (255, 50, 50)
COLOR_CURSOR = (255, 255, 255)

FONT_SIZE_TITLE = 72
FONT_SIZE_SCORE = 48
FONT_SIZE_NAME = 36
FONT_SIZE_INSTRUCTION = 28
FONT_SIZE_ERROR = 24

class ScoreEntryScreen(Screen):
    """Base class for screens that require player name input.
    
    Handles:
        - Name input (max 10 chars, alphanumeric + spaces)
        - Cursor blinking
        - Score display
        - Highscore saving with error handling
    """

    def __init__(self, final_score: int, title: str, title_color: tuple, filename: str, hs_list: list) -> None:
        """Initialize the score entry screen.

        Args:
            final_score: The player's final score to save.
            title: The title text (e.g., "GAME OVER" or "VICTORY!").
            title_color: RGB color for the title.
        """
        self.final_score = final_score
        self.title = title
        self.title_color = title_color
        self.filename = filename
        self.hs_list = hs_list
        
        # État de la saisie
        self.player_name = ""
        self.name_confirmed = False
        self.save_error = False
        self.error_message = ""
        self.show_retry = False
        
        # Curseur clignotant
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 0.5  # Change toutes les 0.5 secondes
        
        # Fonts
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_score = pygame.font.Font(None, FONT_SIZE_SCORE)
        self.font_name = pygame.font.Font(None, FONT_SIZE_NAME)
        self.font_instruction = pygame.font.Font(None, FONT_SIZE_INSTRUCTION)
        self.font_error = pygame.font.Font(None, FONT_SIZE_ERROR)
        
        # Flag pour savoir si on a déjà tenté de sauvegarder
        self.saved = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard input for name entry and validation."""
        if self.save_error and self.show_retry:
            # En cas d'erreur, on gère les boutons "Try Again" et "Quit"
            self._handle_error_events(event)
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Validation du nom
                self._confirm_name()
            elif event.key == pygame.K_BACKSPACE:
                # Supprimer le dernier caractère
                self.player_name = self.player_name[:-1]
            else:
                # Ajouter un caractère si valide et max 10 chars
                char = event.unicode
                if len(self.player_name) < 10 and self._is_valid_char(char):
                    self.player_name += char

    def _handle_error_events(self, event: pygame.event.Event) -> None:
        """Handle events when an error dialog is shown."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Try Again
                self._retry_save()
            elif event.key == pygame.K_q:  # Quit without saving
                self._quit_without_saving()

    def _is_valid_char(self, char: str) -> bool:
        """Check if character is alphanumeric or space."""
        return char.isalnum() or char == ' '

    def _confirm_name(self) -> None:
        """Confirm the player name and attempt to save."""
        # Si le nom est vide, utiliser "anonymous"
        if not self.player_name.strip():
            self.player_name = "anonymous"
        
        # Tenter de sauvegarder
        self._save_highscore()

    def _save_highscore(self) -> None:
        """Save the highscore using the highscore manager."""
        try:
            if hs._validate_name(self.player_name):
                newlist = hs.add_highscore(self.player_name, self.final_score, self.hs_list)
                hs.save_highscores(self.filename, newlist)
                self.saved = True
                self.name_confirmed = True
            else:
                self._show_error("Failed to save highscore")
        except Exception as e:
            self._show_error(f"Error: {str(e)}")

    def _show_error(self, message: str) -> None:
        """Show an error message with options."""
        self.save_error = True
        self.error_message = message
        self.show_retry = True

    def _retry_save(self) -> None:
        """Retry saving the highscore."""
        self.save_error = False
        self.error_message = ""
        self.show_retry = False
        self._save_highscore()

    def _quit_without_saving(self) -> None:
        """Quit to menu without saving."""
        self.save_error = False
        self.error_message = ""
        self.show_retry = False
        self.name_confirmed = True
        self.saved = True

    def update(self, dt: float) -> Optional[ScreenName]:
        """Update cursor blinking and return MENU when confirmed."""
        # Mise à jour du curseur clignotant
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_interval:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
        
        # Retourner au menu une fois le nom confirmé
        if self.name_confirmed:
            return ScreenName.MENU
        
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the score entry screen."""
        width = surface.get_width()
        height = surface.get_height()
        
        # 1. Fond noir
        surface.fill(COLOR_BACKGROUND)
        
        # 2. Titre (GAME OVER ou VICTORY!)
        title_surf = self.font_title.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(width // 2, 100))
        surface.blit(title_surf, title_rect)
        
        # 3. Score
        score_text = f"Score: {self.final_score} pts"
        score_surf = self.font_score.render(score_text, True, COLOR_TEXT)
        score_rect = score_surf.get_rect(center=(width // 2, 200))
        surface.blit(score_surf, score_rect)
        
        # 4. Instruction
        inst_surf = self.font_instruction.render(
            "Enter your name:", True, COLOR_INSTRUCTION
        )
        inst_rect = inst_surf.get_rect(center=(width // 2 - 80, 300))
        surface.blit(inst_surf, inst_rect)
        
        # 5. Nom saisi avec curseur
        name_display = self.player_name
        if self.cursor_visible and not self.save_error:
            name_display += "|"
        
        name_surf = self.font_name.render(name_display, True, COLOR_TEXT)
        name_rect = name_surf.get_rect(center=(width // 2 + 80, 300))
        surface.blit(name_surf, name_rect)
        
        # 6. Indication de la limite
        limit_text = f"({len(self.player_name)}/10 chars)"
        limit_surf = self.font_instruction.render(limit_text, True, COLOR_INSTRUCTION)
        limit_rect = limit_surf.get_rect(center=(width // 2, 340))
        surface.blit(limit_surf, limit_rect)
        
        # 7. Message d'erreur si présent
        if self.save_error:
            # Fond semi-transparent pour l'erreur
            error_box = pygame.Surface((600, 150), pygame.SRCALPHA)
            error_box.fill((50, 0, 0, 200))
            surface.blit(error_box, (width // 2 - 300, height // 2 - 75))
            
            # Message d'erreur
            error_surf = self.font_error.render(
                self.error_message, True, COLOR_ERROR
            )
            error_rect = error_surf.get_rect(center=(width // 2, height // 2 - 20))
            surface.blit(error_surf, error_rect)
            
            # Options
            retry_text = "Press 'R' to Try Again"
            quit_text = "Press 'Q' to Quit without saving"
            retry_surf = self.font_instruction.render(retry_text, True, COLOR_TEXT)
            quit_surf = self.font_instruction.render(quit_text, True, COLOR_TEXT)
            
            retry_rect = retry_surf.get_rect(center=(width // 2, height // 2 + 30))
            quit_rect = quit_surf.get_rect(center=(width // 2, height // 2 + 60))
            
            surface.blit(retry_surf, retry_rect)
            surface.blit(quit_surf, quit_rect)