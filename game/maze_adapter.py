"""Adapter for the A-Maze-ing package.

Converts the generator output to a simple grid format.
"""

import random
import sys
from typing import List

from mazegenerator import MazeGenerator


def translate_maze(maze_gen: MazeGenerator) -> List[List[int]]:
    """Convert A-Maze-ing maze to simple grid (1=wall, 0=open)."""
    raw_maze = maze_gen.maze

    h = len(raw_maze)
    w = len(raw_maze[0])

    simple_grid: List[List[int]] = []

    for y in range(h):
        row: List[int] = []
        for x in range(w):
            cell_value = raw_maze[y][x]
            if cell_value == 15:
                row.append(1)
            else:
                row.append(0)
        simple_grid.append(row)

    return simple_grid


def generate_level(
    level_number: int,
    width: int,
    height: int,
    base_seed: int
) -> List[List[int]]:
    """Generate a maze level using A-Maze-ing.

    Args:
        level_number: 1-based level index.
        width: Maze width in cells.
        height: Maze height in cells.
        base_seed: Seed for level 1 (levels > 1 use random seeds).

    Returns:
        2D grid where 1=wall, 0=open.
    """
    if level_number == 1:
        seed = base_seed
    else:
        seed = random.randint(1, 99999)

    try:
        maze = MazeGenerator(size=(width, height), perfect=False, seed=seed)
        return translate_maze(maze)
    except Exception as e:
        print(
            f"[Maze Adapter] Level {level_number} generation failed: {e}. "
            "Falling back to safe empty grid.",
            file=sys.stderr
        )
        width = max(width, 5)
        height = max(height, 5)
        safe_grid = [
            [1 if x == 0 or x == width - 1 or y == 0 or y == height - 1
             else 0 for x in range(width)]
            for y in range(height)
        ]
        return safe_grid
