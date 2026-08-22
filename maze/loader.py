"""Chargement d'un labyrinthe depuis le package A-Maze-ing.

Convention : grid[y][x], y = ligne (0 en haut), x = colonne.
Ce module est la seule frontière avec le package externe : le reste
du jeu ne manipule que des objets Maze et Cell.
"""

import sys

from mazegenerator import MazeGenerator

from maze.cell import Cell

class Maze:
    """Un labyrinthe prêt à jouer : grille, spawn et coins."""

    def __init__(self, grid: list[list[Cell]]) -> None:
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self.spawn: tuple[int, int] = _find_spawn(grid)
        self.corners: list[tuple[int, int]] = _find_corners(
            self.height, self.width)

    def cell_at(self, y: int, x: int) -> Cell | None:
        """Case en (y, x), ou None si hors grille."""
        if self.in_bounds(y, x):
            return self.grid[y][x]
        else:
            return None

    def in_bounds(self, y: int, x: int) -> bool:
        """True si (y, x) est dans la grille."""
        return 0 <= y < self.height and 0 <= x < self.width


def _find_corners(height: int, width: int) -> list[tuple[int, int]]:
    """Les 4 coins de la grille, en (y, x)."""
    return [
        (0, 0),
        (0, width - 1),
        (height - 1, 0),
        (height - 1, width - 1),
    ]


def _find_spawn(grid: list[list[Cell]]) -> tuple[int, int]:
    """Case jouable la plus proche du centre, en (y, x).

    Le motif '42' occupe le centre avec des cases isolées : on cherche
    donc la case non isolée qui minimise la distance de Manhattan
    au centre géométrique.
    """

    height = len(grid)
    width = len(grid[0])

    center_y = height // 2
    center_x = width // 2

    best = (center_y, center_x)
    best_dist = float("inf")

    for y in range(height):
        for x in range(width):
            if grid[y][x].is_isolated:
                continue
            dist = abs(y - center_y) + abs(x - center_x)
            if dist < best_dist:
                best_dist = dist
                best = (y, x)
    
    return best

def _to_grid(raw: list[list[int]]) -> list[list[Cell]]:
    """Convertit la grille d'entiers A-Maze-ing en grille de Cell."""
    return [[Cell.from_bitmask(v) for v in row] for row in raw]


def _is_valid_raw(raw: object) -> bool:
    """True si la sortie du générateur est exploitable."""
    if not isinstance(raw, list) or not raw:
        return False
    expected = len(raw[0])
    for row in raw:
        if not isinstance(row, list) or not row:
            return False
        elif len(row) != expected:
            return False
        for value in row:
            if type(value) is not int:
                return False
    return True 


def load_maze(width: int, height: int, seed: int = 0) -> Maze | None:
    """Génère un labyrinthe via A-Maze-ing.

    seed > 0 : génération déterministe (niveau 1).
    seed <= 0 : génération aléatoire (niveaux suivants).
    Retourne None si la génération échoue.
    """
    try:
        generator = MazeGenerator(
            size=(width, height),
            perfect=False,
            seed=seed,
        )

        raw = generator.maze
        path = generator.shortest_path

    except Exception as e:
        print(f"Maze access failed: {e}", file=sys.stderr)
        return None

    if not _is_valid_raw(raw):
        print("Maze generation returned an invalid grid",
               file=sys.stderr)
        return None
    elif path is False:
        print("Maze has no path from entry to exit", file=sys.stderr)
        return None
    
    return Maze(_to_grid(raw))