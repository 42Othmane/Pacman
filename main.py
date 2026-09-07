"""Entry point: python3 src/pacman/main.py config.json"""
import sys
from ui.render_loop import build_render_loop

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800


def main() -> None:
    """Parse CLI args, load config, and start the game loop.

    Raises:
        SystemExit: always, with code 0 on normal exit or 1 on error.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <config.json>", file=sys.stderr)
        raise SystemExit(1)
    loop = build_render_loop(SCREEN_WIDTH, SCREEN_HEIGHT)

    loop.run()
    raise SystemExit(0)


if __name__ == "__main__":
    main()
