"""Ghost sprite loading and rendering (spec 6.3).

Sprites are loaded and scaled ONCE per level (see load_ghost_sprites),
never inside the per-frame draw loop — loading/scaling images every
frame would be wasteful and is not how pygame.image.load is meant to
be used.

MLX-equivalent note: pygame.image.load + surface.blit map cleanly to
mlx_xpm_file_to_image/mlx_put_image_to_window. pygame.transform.scale
has no direct MLX equivalent — it is used here only once at load time
(pre-processing), not per frame, but flag this choice in the README
(Implementation section) for the peer review.
"""
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ghost import Ghost

SPRITE_DIR = "assets/sprites"

# Order matches the 4 corners as produced by Maze.corners
# (top-left, top-right, bottom-left, bottom-right) — adjust if your
# corner order differs.
GHOST_COLORS = ["red", "pink", "blue", "green"]


def load_ghost_sprites(tile_size: int) -> list[pygame.Surface]:
    """Load and scale one sprite per ghost color, once per level.

    Args:
        tile_size: Current tile size in pixels (sprites are scaled to
            match, since it changes between levels).

    Returns:
        A list of surfaces, in the same order as GHOST_COLORS.
    """
    sprites = []
    for color in GHOST_COLORS:
        path = f"{SPRITE_DIR}/{color}ghost.png"
        raw = pygame.image.load(path).convert_alpha()
        scaled = pygame.transform.scale(raw, (tile_size, tile_size))
        sprites.append(scaled)
    return sprites


def draw_ghosts(surface: pygame.Surface, ghosts: list["Ghost"]) -> None:
    """Draw each ghost using its assigned sprite, centered on its position.

    Args:
        surface: The pygame surface to draw on.
        ghosts: The list of Ghost instances to render.
    """
    for ghost in ghosts:
        rect = ghost.sprite.get_rect(center=(ghost.x, ghost.y))
        surface.blit(ghost.sprite, rect)
