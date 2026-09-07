"""Playing screen (spec 6.1-6.8).

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

COLOR_BACKGROUND = (0, 0, 0)
COLOR_WALL = (33, 33, 222)
COLOR_PACGUM = (255, 222, 173)
COLOR_SUPER_PACGUM = (255, 222, 173)
COLOR_42_PATTERN = (40, 43, 48)

WALL_THICKNESS = 1

PACGUM_RADIUS_RATIO = 0.10
SUPER_PACGUM_RADIUS_RATIO = 0.28
PACGUM_MIN_RADIUS = 1
SUPER_PACGUM_MIN_RADIUS = 3

HUD_HEIGHT = 60

FONT_SIZE_HUD = 24
FONT_SIZE_CHEAT = 18
HUD_PADDING_X = 16
HUD_LINE_1_Y = 10
HUD_LINE_2_Y = 36
COLOR_HUD_TEXT = (255, 255, 255)
COLOR_HUD_WARNING = (255, 80, 80)
COLOR_CHEAT_TEXT = (255, 140, 0)
TIMER_WARNING_SECONDS = 10.0

DEBUG_KILL_GHOSTS_KEY = pygame.K_k

COLOR_PLAYER = (255, 255, 0)

PLAYER_MOVE_INTERVAL = 0.25
CHEAT_MOVE_INTERVAL = 0.10
RESPAWN_INVINCIBILITY = 2.0
SUPER_PACGUM_DURATION = 8.0
PLAYER_ANIMATION_FPS = FRAME_COUNT * 2

MOVEMENT_KEYS: dict[int, str] = {
    pygame.K_UP: "N", pygame.K_DOWN: "S",
    pygame.K_RIGHT: "E", pygame.K_LEFT: "W",
    pygame.K_z: "N", pygame.K_w: "N",
    pygame.K_s: "S",
    pygame.K_d: "E",
    pygame.K_q: "W", pygame.K_a: "W",
}

CHEAT_INVINCIBLE_KEY = pygame.K_F1
CHEAT_SKIP_LEVEL_KEY = pygame.K_F2
CHEAT_FREEZE_GHOSTS_KEY = pygame.K_F3
CHEAT_ADD_LIFE_KEY = pygame.K_F4
CHEAT_SPEED_KEY = pygame.K_F5

LEVEL_TRANSITION_DURATION = 2.0
COLOR_TRANSITION_TEXT = (255, 255, 255)
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

        self.starting_lives = config["lives"]
        self.points_per_pacgum = config["points_per_pacgum"]
        self.points_per_super_pacgum = config["points_per_super_pacgum"]
        self.points_per_ghost = config["points_per_ghost"]
        self.score = 0

        self.super_pacgum_duration = float(
            config.get("super_pacgum_duration", SUPER_PACGUM_DURATION)
        )
        self.edible_timer = 0.0
        self.ghost_chain = 0

        self.cheat_invincible = False
        self.cheat_freeze_ghosts = False
        self.cheat_speed = False

        self.invincible_timer = 0.0

        self.move_interval = PLAYER_MOVE_INTERVAL

        self._setup_level(level_index)

        self.transition_timer: Optional[float] = None
        self.font_transition = pygame.font.Font(None, FONT_SIZE_TRANSITION)
        self.font_hud = pygame.font.Font(None, FONT_SIZE_HUD)
        self.font_cheat = pygame.font.Font(None, FONT_SIZE_CHEAT)

        self.move_timer = 0.0

    @property
    def lives(self) -> int:
        """Remaining lives, read from the Player (single source)."""
        return self.player.lives

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

        playable_height = self.window_height - HUD_HEIGHT
        self.tile_size = min(
            self.window_width // self.maze.width,
            playable_height // self.maze.height,
        )
        maze_pixel_width = self.maze.width * self.tile_size
        self.offset_x = (self.window_width - maze_pixel_width) // 2
        self.offset_y = HUD_HEIGHT

        self.pacgum_radius = max(
            PACGUM_MIN_RADIUS, round(self.tile_size * PACGUM_RADIUS_RATIO)
        )
        self.super_pacgum_radius = max(
            SUPER_PACGUM_MIN_RADIUS,
            round(self.tile_size * SUPER_PACGUM_RADIUS_RATIO),
        )

        self.player_frames = load_player_frames(self.tile_size)
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

        self.collectibles = CollectibleManager(
            self.maze, self.config["pacgum"]
        )
        previous_player = getattr(self, "player", None)
        self.player = Player(
            self.maze,
            previous_player.lives if previous_player else self.starting_lives,
        )
        self.move_timer = 0.0
        self.invincible_timer = 0.0
        self.edible_timer = 0.0
        self.ghost_chain = 0

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

    def _ghost_cell(self, ghost: Ghost) -> tuple[int, int]:
        """Grid cell a ghost currently occupies.

        The inverse of _cell_pixel_pos(): ghosts live in pixel space
        (they interpolate smoothly), the player lives in cell space, so
        one of the two has to be converted before they can be compared.

        Note the return order. Ghost._pixel_to_cell() returns (x, y),
        but Player.position is (y, x); this returns the Player order so
        the two can be compared with a plain ==.

        Args:
            ghost: The ghost to locate.

        Returns:
            (row, column) — the same (y, x) convention as Player.
        """
        column = int((ghost.x - self.offset_x) // self.tile_size)
        row = int((ghost.y - self.offset_y) // self.tile_size)
        return row, column

    def _update_player(self, dt: float) -> None:
        """Advance the player and apply what it walks over.

        The player owns a discrete cell position; move_progress only
        drives the rendering interpolation. A while loop is used rather
        than an if so a long frame catches up instead of dropping steps.

        Args:
            dt: Time elapsed since the last frame, in seconds.
        """
        self.player.tick(dt, 1.0 / self.move_interval)
        self.animation_timer += dt

        self.move_timer += dt
        while self.move_timer >= self.move_interval:
            self.move_timer -= self.move_interval
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
            self._start_edible_window()

    def _start_edible_window(self) -> None:
        """Make every live ghost edible for super_pacgum_duration.

        Eating a second super-pacgum restarts the window from scratch
        rather than stacking, which is the classic behaviour. The
        combo counter restarts with it.
        """
        self.edible_timer = self.super_pacgum_duration
        self.ghost_chain = 0
        for ghost in self.ghosts:
            if not ghost.is_eaten:
                ghost.is_edible = True

    def _end_edible_window(self) -> None:
        """Clear the edible state on every ghost."""
        self.edible_timer = 0.0
        self.ghost_chain = 0
        for ghost in self.ghosts:
            ghost.is_edible = False

    def _update_edible_window(self, dt: float) -> None:
        """Tick the super-pacgum window down.

        A ghost eaten during the window comes back non-edible on
        purpose: get_eaten() clears the flag and nothing restores it,
        so respawning is a genuine second chance for the ghost even if
        the window is still open.

        Args:
            dt: Time elapsed since the last frame, in seconds.
        """
        if self.edible_timer <= 0.0:
            return

        self.edible_timer -= dt
        if self.edible_timer <= 0.0:
            self._end_edible_window()

    def _request_direction(self, direction: str) -> None:
        """Forward a direction request, applying it at once if possible.

        Player.request_direction() only records the wish; it is applied
        on the next scheduled step, up to move_interval away. That
        buffering is what lets a turn be entered slightly before a
        junction, so it is kept while the player is mid-cell.

        Standing still is different: waiting up to a quarter of a
        second before reacting just feels like input lag, so the step
        is taken immediately instead.

        Args:
            direction: One of "N", "S", "E", "W".
        """
        self.player.request_direction(direction)

        if self.player.move_progress < 1.0:
            return
        if not self.player.can_move(direction):
            return

        if self.player.step():
            self._eat_at_player()
            self.move_timer = 0.0

    def _is_protected(self) -> bool:
        """True if the player currently cannot be hurt by a ghost."""
        return self.cheat_invincible or self.invincible_timer > 0.0

    def _reset_ghost_positions(self) -> None:
        """Send every live ghost back to the corner it spawned in.

        Ghosts that are currently eaten are skipped: they are already
        invisible and counting down their own respawn timer.
        """
        for ghost in self.ghosts:
            if not ghost.is_eaten:
                ghost.reset_to_spawn()

    def _lose_life(self) -> None:
        """Take one life, respawn the player, and reset the ghosts.

        Both halves matter: without the ghost reset, a ghost sitting on
        the spawn cell would eat every remaining life within a few
        frames; without the grace period, the same thing happens if a
        ghost simply reaches the spawn first.
        """
        self.player.lose_life()
        self._reset_ghost_positions()
        self._end_edible_window()
        self.invincible_timer = RESPAWN_INVINCIBILITY
        self.move_timer = 0.0

    def _check_ghost_collisions(self) -> None:
        """Resolve the player sharing a cell with a ghost.

        An edible ghost is eaten for points; a normal one costs a life.
        The method returns as soon as a life is lost, so two ghosts
        landing on the player in the same frame only cost one life.
        """
        player_cell = self.player.position
        for ghost in self.ghosts:
            if ghost.is_eaten:
                continue
            if self._ghost_cell(ghost) != player_cell:
                continue
            if ghost.is_edible:
                ghost.get_eaten()
                self.score += self.points_per_ghost * (2 ** self.ghost_chain)
                self.ghost_chain += 1
            elif not self._is_protected():
                self._lose_life()
                return

    def _handle_cheat_key(self, key: int) -> bool:
        """Apply a cheat-mode hotkey.

        Args:
            key: The pygame key constant from the KEYDOWN event.

        Returns:
            True if the key was a cheat key and was handled.
        """
        if key == CHEAT_INVINCIBLE_KEY:
            self.cheat_invincible = not self.cheat_invincible
        elif key == CHEAT_SKIP_LEVEL_KEY:
            if self.transition_timer is None:
                self.transition_timer = LEVEL_TRANSITION_DURATION
        elif key == CHEAT_FREEZE_GHOSTS_KEY:
            self.cheat_freeze_ghosts = not self.cheat_freeze_ghosts
        elif key == CHEAT_ADD_LIFE_KEY:
            self.player.lives += 1
        elif key == CHEAT_SPEED_KEY:
            self.cheat_speed = not self.cheat_speed
            self.move_interval = (
                CHEAT_MOVE_INTERVAL if self.cheat_speed
                else PLAYER_MOVE_INTERVAL
            )
        else:
            return False
        return True

    def _active_cheats(self) -> list[str]:
        """Names of the cheats currently switched on, for the HUD."""
        active = []
        if self.cheat_invincible:
            active.append("INVINCIBLE")
        if self.cheat_freeze_ghosts:
            active.append("GHOSTS FROZEN")
        if self.cheat_speed:
            active.append("SPEED")
        if active:
            active[0] = "CHEATS: " + active[0]
        return active

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pause, movement, cheat-mode and debug hotkeys."""
        if event.type != pygame.KEYDOWN:
            return

        if self._handle_cheat_key(event.key):
            return

        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
            self._pause_requested = True
        elif event.key in MOVEMENT_KEYS:
            self._request_direction(MOVEMENT_KEYS[event.key])

    def update(self, dt: float) -> Optional[ScreenName]:
        """Advance gameplay; detect pause/game-over/victory.

        Args:
            dt: Time elapsed since the last frame, in seconds.

        Returns:
            The next ScreenName to transition to, or None to stay here.
        """
        if getattr(self, "_pause_requested", False):
            self._pause_requested = False
            return ScreenName.PAUSED

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

        if self.invincible_timer > 0.0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)

        self._update_edible_window(dt)

        self._update_player(dt)

        if not self.cheat_freeze_ghosts:
            for ghost in self.ghosts:
                ghost.update(
                    dt,
                    self.maze,
                    self.player.position,
                    self.tile_size,
                    self.offset_x,
                    self.offset_y,
                )

        self._check_ghost_collisions()

        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self._lose_life()
            self.time_remaining = float(self.config["level_max_time"])

        if self.player.is_game_over():
            return ScreenName.GAME_OVER

        if self._count_remaining_gums() == 0:
            self.transition_timer = LEVEL_TRANSITION_DURATION

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the maze, player, ghosts, and HUD."""
        surface.fill(COLOR_BACKGROUND)
        self._draw_maze(surface)
        self._draw_player(surface)
        draw_ghosts(surface, self.ghosts)
        self._draw_hud(surface)

        if self.transition_timer is not None:
            self._draw_transition_message(surface)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format the remaining time as whole seconds, clamped at zero.

        Args:
            seconds: Remaining time, possibly negative on the last frame.

        Returns:
            The duration as "87s".
        """
        return f"{max(0, int(seconds))}s"

    def _draw_hud(self, surface: pygame.Surface) -> None:
        """Draw score, lives, level and remaining time in the top band.

        Args:
            surface: The pygame surface to draw on.
        """
        score_surf = self.font_hud.render(
            f"SCORE {self.score}", True, COLOR_HUD_TEXT
        )
        surface.blit(score_surf, (HUD_PADDING_X, HUD_LINE_1_Y))

        lives_surf = self.font_hud.render(
            f"LIVES {self.player.lives}", True, COLOR_HUD_TEXT
        )
        surface.blit(
            lives_surf,
            (self.window_width // 2 - lives_surf.get_width() - 20,
             HUD_LINE_1_Y),
        )

        level_surf = self.font_hud.render(
            f"LEVEL {self.level_index + 1}", True, COLOR_HUD_TEXT
        )
        surface.blit(
            level_surf, (self.window_width // 2 + 20, HUD_LINE_1_Y)
        )

        time_color = (
            COLOR_HUD_WARNING
            if self.time_remaining <= TIMER_WARNING_SECONDS
            else COLOR_HUD_TEXT
        )
        time_surf = self.font_hud.render(
            f"TIME {self._format_time(self.time_remaining)}", True, time_color
        )
        surface.blit(
            time_surf,
            (self.window_width - time_surf.get_width() - HUD_PADDING_X,
             HUD_LINE_1_Y),
        )

        labels = []
        if self.edible_timer > 0.0:
            labels.append(f"EDIBLE {self.edible_timer:.1f}s")
        labels.extend(self._active_cheats())
        if self.invincible_timer > 0.0:
            labels.append(f"RESPAWN {self.invincible_timer:.1f}s")
        if labels:
            cheat_surf = self.font_cheat.render(
                " | ".join(labels), True, COLOR_CHEAT_TEXT
            )
            surface.blit(cheat_surf, (HUD_PADDING_X, HUD_LINE_2_Y))

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
        if self.invincible_timer > 0.0 and int(
            self.invincible_timer * 8
        ) % 2 == 0:
            return

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

        if self.player.move_progress >= 1.0:
            frame_index = 0
        else:
            frame_index = int(
                self.animation_timer * PLAYER_ANIMATION_FPS
            ) % FRAME_COUNT

        sprite = self.player_frames[self.player.direction][frame_index]
        surface.blit(sprite, sprite.get_rect(center=(center_x, center_y)))

    def _draw_transition_message(self, surface: pygame.Surface) -> None:
        """Draw the 'Level Complete' message with a semi-opacity background.

        Args:
            surface: The pygame surface to draw on.
        """
        width = surface.get_width()
        height = surface.get_height()

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        text = f"Level {self.level_index + 1} Complete !"
        text_surf = self.font_transition.render(
            text, True, COLOR_TRANSITION_TEXT
        )
        text_rect = text_surf.get_rect(
            center=(width // 2, height // 2)
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
                            surface, COLOR_PACGUM, center,
                            self.pacgum_radius,
                        )
                    elif cell.has_super_pacgum:
                        pygame.draw.circle(
                            surface, COLOR_SUPER_PACGUM, center,
                            self.super_pacgum_radius,
                        )
