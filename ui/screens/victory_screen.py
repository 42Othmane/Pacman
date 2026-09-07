"""Victory screen (spec 6.8).

Displays the final score and prompts the player to enter their name
to save it in the highscore list.
"""
from highscore.manager import HighscoreEntry
from ui.screens.score_entry_screen import ScoreEntryScreen

TITLE = "VICTORY!"
TITLE_COLOR = (0, 255, 0)


class VictoryScreen(ScoreEntryScreen):
    """Victory screen with score entry."""

    def __init__(
        self,
        final_score: int,
        filename: str,
        hs_list: list[HighscoreEntry],
    ) -> None:
        """Initialize the Victory screen.

        Args:
            final_score: The player's final score.
            filename: Path to the highscore JSON file.
            hs_list: The current in-memory list of highscore entries.
        """
        super().__init__(
            final_score=final_score,
            filename=filename,
            hs_list=hs_list,
            title=TITLE,
            title_color=TITLE_COLOR,
        )
