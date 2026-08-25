"""Placement et consommation des pacgums dans le labyrinthe.

Convention : coordonnées en (y, x), y = ligne, x = colonne.
Les collectibles sont stockés dans les Cell du labyrinthe ; ce
manager ne fait que les placer et compter ce qui a été mangé.
"""

import random

from maze.cell import EMPTY, PACGUM, SUPER_PACGUM
from maze.loader import Maze


class CollectibleManager:
    """Place les pacgums dans le labyrinthe et suit leur consommation."""

    def __init__(self, maze: Maze, pacgum_count: int) -> None:
        """maze : labyrinthe à peupler.

        pacgum_count : nombre de pacgums simples souhaité (config).
        """
        self.maze = maze
        self.pacgums_eaten = 0
        self.total_pacgums = 0

        supers = self._place_super_pacgums()
        simples = self._place_pacgums(pacgum_count)
        self.total_pacgums = supers + simples

    def _place_super_pacgums(self) -> int:
        """Pose un super-pacgum dans chaque coin.

        Retourne le nombre réellement posé.
        """
        count = 0
        corners = self.maze.corners
        for y, x in corners:
            cell = self.maze.grid[y][x]
            cell.content = SUPER_PACGUM
            count += 1
        return count

    def _eligible_cells(self) -> list[tuple[int, int]]:
        """Cases pouvant recevoir un pacgum simple.

        Exclut les cases isolées du motif '42', celles déjà
        occupées, et la case de spawn du joueur.
        """
        eligible = []
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                if cell.is_isolated:
                    continue
                if cell.content != EMPTY:
                    continue
                if (y, x) == self.maze.spawn:
                    continue
                eligible.append((y, x))
        return eligible

    def _place_pacgums(self, wanted: int) -> int:
        """Tire au sort et pose les pacgums simples.

        Retourne le nombre réellement posé.
        """
        eligible = self._eligible_cells()
        count = min(wanted, len(eligible))
        for y, x in random.sample(eligible, count):
            self.maze.grid[y][x].content = PACGUM
        return count

    def eat(self, y: int, x: int) -> int:
        """Consomme le collectible en (y, x).

        Retourne PACGUM, SUPER_PACGUM, ou EMPTY si rien.
        """
        cell = self.maze.cell_at(y, x)
        if cell is None:
            return EMPTY
        eaten = cell.take_gum()
        if eaten != EMPTY:
            self.pacgums_eaten += 1
        return eaten

    def are_all_eaten(self) -> bool:
        """True si tous les collectibles ont été mangés."""
        return self.pacgums_eaten == self.total_pacgums