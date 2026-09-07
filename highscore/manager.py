"""Persistance et validation des scores (spec 5.5)."""
import json
import re
import sys
from pathlib import Path

MAX_NAME_LENGTH = 10
TOP_N = 10

HighscoreEntry = dict[str, str | int]


def _is_valid_entry(entry: object) -> bool:
    """True si entry est un score bien formé ({"name": str, "score": int})."""
    if not isinstance(entry, dict):
        return False
    if "name" not in entry or "score" not in entry:
        return False
    if not isinstance(entry["name"], str):
        return False
    if type(entry["score"]) is not int:
        return False
    return entry["score"] >= 0


def load_highscores(filepath: str) -> list[HighscoreEntry]:
    """Lit le fichier de highscores sur le disque.

    Retourne une liste vide si le fichier n'existe pas ou est corrompu.
    """
    try:
        highscore_file = Path(filepath).read_text(encoding="utf-8")
        highscore_data = json.loads(highscore_file)

        if not isinstance(highscore_data, list):
            print(
                "Error: Highscore file is not a list. Returning "
                "empty.",
                file=sys.stderr,
            )
            return []

    except FileNotFoundError:
        return []

    except Exception as error:
        print(
            f"Error loading highscores: {error}. Returning empty.",
            file=sys.stderr,
        )
        return []

    return [entry for entry in highscore_data if _is_valid_entry(entry)]


def save_highscores(filepath: str, data: list[HighscoreEntry]) -> None:
    """Écrit la liste de highscores dans le fichier sur le disque."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as error:
        print(f"Error saving highscores: {error}", file=sys.stderr)


def validate_name(name: object) -> bool:
    """True si le nom est valide.

    1 à 10 caractères alphanumériques ou espaces.
    """
    if not isinstance(name, str):
        return False
    pattern = rf"[A-Za-z0-9 ]{{1,{MAX_NAME_LENGTH}}}"
    return re.fullmatch(pattern, name.strip()) is not None


def add_highscore(
    name: str, score: int, existing_scores: list[HighscoreEntry]
) -> list[HighscoreEntry]:
    """Ajoute un score, valide nom/score, garde le top 10 trié."""
    updated_scores = existing_scores.copy()

    if not validate_name(name):
        name = "UNKNOWN"
    else:
        name = name.strip()

    if type(score) is not int or score < 0:
        score = 0

    updated_scores.append({"name": name, "score": score})
    updated_scores.sort(key=lambda entry: entry["score"], reverse=True)

    return updated_scores[:TOP_N]
