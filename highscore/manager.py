import json
import sys
from pathlib import Path
import re

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

def _validate_name(name: str) -> bool:
    return re.fullmatch(r"^[A-Za-z0-9 ]{1,10}$", name.strip()) is not None

def add_highscore(name: str, score: int, existing_scores: list) -> list:
    updated_scores = existing_scores.copy()
    name = name.strip()
    if not _validate_name(name):
        name = "UNKNOWN"
    
    if not isinstance(score, int) or score < 0:
        score = 0

    updated_scores.append({"name": name, "score": score})
    
    updated_scores.sort(key=lambda x: x["score"], reverse=True)

    return updated_scores[:10]

# if __name__ == "__main__":
#     # On simule un tableau de scores déjà existant
#     base_scores = [
#         {"name": "AAA", "score": 1000},
#         {"name": "BBB", "score": 500},
#     ]

#     print("--- TEST 1: Ajout normal ---")
#     # Doit s'insérer en 1ère position
#     resultat1 = add_highscore("Jean", 1500, base_scores)
#     print(resultat1)

#     print("\n--- TEST 2: Nom invalide ---")
#     # Trop long, et caractère spécial (@)
#     resultat2 = add_highscore("Jean@Dupont!", 200, base_scores)
#     print(resultat2) 
#     # Le 3ème élément devrait être {"name": "UNKNOWN", "score": 200}

#     print("\n--- TEST 3: Score invalide ---")
#     # Score négatif et score texte
#     resultat3 = add_highscore("Alain", -50, base_scores)
#     resultat4 = add_highscore("Bernard", "mille", base_scores)
#     print("Score negatif:", resultat3)
#     print("Score texte:", resultat4)

#     print("\n--- TEST 4: Limitation au Top 10 ---")
#     # On crée une liste de 10 scores
#     top10_rempli = [{"name": f"Joueur{i}", "score": (10-i)*100} for i in range(10)]
    
#     # On ajoute un 11ème joueur avec un score énorme
#     resultat5 = add_highscore("Gagnant", 9999, top10_rempli)
#     print(f"Taille de la liste : {len(resultat5)} (Doit faire 10)")
#     print(f"Premier de la liste : {resultat5[0]} (Doit être Gagnant)")
#     # Le dernier joueur (Joueur9 avec 100) doit avoir disparu


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