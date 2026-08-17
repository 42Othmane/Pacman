import random


class CollectibleManager:
    def __init__(self, maze_grid: list, pacgum_count: int):
        """
        maze_grid: La grille du labyrinthe (0 = couloir, 1 = mur)
        pacgum_count: Le nombre de pacgums à placer (vient de la config)
        """
        self.grid = [[0 for _ in range(len(maze_grid[0]))] for _ in range(len(maze_grid))]  # La grille d'état des collectibles
        self.total_pacgums = 0
        self.pacgums_eaten = 0

        h = len(maze_grid)  # Hauteur (Y)
        w = len(maze_grid[0]) # Largeur (X)

        self.grid[0][0] = 2               # Haut Gauche
        self.grid[0][w - 1] = 2           # Haut Droite
        self.grid[h - 1][0] = 2           # Bas Gauche
        self.grid[h - 1][w - 1] = 2       # Bas Droite

        empty_cells = []
        for y in range(h):
            for x in range(w):
                if self.grid[y][x] == 0:
                    empty_cells.append((y, x))

        count_to_place = min(pacgum_count, len(empty_cells))
        chosen_cells = random.sample(empty_cells, count_to_place)

        for y, x in chosen_cells:
            self.grid[y][x] = 1

        self.total_pacgums = count_to_place + 4

    def eat(self, row: int, col: int) -> int | None:
        """
        Le joueur essaie de manger la case (row, col).
        Retourne 1 si c'était un pacgum, 2 si c'était un super-pacgum, None si rien.
        Met à jour la grille et le compteur.
        """
        if self.grid[row][col] == 1:
            self.grid[row][col] = None
            self.pacgums_eaten += 1
            return 1
        elif self.grid[row][col] == 2:
            self.grid[row][col] = None
            self.pacgums_eaten += 1
            return 2
        else:
            return None


    def are_all_eaten(self) -> bool:
        """
        Retourne True si tous les pacgums et super-pacgums ont été mangés.
        """
        return self.pacgums_eaten == self.total_pacgums
