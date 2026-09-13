"""Player sprite loading (spec 6.2).

The player sprite sheet is a single row of square frames showing the
mouth opening and closing. Frames are cut, scaled to the current tile
size and pre-rotated for the four directions once per level, because
image loading and rotation are far too slow to redo every frame.
"""
import os
import sys
from typing import Optional

import pygame

from resources import resource_path

SPRITE_PATH = resource_path(os.path.join("assets", "pacman.png"))
FRAME_COUNT = 6

# Sprites are drawn facing East; rotate counter-clockwise from there.
#
# West is deliberately absent. Rotating East by 180 degrees does point
# the mouth left, but it also turns the sprite upside down — the eye
# ends up at the bottom. West is built with a horizontal flip instead
# (see load_player_frames), which swaps left and right while leaving
# top and bottom alone.
DIRECTION_ANGLES: dict[str, int] = {"E": 0, "N": 90, "S": 270}


def load_player_frames(
    tile_size: int,
) -> Optional[dict[str, list[pygame.Surface]]]:
    """Load the sprite sheet and pre-render every direction and frame.

    Args:
        tile_size: Current tile size in pixels; frames are scaled to
            it.

    Returns:
        A dict mapping "N"/"E"/"S"/"W" to that direction's list of
        FRAME_COUNT surfaces, or None if the sheet cannot be read (the
        caller is expected to fall back to a plain circle).
    """
    try:
        sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
    except (pygame.error, FileNotFoundError, OSError) as error:
        print(f"Player sprite not loaded: {error}", file=sys.stderr)
        return None

    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // FRAME_COUNT
    if frame_width <= 0 or sheet_height <= 0:
        print(
            "Player sprite sheet has unusable dimensions.",
            file=sys.stderr,
        )
        return None

    size = max(1, tile_size)
    base_frames: list[pygame.Surface] = []
    for index in range(FRAME_COUNT):
        frame = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
        frame.blit(
            sheet,
            (0, 0),
            pygame.Rect(index * frame_width, 0, frame_width, sheet_height),
        )
        base_frames.append(pygame.transform.smoothscale(frame, (size, size)))

    frames = {
        direction: [
            pygame.transform.rotate(frame, angle) for frame in base_frames
        ]
        for direction, angle in DIRECTION_ANGLES.items()
    }
    frames["W"] = [
        pygame.transform.flip(frame, True, False) for frame in base_frames
    ]
    return frames
