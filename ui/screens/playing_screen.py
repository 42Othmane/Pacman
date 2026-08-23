"""Reference snippet: PlayingScreen __init__ adapted to the real config
format (see config.example.json / loader.py).

Merge into your actual playing_screen.py — adapt to your exact
signature/attribute names as needed.
"""
import pygame
from maze.loader import load_maze
from game.ghost import Ghost
from ui.draw_ghosts import load_ghost_sprites, draw_ghosts

COLOR_BACKGROUND = (0, 0, 0)
COLOR_WALL = (33, 33, 222)
COLOR_PACGUM = (255, 222, 173)
COLOR_SUPER_PACGUM = (255, 222, 173)
COLOR_42_PATTERN = (255, 255, 0)

COLOR_GHOST = (255, 0, 0)
GHOST_SIZE_RATIO = 0.7 

WALL_THICKNESS = 1
PACGUM_RADIUS = 3
SUPER_PACGUM_RADIUS = 8

HUD_HEIGHT = 60


class PlayingScreen:
    """Active gameplay: maze, player, ghosts, HUD."""

    def __init__(
        self,
        config: dict,
        level_index: int,
        window_width: int,
        window_height: int,
    ) -> None:
        """Initialize gameplay state for the given level.

        Args:
            config: Full parsed game config (see config.example.json).
            level_index: 0-based index into config["levels"].
            window_width: Window width in pixels.
            window_height: Window height in pixels.
        """
        self.config = config
        self.level_index = level_index

        level_spec = config["levels"][level_index]
        # Spec 6.1: level 1 uses the fixed seed, later levels are random.
        seed = config["seed"] if level_index == 0 else 0
        maze = load_maze(
            width=level_spec["width"],
            height=level_spec["height"],
            seed=seed,
        )
        if maze is None:
            raise RuntimeError(
                f"Failed to generate maze for level {level_index + 1}"
            )
        self.maze = maze
        # Recomputed every level, since maze dimensions grow each time.
        playable_height = window_height - HUD_HEIGHT
        self.tile_size = min(
            window_width // self.maze.width,
            playable_height // self.maze.height,
        )
        maze_pixel_width = self.maze.width * self.tile_size
        self.offset_x = (window_width - maze_pixel_width) // 2
        self.offset_y = HUD_HEIGHT

        ghost_sprites = load_ghost_sprites(self.tile_size)
        self.ghosts: list[Ghost] = []
        for i, (corner_y, corner_x) in enumerate(self.maze.corners):
            px, py = self._cell_pixel_pos(corner_x, corner_y)
            center_x = px + self.tile_size // 2
            center_y = py + self.tile_size // 2
            self.ghosts.append(Ghost(center_x, center_y, ghost_sprites[i]))


        self.lives = config["lives"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.time_remaining = float(config["level_max_time"])
        self.score = 0  # TODO: carry over from previous level (spec 6.7)

        # TODO: place player at self.maze.spawn (convert to pixels).
    
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> Optional[ScreenName]:
        for ghost in self.ghosts:
            ghost.update(dt, self.maze, self.maze.spawn, self.tile_size, self.offset_x, self.offset_y)

    def _cell_pixel_pos(self, x: int, y: int) -> tuple[int, int]:
        """Top-left pixel coordinates of the cell at grid position (x, y)."""
        pixel_x = self.offset_x + x * self.tile_size
        pixel_y = self.offset_y + y * self.tile_size
        return pixel_x, pixel_y

    def _draw_maze(self, surface: "pygame.Surface") -> None:
        """Draw walls, collectibles, and the filled yellow '42' pattern.
    
        Isolated cells (all 4 walls closed) form the '42' logo baked into
        the maze center — fill their interior in yellow before drawing
        walls on top, so the walls still read as a border around them.
        """
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                px, py = self._cell_pixel_pos(x, y)
                size = self.tile_size

                if cell.north:
                    pygame.draw.rect(
                        surface, COLOR_WALL,
                        (px, py, size, WALL_THICKNESS),
                    )
                if cell.south:
                    pygame.draw.rect(
                        surface, COLOR_WALL,
                        (px, py + size - WALL_THICKNESS, size, WALL_THICKNESS),
                    )
                if cell.west:
                    pygame.draw.rect(
                        surface, COLOR_WALL,
                        (px, py, WALL_THICKNESS, size),
                    )
                if cell.east:
                    pygame.draw.rect(
                        surface, COLOR_WALL,
                        (px + size - WALL_THICKNESS, py, WALL_THICKNESS, size),
                    )
                if cell.is_isolated:
                    pygame.draw.rect(
                        surface, COLOR_42_PATTERN, (px, py, size, size)
                    )

                # Collectibles — isolated cells have no gum (spec: '42'
                # pattern cells are excluded from pacgum placement), but
                # guard anyway in case that assumption changes.
                if not cell.is_isolated:
                    center = (px + size // 2, py + size // 2)
                    if cell.has_pacgum:
                        pygame.draw.circle(
                            surface, COLOR_PACGUM, center, PACGUM_RADIUS
                        )
                    elif cell.has_super_pacgum:
                        pygame.draw.circle(
                            surface, COLOR_SUPER_PACGUM, center,
                            SUPER_PACGUM_RADIUS,
                        )

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BACKGROUND)
        self._draw_maze(surface)
        draw_ghosts(surface, self.ghosts)
        # TODO: draw player, HUD.
