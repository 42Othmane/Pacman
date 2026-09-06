"""Ghost entity (spec 6.3).

Movement: greedy waypoint-following through the maze grid, always
picking the open neighboring cell closest (or farthest, when fleeing)
to the target cell. This is not optimal pathfinding (no backtracking
out of dead ends), but keeps things simple as intended for a shared
ghost behavior.
"""
from typing import Optional, Tuple, Dict, List

import pygame

# (dy, dx) offset for each maze direction, matching Cell.is_open()'s
# convention (grid[y][x], "N"/"E"/"S"/"W").
_DIRECTION_DELTAS: Dict[str, Tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
}

SPEED_TILES_PER_SECOND = 3.0
ARRIVAL_EPSILON = 1.0  # pixels; below this, snap to the waypoint
RESPAWN_DELAY = 5.0  # seconds before an eaten ghost respawns


class Ghost:
    """A single ghost. Position is stored as its pixel center."""

    def __init__(
        self,
        x: float,
        y: float,
        normal_sprite: "pygame.Surface",
        vulnerable_sprite: "pygame.Surface",
    ) -> None:
        """Initialize a ghost at the given pixel position.

        Args:
            x: Center x position, in pixels. Also stored as the ghost's
                respawn point (ghosts start at their corner, spec 6.1).
            y: Center y position, in pixels. Also stored as the respawn
                point.
            normal_sprite: Pre-loaded, pre-scaled sprite used while the
                ghost is neither edible nor eaten.
            vulnerable_sprite: Pre-loaded, pre-scaled sprite used while
                the ghost is edible (after a super-pacgum).
        """
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y

        self.normal_sprite = normal_sprite
        self.vulnerable_sprite = vulnerable_sprite

        self.waypoint: Optional[Tuple[float, float]] = None
        # Cell the ghost is currently leaving, excluded from candidates
        # in _choose_next_waypoint to prevent back-and-forth oscillation.
        self.previous_cell: Optional[Tuple[int, int]] = None

        self.is_edible: bool = False
        self.is_eaten: bool = False
        self.respawn_timer: Optional[float] = None

    @property
    def sprite(self) -> "pygame.Surface":
        """Return the sprite to draw for the ghost's current state.

        Eaten ghosts are handled by the caller (draw_ghosts skips them
        entirely), but this still returns a sensible surface if drawn.
        """
        return self.vulnerable_sprite if self.is_edible else self.normal_sprite

    def get_eaten(self) -> None:
        """Mark this ghost as eaten: hide it and start its respawn timer.

        Called by PlayingScreen when the player touches this ghost
        while it is edible.
        """
        self.is_eaten = True
        self.is_edible = False
        self.respawn_timer = RESPAWN_DELAY
        self.waypoint = None
        self.previous_cell = None

    def _respawn(self) -> None:
        """Reset the ghost to its corner spawn point, alive again."""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.is_eaten = False
        self.respawn_timer = None
        self.waypoint = None
        self.previous_cell = None

    def reset_to_spawn(self) -> None:
        """Send the ghost back to its corner, clearing its current path.

        Used by PlayingScreen when the player dies. Clearing waypoint
        and previous_cell is not optional: the ghost interpolates
        toward waypoint in a straight line without re-checking walls,
        so a stale waypoint left over from before the teleport would
        make it glide across the maze through the walls.

        Eaten/edible flags are left untouched — this is a repositioning,
        not a respawn.
        """
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.waypoint = None
        self.previous_cell = None

    def _pixel_to_cell(
        self, tile_size: int, offset_x: int, offset_y: int
    ) -> Tuple[int, int]:
        """Return the (cell_x, cell_y) the ghost currently occupies."""
        cell_x = int((self.x - offset_x) // tile_size)
        cell_y = int((self.y - offset_y) // tile_size)
        return cell_x, cell_y

    @staticmethod
    def _cell_center_pixel(
        cell_x: int,
        cell_y: int,
        tile_size: int,
        offset_x: int,
        offset_y: int
    ) -> Tuple[float, float]:
        """Return the pixel center of the given (cell_x, cell_y)."""
        px = offset_x + cell_x * tile_size + tile_size / 2
        py = offset_y + cell_y * tile_size + tile_size / 2
        return px, py

    def _choose_next_waypoint(
        self,
        maze: object,
        target_cell: Tuple[int, int],
        tile_size: int,
        offset_x: int,
        offset_y: int,
    ) -> Tuple[float, float]:
        """Pick the open neighboring cell closest (or farthest, if edible).

        Args:
            maze: The Maze object (grid[y][x], cell_at(y, x)).
            target_cell: The (y, x) cell to move toward (or away from).
            tile_size: Current tile size in pixels.
            offset_x: Maze horizontal pixel offset.
            offset_y: Maze vertical pixel offset (HUD band).

        Returns:
            The pixel center of the chosen next cell. Falls back to
            the ghost's current position if no open neighbor exists
            (should not normally happen in a valid maze).
        """
        cell_x, cell_y = self._pixel_to_cell(tile_size, offset_x, offset_y)
        current_cell = maze.cell_at(cell_y, cell_x)  # type: ignore

        target_y, target_x = target_cell

        if current_cell is None:
            return (self.x, self.y)

        candidates: List[Tuple[int, int]] = []
        for direction, (dy, dx) in _DIRECTION_DELTAS.items():
            if not current_cell.is_open(direction):
                continue

            neighbor_x = cell_x + dx
            neighbor_y = cell_y + dy
            if maze.cell_at(neighbor_y, neighbor_x) is None:  # type: ignore
                continue

            candidates.append((neighbor_x, neighbor_y))

        non_backtrack = [c for c in candidates if c != self.previous_cell]
        usable_candidates = non_backtrack if non_backtrack else candidates

        best_pixel = (self.x, self.y)
        best_cell: Optional[Tuple[int, int]] = None
        # When fleeing (edible), we want the FARTHEST neighbor, so start
        # from -inf; when chasing, we want the CLOSEST, so start from
        # +inf. Getting this initial value wrong silently breaks the
        # comparison below (nothing ever looks "better").
        best_distance = float("-inf") if self.is_edible else float("inf")

        for neighbor_x, neighbor_y in usable_candidates:
            distance = abs(neighbor_y - target_y) + abs(neighbor_x - target_x)
            is_better = (
                distance > best_distance
                if self.is_edible
                else distance < best_distance
            )
            if is_better:
                best_distance = distance
                best_cell = (neighbor_x, neighbor_y)
                best_pixel = self._cell_center_pixel(
                    neighbor_x, neighbor_y, tile_size, offset_x, offset_y
                )

        if best_cell is not None:
            self.previous_cell = (cell_x, cell_y)

        return best_pixel

    def update(
        self,
        dt: float,
        maze: object,
        target_cell: Tuple[int, int],
        tile_size: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Advance the ghost by one frame.

        While eaten, movement is skipped entirely and only the respawn
        timer ticks down; once it reaches zero the ghost reappears at
        its corner spawn point, alive and no longer edible.

        Args:
            dt: Time elapsed since the last frame, in seconds.
            maze: The Maze object.
            target_cell: The (y, x) cell the ghost moves toward (or
                flees from, if edible).
            tile_size: Current tile size in pixels.
            offset_x: Maze horizontal pixel offset.
            offset_y: Maze vertical pixel offset (HUD band).
        """
        if self.is_eaten:
            if self.respawn_timer is not None:
                self.respawn_timer -= dt
                if self.respawn_timer <= 0:
                    self._respawn()
            return

        if self.waypoint is None:
            self.waypoint = self._choose_next_waypoint(
                maze, target_cell, tile_size, offset_x, offset_y
            )

        target_x, target_y = self.waypoint
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= ARRIVAL_EPSILON:
            self.x, self.y = target_x, target_y
            self.waypoint = None
            return

        speed = tile_size * SPEED_TILES_PER_SECOND
        step = speed * dt

        if step >= distance:
            self.x, self.y = target_x, target_y
            self.waypoint = None
        else:
            self.x += dx / distance * step
            self.y += dy / distance * step
