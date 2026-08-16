import copy
import json
import sys
from pathlib import Path

STATE_NORMAL = 0
STATE_STRING = 1
STATE_LINE_COMMENT = 2
STATE_BLOCK_COMMENT = 3

DEFAULT_CONFIG = {
    "highscore_filename": "highscore.json",
    "levels": [{"width": 21, "height": 21}],
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90
}

def _strip_comments(json_text: str) -> str:
    result = []
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

            if char == '"' and (i == 0 or json_text[i - 1] != '\\'):
                state = STATE_NORMAL

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

def load_config(filepath: str) -> dict:
    try:
        config_file = Path(filepath).read_text(encoding="utf-8")
        strip_config = _strip_comments(config_file)
        data = json.loads(strip_config)
    except Exception as e:
        print(f"Configuration Error: {e}. Default values will be used", file=sys.stderr)
        return DEFAULT_CONFIG.copy()
    
    final_config = copy.deepcopy(DEFAULT_CONFIG)

    for key, value in data.items():
        if key not in DEFAULT_CONFIG:
            continue
        
        attended_type = type(DEFAULT_CONFIG[key])
        data_type = type(value)

        if attended_type == data_type:
            final_config[key] = value
        else:
            print(f"Warning: key '{key}' has type {data_type.__name__}, "
                  f"expected {attended_type.__name__}. "
                  f"Default value will be used.", file=sys.stderr)
        
    return final_config


# if __name__ == "__main__":
#     # On vérifie qu'un fichier a été passé en argument
#     if len(sys.argv) < 2:
#         print("Utilisation : python settings.py <fichier.json>")
#         sys.exit(1)

#     print("--- CHARGEMENT DE LA CONFIG ---")
#     config = load_config(sys.argv[1])
    
#     print("\n--- RÉSULTAT FINAL ---")
#     # Le 'import json' sert ici à afficher le dictionnaire joliment (avec l'indentation)
#     print(json.dumps(config, indent=4))

