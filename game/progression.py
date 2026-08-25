"""Progression de partie : niveaux, timer, score et vies.

Convention : coordonnées en (y, x).
"""

from maze.cell import PACGUM, SUPER_PACGUM
from game.collectables import CollectibleManager
from game.player import Player
from game.scoring import Score
from maze.loader import load_maze
import sys

STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_WON = "won"
STATE_LOST = "lost"


class Game:
    """Une partie complète : plusieurs niveaux, un score, des vies."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.levels = config["levels"]
        self.max_time = float(config["level_max_time"])
        self.lives = config["lives"]

        self.score = Score(
            config["points_per_pacgum"],
            config["points_per_super_pacgum"],
            config["points_per_ghost"],
        )

        self.level_index = 0
        self.state = STATE_PLAYING
        self.time_left = self.max_time
        self.maze = None
        self.collectibles = None
        self.player = None

        self.move_interval = 0.25
        self.move_timer = 0.0

        self.start_level(0)

    def start_level(self, index: int) -> bool:
        """Charge le niveau `index`. False si la génération échoue."""
        if index < 0 or index >= len(self.levels):
            return False
        width = self.levels[index]["width"]
        height = self.levels[index]["height"]
        if index == 0:
            seed = self.config["seed"]
        else:
            seed = 0
        maze = load_maze(width, height, seed)
        if maze is None:
            print("Maze couldn't be loaded", file=sys.stderr)
            return False
        self.maze = maze
        self.collectibles = CollectibleManager(maze, self.config["pacgum"])
        self.player = Player(maze, self.lives)
        self.level_index = index
        self.time_left = self.max_time
        return True

    def handle_input(self, direction: str) -> None:
        """Enregistre la direction souhaitée par le joueur."""
        if self.state != STATE_PLAYING:
            return
        self.player.request_direction(direction)

    def _step_player(self) -> None:
        """Avance le joueur d'une case et applique les conséquences."""
        if not self.player.step():
            return
        y, x = self.player.position
        eaten = self.collectibles.eat(y, x)
        if eaten == PACGUM:
            self.score.add_pacgum()
        elif eaten == SUPER_PACGUM:
            self.score.add_superpacgum()
        if self.collectibles.are_all_eaten():
            self.next_level()

    def tick(self, delta: float) -> None:
        if self.state != STATE_PLAYING:
            return

        self.player.tick(delta, 1.0 / self.move_interval)

        self.move_timer += delta
        while self.move_timer >= self.move_interval:
            self.move_timer -= self.move_interval
            self._step_player()
            if self.state != STATE_PLAYING:
                break

        self.time_left -= delta
        if self.time_left <= 0:
            self.time_left = 0
            self.player_caught()
            if self.state != STATE_LOST:
                self.start_level(self.level_index)

    def player_caught(self) -> None:
        """Le joueur a été touché par un fantôme."""
        if self.state != STATE_PLAYING:
            return
        self.player.lose_life()
        self.lives = self.player.lives
        if self.player.is_game_over():
            self.state = STATE_LOST

    def next_level(self) -> None:
        """Passe au niveau suivant, ou gagne la partie."""
        if self.level_index + 1 >= len(self.levels):
            self.state = STATE_WON
            return
        if not self.start_level(self.level_index + 1):
            self.state = STATE_WON

    def toggle_pause(self) -> None:
        """Bascule pause / jeu."""
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED
        elif self.state == STATE_PAUSED:
            self.state = STATE_PLAYING

    @property
    def is_over(self) -> bool:
        """True si la partie est finie."""
        return self.state in (STATE_WON, STATE_LOST)