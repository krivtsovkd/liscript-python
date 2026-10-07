import lst
import symbol
import re
import enums


def strip_left(text):
    while len(text) > 0:
        if text[0].isspace() or text[0] in ",":
            text = text[1:]
        elif text[0] == ";":
            line_end = text.find("\n")
            if line_end == -1:
                return ""
            text = text[line_end:]
        else:
            break
    return text


def parse_list(text):
    text = strip_left(text)

    if text == "":
        raise ValueError("Missing list closing bracket")

    if text[0] == ")":
        return lst.nil, text[1:]

    value, remainder = parse(text)
    remaining_value, remaining_text = parse_list(remainder)
    return lst.cons(value, remaining_value), remaining_text


def parse_token(token):
    token = strip_left(token)

    if token == "false":
        return False
    elif token == "true":
        return True
    elif token in enums.StringToValue:
        return enums.StringToValue[token]

    try:
        return int(token)
    except Exception:
        try:
            return float(token)
        except Exception:
            return symbol.symbol(token)


def parse(text):
    text = strip_left(text)

    if text == "":
        return None, ""

    f = text[0]
    if f == '"':
        try:
            s = text[1:].index('"')
            return text[1:s + 1], text[s + 2:]
        except Exception:
            raise ValueError("Missing closing quote in " + text[:50])
    elif f == "'":
        x, y = parse(text[1:])
        return lst.cons(enums.SF.QUOTE, lst.cons(x, lst.nil)), y
    elif f == "(":
        return parse_list(text[1:])
    elif f == ")":
        raise ValueError("Extra closing bracket in " + text[:50])
    else:
        match = re.search(r"[, \n\r\t\"();]|$", text).start()
        return parse_token(text[:match]), text[match:]
