"""Victory screen (spec 6.8).

Displays final score and prompts player to enter name for highscore.
"""
from ui.screens.score_entry_screen import ScoreEntryScreen

class VictoryScreen(ScoreEntryScreen):
    """Victory screen with score entry."""

    def __init__(self, final_score: int) -> None:
        """Initialize the Victory screen.

        Args:
            final_score: The player's final score.
        """
        super().__init__(
            final_score=final_score,
            title="VICTORY!",
            title_color=(0, 255, 0)  # Vert
        )
