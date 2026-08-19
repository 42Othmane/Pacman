from mazegenerator import MazeGenerator
import random
import sys

def translate_maze(maze_gen: MazeGenerator) -> list:
    raw_maze =  maze_gen.maze

    h = len(raw_maze)
    w = len(raw_maze[0])

    simple_grid = []

    for y in range(h):
        row = []
        for x in range(w):
            cell_value = raw_maze[y][x]
            if cell_value == 15:
                row.append(1)
            else:
                row.append(0)
        simple_grid.append(row)
    
    return simple_grid

def generate_level(level_number: int, width: int, height: int, base_seed: int) -> list:
    
    if level_number == 1:
        seed = base_seed
    else:
        seed = random.randint(1, 99999)

    try:
        maze = MazeGenerator(size=(width, height), perfect=False, seed=seed)
        return translate_maze(maze)
    except Exception as e:
        print(f"[Maze Adapter] Level {level_number} generation failed: {e}. Falling back to safe empty grid.", file=sys.stderr)
        width = max(width, 5)
        height = max(height, 5)
        safe_grid = [[1 if x == 0 or x == width - 1 or y == 0 or y == height - 1 else 0 
                      for x in range(width)] 
                     for y in range(height)]
        return safe_grid

