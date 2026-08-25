"""Playing screen (spec 6.1-6.4, 6.6-6.8).

Renders the maze, player, ghosts, and HUD; drives gameplay updates each
frame; detects pause/game-over/victory transitions.
"""
from typing import Optional

import pygame

from ui.screens.base import Screen, ScreenName
from ui.draw_ghosts import load_ghost_sprites, draw_ghosts
from game.ghost import Ghost
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

# --- TEMPORARY: Lot A hasn't shipped pacgum placement yet, so every
# maze loads with zero gums. This flag lets us fake "1 gum remaining"
# and clear it on a debug key, to validate level-to-level progression
# in isolation. REMOVE once real gum placement is in place. ---
DEBUG_FAKE_GUM_KEY = pygame.K_n
DEBUG_KILL_GHOSTS_KEY = pygame.K_k

LEVEL_TRANSITION_DURATION = 12.0  # seconds; temporary, tune as needed
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

        # TEMPORARY: see DEBUG_FAKE_GUM_KEY above.
        self._debug_gum_emptied = False

        # TODO(Lot A): player object/position, hooked in once available.

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

        ghost_sprites, vulnerable_sprite = load_ghost_sprites(self.tile_size)
        self.ghosts: list[Ghost] = []
        for i, (corner_y, corner_x) in enumerate(self.maze.corners):
            px, py = self._cell_pixel_pos(corner_x, corner_y)
            center_x = px + self.tile_size // 2
            center_y = py + self.tile_size // 2
            self.ghosts.append(
                Ghost(center_x, center_y, ghost_sprites[i], vulnerable_sprite)
            )

        self.time_remaining = float(self.config["level_max_time"])
        self._debug_gum_emptied = False  # TEMPORARY, see top of file

        # TODO(Lot A): reposition the player at self.maze.spawn here too.

    def _load_next_level(self) -> None:
        """Advance to the next level, keeping score and lives."""
        self._setup_level(self.level_index + 1)

    def _count_remaining_gums(self) -> int:
        """Count pacgums and super-pacgums still present in the maze.

        TEMPORARY: real gum placement isn't shipped yet (Lot A), so
        every maze currently loads with zero gums (see Cell.__init__).
        Fake a single remaining gum, clearable via DEBUG_FAKE_GUM_KEY,
        so level-to-level progression can be tested in isolation.
        Remove this override once real placement lands — the real
        counting logic below already works as-is.

        Returns:
            The number of cells whose content is not EMPTY.
        """
        real_count = 0
        for row in self.maze.grid:
            for cell in row:
                if cell.has_gum:
                    real_count += 1

        if real_count == 0:
            return 0 if self._debug_gum_emptied else 1

        return real_count

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

    # --- Screen interface ---------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle the pause key (and later, cheat-mode hotkeys)."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self._pause_requested = True
            elif event.key == DEBUG_FAKE_GUM_KEY:
                # TEMPORARY: simulate eating the last gum for testing.
                self._debug_gum_emptied = True
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
        # TODO(Lot A/B): movement key handling for the player.
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

        # Ghosts currently target the maze's spawn cell as a placeholder
        # until the player's position is available from Lot A.
        for ghost in self.ghosts:
            ghost.update(
                dt,
                self.maze,
                self.maze.spawn,  # TODO: replace with player's cell
                self.tile_size,
                self.offset_x,
                self.offset_y,
            )

        self.time_remaining -= dt
        # TODO: handle time_remaining <= 0 (restart level? end game? —
        # spec 6.7, behavior is your choice).

        # TODO(Lot A/B): player movement, player/ghost collisions,
        # gum eating and score increment — see "État de jeu partagé" in
        # the cahier des charges.

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
        draw_ghosts(surface, self.ghosts)
        # TODO(Lot A/B): draw player.
        # TODO: draw HUD (score, lives, level, time_remaining) — spec 6.8.

        if self.transition_timer is not None:
            self._draw_transition_message(surface)

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
