import json
import sys
from pathlib import Path

def load_highscores(filepath: str) -> list:
    """
    Lit le fichier de highscores sur le disque.
    Retourne une liste vide si le fichier n'existe pas ou est corrompu.
    """
    try:
        highscore_file = Path(filepath).read_text(encoding="utf-8")
        highscore_data = json.loads(highscore_file)

        if not isinstance(highscore_data, list):
            print("Error: Highscore file is not a list. Returning empty.", file=sys.stderr)
            return []

    except FileNotFoundError:
        return []

    except Exception as e:
        print(f"Error loading highscores: {e}. Returning empty.", file=sys.stderr)
        return []
    
    return highscore_data

def save_highscores(filepath: str, data: list) -> None:
    """
    Écrit la liste de highscores dans le fichier sur le disque.
    """
    try :
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving highscores: {e}", file=sys.stderr)

# if __name__ == "__main__":
#     # On simule le nom du fichier
#     fichier_test = "test_highscore.json"
    
#     print("=== 1. CHARGEMENT INITIAL ===")
#     scores = load_highscores(fichier_test)
#     print(f"Contenu chargé : {scores}")
    
#     print("\n=== 2. SIMULATION D'UNE FIN DE PARTIE ===")
#     # On ajoute un faux score à notre liste vide
#     scores.append({"name": "Player1", "score": 1500})
#     print(f"Nouveau contenu en mémoire : {scores}")
    
#     print("\n=== 3. SAUVEGARDE DANS LE FICHIER ===")
#     save_highscores(fichier_test, scores)
#     print("(Regarde dans ton dossier, le fichier 'test_highscore.json' a été créé !)")
    
#     print("\n=== 4. RECHARGEMENT POUR VERIFIER ===")
#     # Maintenant que le fichier existe, ça doit le lire correctement
#     scores_relus = load_highscores(fichier_test)
#     print(f"Contenu relu depuis le disque : {scores_relus}")
    
#     print("\n=== 5. TEST DE FICHIER CORROMPU ===")
#     # On écrit n'importe quoi dans le fichier à la main
#     with open(fichier_test, "w") as f:
#         f.write("CECI N'EST PAS DU JSON")
    
#     # On essaie de le relire
#     scores_casses = load_highscores(fichier_test)
#     print(f"Contenu lu après corruption : {scores_casses}")
    
#     # Nettoyage du fichier de test à la fin
#     import os
#     if os.path.exists(fichier_test):
#         os.remove(fichier_test)