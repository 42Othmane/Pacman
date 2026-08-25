"""Le joueur : position, déplacement et vies.

Convention : coordonnées en (y, x), y = ligne, x = colonne.
"""

from maze.loader import Maze

DELTAS = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
}


class Player:
    """Pac-Man : sa position dans le labyrinthe et ses vies."""

    def __init__(self, maze:  Maze, lives: int) -> None:
        self.maze = maze
        self.lives = lives
        self.y, self.x = maze.spawn
        self.direction = "E"
        self.prev_y, self.prev_x = self.y, self.x
        self.move_progress: float = 1.0
        self.next_direction: str | None = None

    def request_direction(self, direction: str) -> None:
        """Enregistre la direction souhaitée par le joueur.

        Elle sera appliquée dès que le passage sera possible.
        """
        if direction in DELTAS:
            self.next_direction = direction


    def step(self) -> bool:
        """Avance d'une case. True si le joueur a bougé."""
        if self.next_direction is not None and self.can_move(self.next_direction):
            self.direction = self.next_direction
            self.next_direction = None
        return self.move(self.direction)


    def tick(self, delta: float, speed: float) -> None:
        """Fait progresser l'animation de déplacement.

        speed : cases par seconde.
        """
        if self.move_progress < 1.0:
            self.move_progress = min(1.0, self.move_progress + delta * speed)

    @property
    def position(self) -> tuple[int, int]:
        """Position courante en (y, x)."""
        return (self.y, self.x)
        

    def can_move(self, direction: str) -> bool:
        """True si le déplacement est possible depuis la case courante."""
        
        if direction not in DELTAS:
            return False
        dy, dx = DELTAS[direction]
        ny, nx = self.y + dy, self.x + dx
        cell = self.maze.grid[self.y][self.x]
        return cell.is_open(direction) and self.maze.in_bounds(ny, nx)

    def move(self, direction: str) -> bool:
        """Déplace le joueur d'une case. Retourne True si ça a bougé."""
        if not self.can_move(direction):
            return False
        dy, dx = DELTAS[direction]
        self.prev_y, self.prev_x = self.y, self.x
        self.move_progress = 0.0
        self.y += dy
        self.x += dx
        self.direction = direction
        return True

    def lose_life(self) -> None:
        """Retire une vie et replace le joueur au spawn."""
        self.lives -= 1
        self.y, self.x = self.maze.spawn
        self.prev_y, self.prev_x = self.y, self.x
        self.move_progress = 1.0
        self.direction = "E"
        self.next_direction = None


    def is_game_over(self) -> bool:
        """True si le joueur n'a plus de vies."""
        return self.lives <= 0