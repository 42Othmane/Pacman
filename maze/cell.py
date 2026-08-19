"""Représentation d'une case du labyrinthe.

Convention : grid[y][x], y = ligne (0 en haut), x = colonne.
Un mur à True signifie qu'il est FERMÉ (on ne passe pas).
"""

EMPTY = 0
PACGUM = 1
SUPER_PACGUM = 2


class Cell:
    """Une case du labyrinthe : ses 4 murs et son contenu."""

    def __init__(self, north: bool, east: bool,
                 south: bool, west: bool) -> None:
        self.north = north
        self.east = east
        self.south = south
        self.west = west
        self.content: int = EMPTY

    @classmethod
    def from_bitmask(cls, value: int) -> "Cell":
        """Construit une Cell depuis un entier A-Maze-ing.

        Bit 0 = Nord, 1 = Est, 2 = Sud, 3 = Ouest.
        Bit à 1 = mur fermé.
        """

        value &= 0xF

        return cls(
            north = bool(value & 1),
            east = bool(value & 2),
            south = bool(value & 4),
            west = bool(value & 8),
        )

    @property
    def is_isolated(self) -> bool:
        """True si les 4 murs sont fermés (case du motif '42')."""
        return all([self.north, self.east, self.south, self.west])

    def is_open(self, direction: str) -> bool:
        """True si on peut sortir dans cette direction ('N','E','S','W')."""
        walls = {"N": self.north, "E": self.east,
                 "S": self.south, "W": self.west}
        return not walls.get(direction, True)

    @property
    def has_pacgum(self) -> bool:
        return self.content == PACGUM

    @property
    def has_super_pacgum(self) -> bool:
        return self.content == SUPER_PACGUM
    @property
    def has_gum(self) -> bool:
        """True si la case contient un collectible, quel qu'il soit."""
        return self.content != EMPTY
    
    @property
    def take_gum(self) -> int:
        """Vide la case et renvoie ce qui s'y trouvait (EMPTY si rien)."""
        eaten = self.content
        self.content = EMPTY
        return eaten