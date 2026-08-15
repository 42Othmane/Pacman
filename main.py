"""Entry point: python3 src/pacman/main.py config.json"""
import sys
from typing import NoReturn


def main() -> NoReturn:
    """Parse CLI args, load config, and start the game loop.

    Raises:
        SystemExit: always, with code 0 on normal exit or 1 on error.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <config.json>", file=sys.stderr)
        raise SystemExit(1)

    # TODO(person-A): load_config(sys.argv[1]) -> GameConfig
    # TODO(person-B): init graphics window, then run Menu -> Game loop

    raise SystemExit(0)


if __name__ == "__main__":
    main()
