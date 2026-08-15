STATE_NORMAL = 0
STATE_STRING = 1
STATE_COMMENT = 2

def _strip_comments(json_text: str) -> str:
    """
    Prend le texte brut du fichier, supprime les commentaires #, // et /* */
    et retourne du texte JSON propre prêt à être lu par Python.
    """

    result = ""
    actual_state = STATE_NORMAL
    i = 0

    while i < len(json_text):

        if actual_state == STATE_NORMAL:
            if json_text[i] == '"':
                actual_state = STATE_STRING
            elif json_text[i] == '#':
                actual_state = STATE_COMMENT
            elif json_text[i] == '/':
                if json_text[i + 1] == '/' or json_text[i + 1] == "*":
                    actual_state = STATE_COMMENT
            else:
                result += json_text[i]

        elif actual_state == STATE_STRING:
            if json_text[i] == '"':
                actual_state = STATE_NORMAL
            else:
                result += json_text[i]

        elif actual_state == STATE_COMMENT:
            if json_text[i] == "\n":
                actual_state = STATE_NORMAL
                result += json_text[i]
            elif json_text[i] == "*":
                if json_text[i + 1] == "/":
                    actual_state = STATE_NORMAL
                    i += 1
        i += 1
    return result

# import sys

# if __name__ == "__main__":
#     # On vérifie qu'un fichier a bien été passé en argument
#     if len(sys.argv) < 2:
#         print("Utilisation : python settings.py <fichier.json>")
#         sys.exit(1)

#     # Le bloc 'with' ferme le fichier tout seul à la fin
#     with open(sys.argv[1], "r", encoding="utf-8") as file:
#         texte_brut = file.read() # <-- ICI on transforme l'objet fichier en texte
        
#     resultat_propre = _strip_comments(texte_brut)
    
#     # Le print est ici, bien séparé de la logique de la fonction
#     print(resultat_propre)
