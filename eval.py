import lst
import enums
import ast
import symbol


def repr(x):
    return x if isinstance(x, str) else ast.show_ast(x)


Operations = {
    enums.OP.Add: lambda x, y: x + y,
    enums.OP.Sub: lambda x, y: x - y,
    enums.OP.Mul: lambda x, y: x * y,
    enums.OP.Div: lambda x, y: x // y if isinstance(x, int) and isinstance(y, int) else x / y,
    enums.OP.Mod: lambda x, y: x % y,
    enums.OP.SConcat: lambda x, y: repr(x) + repr(y),
}

Predicates = {
    enums.PR.Eq: lambda x, y: ast.equal(x, y),
    enums.PR.Gt: lambda x, y: x > y,
    enums.PR.Lt: lambda x, y: x < y,
    enums.PR.Gte: lambda x, y: x >= y,
    enums.PR.Lte: lambda x, y: x <= y,
}


def fold_op(op, values):
    if lst.is_nil(values):
        raise ValueError("Operation" + enums.ValuesToString[op] + "without arguments")

    out = eval(lst.car(values))
    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values))
        out = Operations[op](out, elem)
        values = lst.cdr(values)

    return out


def fold_pr(pr, values):
    if lst.is_nil(values):
        return True

    cur = eval(lst.car(values))
    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values))
        if not Predicates[pr](cur, elem):
            return False
        cur = elem
        values = lst.cdr(values)

    return True


def get_args(values, count):
    out = []
    for _ in range(count):
        if lst.is_nil(values):
            raise ValueError("TODO error")

        out.append(lst.car(values))
        values = lst.cdr(values)

    if not lst.is_nil(values):
        raise ValueError("TODO error")

    return out


def eval(value):
    if lst.is_cons_list(value):
        if lst.is_nil(value):
            return value

        head = eval(lst.car(value))

        if isinstance(head, enums.OP):
            return fold_op(head, lst.cdr(value))
        elif isinstance(head, enums.PR):
            return fold_pr(head, lst.cdr(value))
        elif isinstance(head, enums.SF):
            tail = lst.cdr(value)

            if head == enums.SF.QUOTE:
                return get_args(tail, 1)[0]

            elif head == enums.SF.TYPEOF:
                arg = eval(get_args(tail, 1)[0])

                if lst.is_cons_list(arg):
                    return "list"
                elif symbol.is_symbol(arg):
                    return "symbol"
                else:
                    return type(arg).__name__

            elif head == enums.SF.CONS:
                args = list(map(eval, get_args(tail, 2)))

                if not lst.is_cons_list(args[1]):
                    raise ValueError("TODO error")

                return lst.cons(args[0], args[1])

            elif head == enums.SF.CAR:
                arg = eval(get_args(tail, 1)[0])

                if not lst.is_cons_list(arg):
                    raise ValueError("TODO error")

                return lst.car(arg)

            elif head == enums.SF.CDR:
                arg = eval(get_args(tail, 1)[0])

                if not lst.is_cons_list(arg):
                    raise ValueError("TODO error")

                return lst.cdr(arg)
        else:
            raise ValueError("head not callable: " + ast.show_ast(value))

    else: return value
