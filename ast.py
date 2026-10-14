import symbol
import lst
import enums


def show_ast(ast):
    if type(ast) is bool:
        return "true" if ast else "false"
    elif ast in enums.ValuesToString:
        return enums.ValuesToString[ast]
    elif symbol.is_symbol(ast):
        return str(symbol.name(ast))
    elif type(ast) is str:
        return '"' + ast + '"'
    elif lst.is_cons_list(ast):
        # TODO use " ".join(out)
        out = "("
        while not lst.is_nil(ast):
            out += show_ast(lst.car(ast)) + " "
            ast = lst.cdr(ast)

        if out[-1] == " ":
            out = out[:-1]

        out += ")"
        return out

    return str(ast)


def equal(a, b):
    if lst.is_cons_list(a) and lst.is_cons_list(b):
        if lst.is_nil(a):
            return lst.is_nil(b)
        elif lst.is_nil(b):
            return lst.is_nil(a)

        return equal(lst.car(a), lst.car(b)) and equal(lst.cdr(a), lst.cdr(b))
    elif symbol.is_symbol(a) and symbol.is_symbol(b):
        return symbol.name(a) == symbol.name(b)
    else:
        return False if not (type(a) is type(b)) else a == b
