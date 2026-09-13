"""Entry point: python3 main.py config.json"""
import sys

from ui.render_loop import build_render_loop

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# PyInstaller sets sys.frozen on the bundled build. There, the game is
# launched from a desktop icon with no argument, so it falls back to
# the config shipped inside the package (see RenderLoop).
IS_FROZEN = getattr(sys, "frozen", False)


def main() -> None:
    """Parse CLI args and start the game loop.

    Raises:
        SystemExit: always, with code 0 on normal exit or 1 on error.
    """
    if not IS_FROZEN and len(sys.argv) != 2:
        print("Usage: python3 main.py <config.json>", file=sys.stderr)
        raise SystemExit(1)

    loop = build_render_loop(SCREEN_WIDTH, SCREEN_HEIGHT)
    loop.run()
    raise SystemExit(0)


if __name__ == "__main__":
    main()
