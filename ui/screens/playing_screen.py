"""Playing screen (spec 6.1-6.4, 6.6-6.8).

Renders the maze, player, ghosts, and HUD; drives gameplay updates each
frame; detects pause/game-over/victory transitions.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName
from ui.draw_ghosts import load_ghost_sprites, draw_ghosts
from ui.draw_player import load_player_frames, FRAME_COUNT
from game.ghost import Ghost
from game.collectables import CollectibleManager
from game.player import Player
from maze.cell import PACGUM, SUPER_PACGUM
from maze.loader import load_maze

# --- Colors (classic Pac-Man palette) ---
COLOR_BACKGROUND = (0, 0, 0)
COLOR_WALL = (33, 33, 222)
COLOR_PACGUM = (255, 222, 173)
COLOR_SUPER_PACGUM = (255, 222, 173)
COLOR_42_PATTERN = (255, 255, 0)

WALL_THICKNESS = 1
PACGUM_RADIUS = 3
SUPER_PACGUM_RADIUS = 8

HUD_HEIGHT = 60  # reserved band at the top for score/lives/level/timer

DEBUG_KILL_GHOSTS_KEY = pygame.K_k

# --- Player (Lot A) ---
COLOR_PLAYER = (255, 255, 0)

# Seconds between two cell steps. 0.25 -> 4 cells/second, slightly
# faster than the ghosts (SPEED_TILES_PER_SECOND = 3.0).
PLAYER_MOVE_INTERVAL = 0.25

# Mouth animation: full open/close cycle per cell step, so the chomp
# lines up with the movement.
PLAYER_ANIMATION_FPS = FRAME_COUNT * 2

# Arrow keys and ZQSD/WASD, mapped to Cell.is_open() directions.
MOVEMENT_KEYS: dict[int, str] = {
    pygame.K_UP: "N", pygame.K_DOWN: "S",
    pygame.K_RIGHT: "E", pygame.K_LEFT: "W",
    pygame.K_z: "N", pygame.K_w: "N",
    pygame.K_s: "S",
    pygame.K_d: "E",
    pygame.K_q: "W", pygame.K_a: "W",
}

LEVEL_TRANSITION_DURATION = 2.0  # seconds; temporary, tune as needed
COLOR_TRANSITION_TEXT = (255, 255, 0)
FONT_SIZE_TRANSITION = 48


class PlayingScreen(Screen):
    """Active gameplay: maze, player, ghosts, HUD."""

    def __init__(
        self,
        config: dict,
        level_index: int,
        window_width: int,
        window_height: int,
    ) -> None:
        """Initialize gameplay state for a new game, starting at a level.

        Args:
            config: Full parsed game config (see config.example.json).
            level_index: 0-based index into config["levels"] to start on.
            window_width: Window width in pixels.
            window_height: Window height in pixels.
        """
        self.config = config
        self.window_width = window_width
        self.window_height = window_height

        # Persist across levels (spec 6.7) — only set here, never in
        # _setup_level(), so they survive level transitions.
        self.lives = config["lives"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.score = 0

        self._setup_level(level_index)

        self.transition_timer: Optional[float] = None
        self.font_transition = pygame.font.Font(None, FONT_SIZE_TRANSITION)

        # Accumulates dt until a full PLAYER_MOVE_INTERVAL has elapsed,
        # at which point the player advances by one cell.
        self.move_timer = 0.0

    # --- Level setup / progression ---------------------------------

    def _setup_level(self, level_index: int) -> None:
        """Load and configure everything specific to a single level.

        Called once from __init__ for the first level, and again from
        _load_next_level() when the player clears a level. Score and
        lives are untouched here — they persist across levels.

        Args:
            level_index: 0-based index into self.config["levels"].
        """
        self.level_index = level_index
        level_spec = self.config["levels"][level_index]

        # Spec 6.1: level 1 uses the fixed seed, later levels are random.
        seed = self.config["seed"] if level_index == 0 else 0

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
        playable_height = self.window_height - HUD_HEIGHT
        self.tile_size = min(
            self.window_width // self.maze.width,
            playable_height // self.maze.height,
        )
        maze_pixel_width = self.maze.width * self.tile_size
        self.offset_x = (self.window_width - maze_pixel_width) // 2
        self.offset_y = HUD_HEIGHT

        # Depends on tile_size, so it must be reloaded every level.
        self.player_frames = load_player_frames(self.tile_size)
        print(self.player_frames)
        self.animation_timer = 0.0

        ghost_sprites, vulnerable_sprite = load_ghost_sprites(self.tile_size)
        self.ghosts: list[Ghost] = []
        for i, (corner_y, corner_x) in enumerate(self.maze.corners):
            px, py = self._cell_pixel_pos(corner_x, corner_y)
            center_x = px + self.tile_size // 2
            center_y = py + self.tile_size // 2
            self.ghosts.append(
                Ghost(center_x, center_y, ghost_sprites[i], vulnerable_sprite)
            )

        # Lot A owns gum placement and the player; the screen only
        # renders them and forwards input.
        self.collectibles = CollectibleManager(
            self.maze, self.config["pacgum"]
        )
        self.player = Player(self.maze, self.lives)
        self.move_timer = 0.0

        self.time_remaining = float(self.config["level_max_time"])

    def _load_next_level(self) -> None:
        """Advance to the next level, keeping score and lives."""
        self._setup_level(self.level_index + 1)

    def _count_remaining_gums(self) -> int:
        """Return how many pacgums and super-pacgums are still uneaten.

        Returns:
            The number of collectibles left in the current level.
        """
        return (
            self.collectibles.total_pacgums
            - self.collectibles.pacgums_eaten
        )

    # --- Coordinate helpers ------------------------------------------

    def _cell_pixel_pos(self, x: int, y: int) -> tuple[int, int]:
        """Top-left pixel coordinates of the cell at grid position (x, y).

        Args:
            x: Column index in the maze grid.
            y: Row index in the maze grid.

        Returns:
            (pixel_x, pixel_y) of the cell's top-left corner.
        """
        pixel_x = self.offset_x + x * self.tile_size
        pixel_y = self.offset_y + y * self.tile_size
        return pixel_x, pixel_y

    # --- Player ------------------------------------------------------

    def _update_player(self, dt: float) -> None:
        """Advance the player and apply what it walks over.

        The player owns a discrete cell position; move_progress only
        drives the rendering interpolation. A while loop is used rather
        than an if so a long frame catches up instead of dropping steps.

        Args:
            dt: Time elapsed since the last frame, in seconds.
        """
        self.player.tick(dt, 1.0 / PLAYER_MOVE_INTERVAL)
        self.animation_timer += dt

        self.move_timer += dt
        while self.move_timer >= PLAYER_MOVE_INTERVAL:
            self.move_timer -= PLAYER_MOVE_INTERVAL
            if not self.player.step():
                break
            self._eat_at_player()

    def _eat_at_player(self) -> None:
        """Consume the collectible under the player, if any."""
        eaten = self.collectibles.eat(*self.player.position)
        if eaten == PACGUM:
            self.score += self.points_per_pacgum
        elif eaten == SUPER_PACGUM:
            self.score += self.points_per_super_pacgum
            # TODO(Lot B): make ghosts edible for a while (spec 6.4).

    # --- Screen interface ---------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle the pause key (and later, cheat-mode hotkeys)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self._pause_requested = True
            elif event.key in MOVEMENT_KEYS:
                # Lot A's Player keeps the request until the passage
                # opens up, so turns can be buffered before a junction.
                self.player.request_direction(MOVEMENT_KEYS[event.key])
            elif event.key == DEBUG_KILL_GHOSTS_KEY:
                # TEMPORARY: simulate the player eating every ghost,
                # standing in for real player/ghost collision detection
                # (Lot A/B dependency) until the player exists.
                for ghost in self.ghosts:
                    if not ghost.is_eaten:
                        ghost.get_eaten()
            elif event.key == pygame.K_r:
                for ghost in self.ghosts:
                    ghost.is_edible = not ghost.is_edible
            if event.key == pygame.K_n:
                self.transition_timer = LEVEL_TRANSITION_DURATION
        # TODO: cheat mode hotkeys (spec 6.5).

    def update(self, dt: float) -> Optional[ScreenName]:
        """Advance ghosts/timer; detect pause/game-over/victory.

        Args:
            dt: Time elapsed since the last frame, in seconds.

        Returns:
            The next ScreenName to transition to, or None to stay here.
        """
        if getattr(self, "_pause_requested", False):
            self._pause_requested = False
            return ScreenName.PAUSED

        # If a level-complete transition is active, only tick it down —
        # freeze gameplay (ghosts, timer) until it finishes.
        if self.transition_timer is not None:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.transition_timer = None
                is_last_level = (
                    self.level_index >= len(self.config["levels"]) - 1
                )
                if is_last_level:
                    return ScreenName.VICTORY
                self._load_next_level()
            return None

        self._update_player(dt)

        for ghost in self.ghosts:
            ghost.update(
                dt,
                self.maze,
                self.player.position,
                self.tile_size,
                self.offset_x,
                self.offset_y,
            )

        self.time_remaining -= dt
        # TODO: handle time_remaining <= 0 (restart level? end game? —
        # spec 6.7, behavior is your choice).

        # TODO(Lot A/B): player/ghost collisions — needs a shared cell
        # accessor on Ghost, see "État de jeu partagé" in the cahier
        # des charges.

        if self.lives <= 0:
            return ScreenName.GAME_OVER

        if self._count_remaining_gums() == 0:
            # Start the transition instead of switching immediately —
            # _load_next_level()/VICTORY only happen once the timer
            # above runs out.
            self.transition_timer = LEVEL_TRANSITION_DURATION

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the maze, ghosts, and (eventually) player and HUD."""
        surface.fill(COLOR_BACKGROUND)
        self._draw_maze(surface)
        self._draw_player(surface)
        draw_ghosts(surface, self.ghosts)
        # TODO: draw HUD (score, lives, level, time_remaining) — spec 6.8.

        if self.transition_timer is not None:
            self._draw_transition_message(surface)

    def _draw_player(self, surface: pygame.Surface) -> None:
        """Draw the player, interpolated between its two cells.

        Lot A stores the player on a whole cell; move_progress (0.0 to
        1.0) says how far along the current step it is, which is what
        makes the movement look continuous. The sprite is picked from
        the pre-rotated frames for the current direction, falling back
        to a plain circle if the sheet failed to load.

        Args:
            surface: The pygame surface to draw on.
        """
        player = self.player
        progress = player.move_progress
        cell_y = player.prev_y * (1.0 - progress) + player.y * progress
        cell_x = player.prev_x * (1.0 - progress) + player.x * progress

        center_x = int(
            self.offset_x + cell_x * self.tile_size + self.tile_size / 2
        )
        center_y = int(
            self.offset_y + cell_y * self.tile_size + self.tile_size / 2
        )
        if self.player_frames is None:
            radius = max(2, self.tile_size // 2 - 2)
            pygame.draw.circle(
                surface, COLOR_PLAYER, (center_x, center_y), radius
            )
            return

        # Freeze on the closed-mouth frame while standing still.
        if self.player.move_progress >= 1.0:
            frame_index = 0
        else:
            frame_index = int(
                self.animation_timer * PLAYER_ANIMATION_FPS
            ) % FRAME_COUNT

        sprite = self.player_frames[self.player.direction][frame_index]
        surface.blit(sprite, sprite.get_rect(center=(center_x, center_y)))

    def _draw_transition_message(self, surface: pygame.Surface) -> None:
        """Draw the 'Level Complete' message during a level transition.

        Args:
            surface: The pygame surface to draw on.
        """
        text = f"Level {self.level_index + 1} Complete!"
        text_surf = self.font_transition.render(
            text, True, COLOR_TRANSITION_TEXT
        )
        text_rect = text_surf.get_rect(
            center=(surface.get_width() // 2, surface.get_height() // 2)
        )
        surface.blit(text_surf, text_rect)

    def _draw_maze(self, surface: pygame.Surface) -> None:
        """Draw all walls, the '42' pattern, and collectibles.

        Args:
            surface: The pygame surface to draw on.
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
