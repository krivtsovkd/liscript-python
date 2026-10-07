def is_symbol(val):
    return type(val) is str and len(val) > 0 and val[0] == "\x00"


def symbol(name):
    return "\x00" + name


def symbol_name(sym):
    return sym[1:]
