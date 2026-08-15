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
