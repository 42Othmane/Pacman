"""Usage:
    python3 tests/manual/test_screen_visual.py highscores
    python3 tests/manual/test_screen_visual.py instructions
"""
import sys
from pathlib import Path

import pygame

# Allow running this script directly without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ui.screens.highscores_screen import HighscoresScreen  # noqa: E402
from ui.screens.instructions_screen import InstructionsScreen  # noqa: E402
from ui.screens.menu_screen import MenuScreen
from ui.screens.pause_screen import PauseScreen

WINDOW_WIDTH = 630
WINDOW_HEIGHT = 760
FPS = 60

FAKE_SCORES = [
    ("Alice", 1250),
    ("Bob", 980),
    ("Carol", 760),
    ("Dave", 500),
    ("Eve", 320),
]


def build_screen(name: str):
    """Instantiate the requested screen with dummy/fake data.

    Args:
        name: "highscores" or "instructions".

    Returns:
        A Screen instance ready to run.
    """
    if name == "highscores":
        return HighscoresScreen(FAKE_SCORES)
    if name == "instructions":
        return InstructionsScreen()
    if name == "menu":
        return MenuScreen()
    if name == "pause":
        return PauseScreen()
    raise ValueError(f"Unknown screen: {name!r} (use 'highscores' or 'instructions')")


def run(screen_name: str) -> None:
    """Run a single screen in its own pygame window until it transitions.

    Args:
        screen_name: Which screen to test (see build_screen()).
    """
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(f"Manual test: {screen_name}")
    clock = pygame.time.Clock()

    current = build_screen(screen_name)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                current.handle_event(event)

        next_screen = current.update(dt)
        if next_screen is not None:
            print(f"[manual test] {screen_name} requested transition to: {next_screen}")
            running = False

        current.draw(window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_screen_visual.py <highscores|instructions>")
        raise SystemExit(1)
    run(sys.argv[1])