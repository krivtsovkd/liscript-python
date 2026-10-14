# important !!! (def a 1 b (+ 1 a)) must work in ocaml
# TODO read-number (in the lisp ? in the future)
import lst
import enums
import ast
import symbol
import settings
import parser
from env import Env

env = Env()


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
    out = repr(out) if op == enums.OP.SConcat else out

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


def get_args(values, count, desc):
    out = []
    for _ in range(count):
        if lst.is_nil(values):
            raise ValueError("expected " + str(count) + " arguments, got " + str(len(out)) + " in:\n" + desc)

        out.append(lst.car(values))
        values = lst.cdr(values)

    if not lst.is_nil(values):
        raise ValueError("expected " + str(count) + " arguments, got too many in:\n" + desc)

    return out


def eval(value):
    if symbol.is_symbol(value):
        return env.get(value)

    if not lst.is_cons_list(value):
        return value

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
            return get_args(tail, 1, repr(value))[0]

        elif head == enums.SF.TYPEOF:
            arg = eval(get_args(tail, 1, repr(value))[0])

            if lst.is_cons_list(arg):
                return "list"
            elif symbol.is_symbol(arg):
                return "symbol"
            else:
                return type(arg).__name__

        elif head == enums.SF.CONS:
            args = list(map(eval, get_args(tail, 2, repr(value))))

            if not lst.is_cons_list(args[1]):
                raise ValueError("expected cons list, got " + ast.show_ast(args[1]) + " in:\n" + ast.show_ast(value))

            return lst.cons(args[0], args[1])

        elif head == enums.SF.CAR:
            arg = eval(get_args(tail, 1, repr(value))[0])

            if not lst.is_cons_list(arg):
                if settings.settings.implicit_list_interface:
                    return arg
                else:
                    raise ValueError("expected cons list, got " + ast.show_ast(arg) + " in:\n" + ast.show_ast(value))
            elif lst.is_nil(arg):
                raise ValueError("expected nonempty list in:\n" + ast.show_ast(value))

            return lst.car(arg)

        elif head == enums.SF.CDR:
            arg = eval(get_args(tail, 1, repr(value))[0])

            if not lst.is_cons_list(arg):
                if settings.settings.implicit_list_interface:
                    return lst.nil
                else:
                    raise ValueError("expected cons list, got " + ast.show_ast(arg) + " in:\n" + ast.show_ast(value))
            elif lst.is_nil(arg):
                raise ValueError("expected nonempty list in:\n" + ast.show_ast(value))

            return lst.cdr(arg)

        elif head == enums.SF.COND:
            # TODO maybe raise if 1 argument
            while not lst.is_nil(tail):
                var_sym = eval(lst.car(tail))
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    return var_sym

                if not isinstance(var_sym, bool):
                    raise ValueError("expected bool, got " + ast.show_ast(var_sym) + " in:\n" + ast.show_ast(value))

                if var_sym:
                    return eval(lst.car(tail))
                else:
                    tail = lst.cdr(tail)

            raise ValueError("none of the conditions are true in\n" + ast.show_ast(value))

        elif head == enums.SF.EVAL:
            arg = eval(get_args(tail, 1, repr(value))[0])
            return eval(arg)

        elif head == enums.SF.SYMBOL:
            arg = eval(get_args(tail, 1, repr(value))[0])
            return symbol.symbol(repr(arg))

        elif head == enums.SF.DO:
            out = lst.nil

            while not lst.is_nil(tail):
                out = eval(lst.car(tail))
                tail = lst.cdr(tail)

            return out

        elif head == enums.SF.PRINT:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail))))
                tail = lst.cdr(tail)

            print(" ".join(out))
            return lst.nil

        elif head == enums.SF.READ:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail))))
                tail = lst.cdr(tail)

            user_input = input(" ".join(out) + "\n")
            x, y = parser.parse(user_input)
            return x

        elif head == enums.SF.DEF:
            while not lst.is_nil(tail):
                var_sym = lst.car(tail)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("TODO def not sym")
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    raise ValueError("TODO no def value")

                env.define(var_sym, eval(lst.car(tail)))

                tail = lst.cdr(tail)

            return lst.nil

        elif head == enums.SF.SET:
            while not lst.is_nil(tail):
                var_sym = lst.car(tail)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("TODO def not sym")
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    raise ValueError("TODO no def value")

                env.set(var_sym, eval(lst.car(tail)))

                tail = lst.cdr(tail)

            return lst.nil

    else:
        raise ValueError("head not callable: " + ast.show_ast(value))
