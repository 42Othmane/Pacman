"""Configuration loader with comment support and validation."""

import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STATE_NORMAL = 0
STATE_STRING = 1
STATE_LINE_COMMENT = 2
STATE_BLOCK_COMMENT = 3
STATE_STRING_ESCAPE = 4

DEFAULT_CONFIG: Dict[str, Any] = {
    "highscore_filename": "highscore.json",
    "levels": [{"width": 15, "height": 15}],
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90
}

BOUNDS: Dict[str, Tuple[int, Optional[int]]] = {
    "lives": (1, 99),
    "pacgum": (1, 10000),
    "points_per_pacgum": (0, 100000),
    "points_per_super_pacgum": (0, 100000),
    "points_per_ghost": (0, 100000),
    "seed": (0, None),
    "level_max_time": (10, 3600),
}

MIN_MAZE_SIZE = 5
MAX_MAZE_SIZE = 101

MIN_LEVELS = 10
SIZE_STEP = 2


def _ensure_min_levels(
    levels: List[Dict[str, int]]
) -> List[Dict[str, int]]:
    """Complète la liste jusqu'à MIN_LEVELS niveaux.

    Les niveaux ajoutés dérivent du dernier, avec une taille
    croissante plafonnée à MAX_MAZE_SIZE.
    """
    result = copy.deepcopy(levels)

    if not result:
        return copy.deepcopy(DEFAULT_CONFIG["levels"])

    while len(result) < MIN_LEVELS:
        last_res = result[-1]
        w = min(last_res["width"] + SIZE_STEP, MAX_MAZE_SIZE)
        h = min(last_res["height"] + SIZE_STEP, MAX_MAZE_SIZE)
        result.append({"width": w, "height": h})

    return result


def _clamp(key: str, value: int) -> int:
    """Ramène value dans les bornes définies pour key."""
    if key not in BOUNDS:
        return value
    low, high = BOUNDS[key]
    if value < low:
        print(
            f"Warning: '{key}' = {value} is below minimum {low}. "
            f"Clamped to {low}.",
            file=sys.stderr
        )
        return low
    if high is not None and value > high:
        print(
            f"Warning: '{key}' = {value} is over maximum {high}. "
            f"Clamped to {high}.",
            file=sys.stderr
        )
        return high
    return value


def _validate_levels(
    levels: Any
) -> Optional[List[Dict[str, int]]]:
    """Valide et nettoie la liste des niveaux.

    Retourne la liste des niveaux valides, ou None si aucun
    n'est exploitable.
    """
    if not isinstance(levels, list):
        print(
            "Warning: 'levels' must be a list. "
            "Default levels will be used.",
            file=sys.stderr
        )
        return None

    valid: List[Dict[str, int]] = []
    for index, level in enumerate(levels):
        if not isinstance(level, dict):
            print(
                f"Warning: level {index} is not an object. Skipped.",
                file=sys.stderr
            )
            continue

        if "width" not in level or "height" not in level:
            print(
                f"Warning: level {index} is missing 'width' or 'height'. "
                "Skipped.",
                file=sys.stderr
            )
            continue

        w = level["width"]
        h = level["height"]
        if not isinstance(w, int) or not isinstance(h, int):
            print(
                f"Warning: level {index}: 'width' and 'height' must be "
                "integers. Skipped.",
                file=sys.stderr
            )
            continue

        w = max(MIN_MAZE_SIZE, min(w, MAX_MAZE_SIZE))
        h = max(MIN_MAZE_SIZE, min(h, MAX_MAZE_SIZE))

        valid.append({"width": w, "height": h})

    if not valid:
        return None
    return valid


def _strip_comments(json_text: str) -> str:
    """Remove comments from JSON string."""
    result: List[str] = []
    state = STATE_NORMAL
    i = 0

    while i < len(json_text):
        char = json_text[i]

        if state == STATE_NORMAL:
            if char == '"':
                state = STATE_STRING
                result.append(char)

            elif char == '#':
                state = STATE_LINE_COMMENT

            elif char == '/' and i + 1 < len(json_text):
                if json_text[i + 1] == '/':
                    state = STATE_LINE_COMMENT
                    i += 1

                elif json_text[i + 1] == '*':
                    state = STATE_BLOCK_COMMENT
                    i += 1

                else:
                    result.append(char)

            else:
                result.append(char)

        elif state == STATE_STRING:
            result.append(char)
            if char == "\\":
                state = STATE_STRING_ESCAPE
            elif char == '"':
                state = STATE_NORMAL

        elif state == STATE_STRING_ESCAPE:
            result.append(char)
            state = STATE_STRING

        elif state == STATE_LINE_COMMENT:
            if char == '\n':
                state = STATE_NORMAL

        elif state == STATE_BLOCK_COMMENT:
            if char == '*' and i + 1 < len(json_text):
                if json_text[i + 1] == '/':
                    state = STATE_NORMAL
                    i += 1

        i += 1

    return ''.join(result)


def load_config(filepath: str) -> Dict[str, Any]:
    """Load and validate configuration from a JSON file."""
    if Path(filepath).suffix.lower() != ".json":
        print("File type must be .JSON", file=sys.stderr)
        defaults = copy.deepcopy(DEFAULT_CONFIG)
        defaults["levels"] = _ensure_min_levels(defaults["levels"])
        return defaults

    try:
        config_file = Path(filepath).read_text(encoding="utf-8")
        strip_config = _strip_comments(config_file)
        data = json.loads(strip_config)
    except Exception as e:
        print(
            f"Configuration Error: {e}. Default values will be used",
            file=sys.stderr
        )
        defaults = copy.deepcopy(DEFAULT_CONFIG)
        defaults["levels"] = _ensure_min_levels(defaults["levels"])
        return defaults

    if not isinstance(data, dict):
        print(
            "Configuration Error: root must be a JSON object. "
            "Default values will be used",
            file=sys.stderr
        )
        defaults = copy.deepcopy(DEFAULT_CONFIG)
        defaults["levels"] = _ensure_min_levels(defaults["levels"])
        return defaults

    final_config = copy.deepcopy(DEFAULT_CONFIG)

    for key, value in data.items():
        if key not in DEFAULT_CONFIG:
            continue

        attended_type = type(DEFAULT_CONFIG[key])
        data_type = type(value)

        if attended_type == data_type:
            if key == "levels":
                cleaned = _validate_levels(value)
                if cleaned is not None:
                    final_config[key] = cleaned
            elif isinstance(value, int):
                final_config[key] = _clamp(key, value)
            else:
                final_config[key] = value
        else:
            print(
                f"Warning: key '{key}' has type {data_type.__name__}, "
                f"expected {attended_type.__name__}. "
                "Default value will be used.",
                file=sys.stderr
            )

    final_config["levels"] = _ensure_min_levels(final_config["levels"])

    return final_config
