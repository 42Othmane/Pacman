"""Game Over screen (spec 6.8).

Displays final score and prompts player to enter name for highscore.
"""
from ui.screens.score_entry_screen import ScoreEntryScreen

class GameOverScreen(ScoreEntryScreen):
    """Game Over screen with score entry."""

    def __init__(self, final_score: int) -> None:
        """Initialize the Game Over screen.

        Args:
            final_score: The player's final score.
        """
        super().__init__(
            final_score=final_score,
            title="GAME OVER",
            title_color=(255, 0, 0)  # Rouge
        )
