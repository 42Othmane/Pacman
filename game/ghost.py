"""Ghost entity (spec 6.3).

Movement: greedy waypoint-following through the maze grid, always
picking the open neighboring cell closest to the target cell. This is
not optimal pathfinding (no backtracking out of dead ends), but keeps
things simple as intended for a shared ghost behavior.

Placeholder rendering: a plain colored square, to be replaced with a
sprite later (see playing_screen.py's _draw_ghosts).
"""
from typing import Optional

# (dy, dx) offset for each maze direction, matching Cell.is_open()'s
# convention (grid[y][x], "N"/"E"/"S"/"W").
_DIRECTION_DELTAS: dict[str, tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
}

SPEED_TILES_PER_SECOND = 3.0
ARRIVAL_EPSILON = 1.0  # pixels; below this, snap to the waypoint


class Ghost:
    """A single ghost. Position is stored as its pixel center."""

    def __init__(self, x: float, y: float) -> None:
        """Initialize a ghost at the given pixel position.

        Args:
            x: Center x position, in pixels.
            y: Center y position, in pixels.
        """
        self.x = x
        self.y = y
        self.waypoint: Optional[tuple[float, float]] = None
        # Cell the ghost is currently leaving, excluded from candidates
        # in _choose_next_waypoint to prevent back-and-forth oscillation.
        self.previous_cell: Optional[tuple[int, int]] = None
        # TODO: direction, is_edible, is_eaten/respawn timer (spec 6.3).

    def _pixel_to_cell(
        self, tile_size: int, offset_x: int, offset_y: int
    ) -> tuple[int, int]:
        """Return the (cell_x, cell_y) the ghost currently occupies."""
        cell_x = int((self.x - offset_x) // tile_size)
        cell_y = int((self.y - offset_y) // tile_size)
        return cell_x, cell_y

    @staticmethod
    def _cell_center_pixel(
        cell_x: int, cell_y: int, tile_size: int, offset_x: int, offset_y: int
    ) -> tuple[float, float]:
        """Return the pixel center of the given (cell_x, cell_y)."""
        px = offset_x + cell_x * tile_size + tile_size / 2
        py = offset_y + cell_y * tile_size + tile_size / 2
        return px, py

    def _choose_next_waypoint(
        self,
        maze: object,
        target_cell: tuple[int, int],
        tile_size: int,
        offset_x: int,
        offset_y: int,
    ) -> tuple[float, float]:
        """Pick the open neighboring cell closest to the target cell.

        Args:
            maze: The Maze object (grid[y][x], cell_at(y, x)).
            target_cell: The (y, x) cell to move toward.
            tile_size: Current tile size in pixels.
            offset_x: Maze horizontal pixel offset.
            offset_y: Maze vertical pixel offset (HUD band).

        Returns:
            The pixel center of the chosen next cell. Falls back to
            the ghost's current position if no open neighbor exists
            (should not normally happen in a valid maze).
        """
        cell_x, cell_y = self._pixel_to_cell(tile_size, offset_x, offset_y)
        current_cell = maze.cell_at(cell_y, cell_x)

        target_y, target_x = target_cell

        if current_cell is None:
            return (self.x, self.y)

        # Gather all open, in-bounds neighbors, remembering which one
        # (if any) corresponds to previous_cell so we can exclude it
        # unless it turns out to be the only option (dead end).
        candidates: list[tuple[int, int]] = []
        for direction, (dy, dx) in _DIRECTION_DELTAS.items():
            if not current_cell.is_open(direction):
                continue

            neighbor_x = cell_x + dx
            neighbor_y = cell_y + dy
            if maze.cell_at(neighbor_y, neighbor_x) is None:
                continue

            candidates.append((neighbor_x, neighbor_y))

        non_backtrack = [c for c in candidates if c != self.previous_cell]
        # Only allow going back where we came from if it's the sole exit
        # (dead end) — otherwise it would just bounce back and forth.
        usable_candidates = non_backtrack if non_backtrack else candidates

        best_pixel = (self.x, self.y)
        best_distance = float("inf")
        best_cell: Optional[tuple[int, int]] = None

        for neighbor_x, neighbor_y in usable_candidates:
            distance = abs(neighbor_y - target_y) + abs(neighbor_x - target_x)
            if distance < best_distance:
                best_distance = distance
                best_cell = (neighbor_x, neighbor_y)
                best_pixel = self._cell_center_pixel(
                    neighbor_x, neighbor_y, tile_size, offset_x, offset_y
                )

        # We're committing to leave (cell_x, cell_y) now, so it becomes
        # the "previous cell" to avoid immediately reversing into it.
        if best_cell is not None:
            self.previous_cell = (cell_x, cell_y)

        return best_pixel

    def update(
        self,
        dt: float,
        maze: object,
        target_cell: tuple[int, int],
        tile_size: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Advance the ghost by one frame toward target_cell.

        Args:
            dt: Time elapsed since the last frame, in seconds.
            maze: The Maze object.
            target_cell: The (y, x) cell the ghost moves toward.
            tile_size: Current tile size in pixels.
            offset_x: Maze horizontal pixel offset.
            offset_y: Maze vertical pixel offset (HUD band).
        """
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
