import time
import lst
import enums
import ast
import symbol
import settings
import parser
import ldambda
import env as environ

REST_ARGS = symbol.symbol("rest-args")


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


def fold_op(op, values, e):
    if lst.is_nil(values):
        raise ValueError("Operation" + enums.ValuesToString[op] + "without arguments")

    out = eval(lst.car(values), e)
    out = repr(out) if op == enums.OP.SConcat else out

    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values), e)
        out = Operations[op](out, elem)
        values = lst.cdr(values)

    return out


def fold_pr(pr, values, e):
    if lst.is_nil(values):
        return True

    cur = eval(lst.car(values), e)
    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values), e)
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


def racroexpand(e, value):
    if symbol.is_symbol(value):
        try:
            return e.get(value)
        except ValueError:
            return value
    elif lst.is_cons_list(value):
        return lst.nil if lst.is_nil(value) else lst.cons(racroexpand(e, lst.car(value)), racroexpand(e, lst.cdr(value)))
    else:
        return value


def eval(value, e):
    if symbol.is_symbol(value):
        return e.get(value)

    if not lst.is_cons_list(value):
        return value

    if lst.is_nil(value):
        return value

    head = eval(lst.car(value), e)

    if isinstance(head, enums.OP):
        return fold_op(head, lst.cdr(value), e)
    elif isinstance(head, enums.PR):
        return fold_pr(head, lst.cdr(value), e)
    elif isinstance(head, enums.SF):
        tail = lst.cdr(value)

        if head == enums.SF.QUOTE:
            return get_args(tail, 1, repr(value))[0]

        elif head == enums.SF.TYPEOF:
            arg = eval(get_args(tail, 1, repr(value))[0], e)

            if lst.is_cons_list(arg):
                return "list"
            elif symbol.is_symbol(arg):
                return "symbol"
            else:
                return type(arg).__name__

        elif head == enums.SF.CONS:
            dambda_args = get_args(tail, 2, repr(value))
            dambda_args[0] = eval(dambda_args[0], e)
            dambda_args[1] = eval(dambda_args[1], e)

            if not lst.is_cons_list(dambda_args[1]):
                raise ValueError("expected cons list, got " + ast.show_ast(dambda_args[1]) + " in:\n" + ast.show_ast(value))

            return lst.cons(dambda_args[0], dambda_args[1])

        elif head == enums.SF.CAR:
            arg = eval(get_args(tail, 1, repr(value))[0], e)

            if not lst.is_cons_list(arg):
                if settings.settings.implicit_list_interface:
                    return arg
                else:
                    raise ValueError("expected cons list, got " + ast.show_ast(arg) + " in:\n" + ast.show_ast(value))
            elif lst.is_nil(arg):
                raise ValueError("expected nonempty list in:\n" + ast.show_ast(value))

            return lst.car(arg)

        elif head == enums.SF.CDR:
            arg = eval(get_args(tail, 1, repr(value))[0], e)

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
                var_sym = eval(lst.car(tail), e)
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    return var_sym

                if not isinstance(var_sym, bool):
                    raise ValueError("expected bool, got " + ast.show_ast(var_sym) + " in:\n" + ast.show_ast(value))

                if var_sym:
                    return eval(lst.car(tail), e)
                else:
                    tail = lst.cdr(tail)

            # raise ValueError("none of the conditions are true in\n" + ast.show_ast(value))
            return lst.nil

        elif head == enums.SF.EVAL:
            arg = eval(get_args(tail, 1, repr(value))[0], e)
            return eval(arg, e)

        elif head == enums.SF.SYMBOL:
            arg = eval(get_args(tail, 1, repr(value))[0], e)
            return symbol.symbol(repr(arg))

        elif head == enums.SF.DO:
            out = lst.nil

            while not lst.is_nil(tail):
                out = eval(lst.car(tail), e)
                tail = lst.cdr(tail)

            return out

        elif head == enums.SF.PRINT:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail), e)))
                tail = lst.cdr(tail)

            print(" ".join(out))
            return lst.nil

        elif head == enums.SF.READ:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail), e)))
                tail = lst.cdr(tail)

            user_input = input(" ".join(out) + "\n")
            x, y = parser.parse(user_input)
            return x

        elif head == enums.SF.DEF:
            while not lst.is_nil(tail):
                var_sym = lst.car(tail)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("expected symbol, got " + ast.show_ast(var_sym) + " in:\n" + ast.show_ast(value))
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    raise ValueError("expected even number of arguments to def:\n" + ast.show_ast(value))

                e.define(var_sym, eval(lst.car(tail), e))

                tail = lst.cdr(tail)

            return lst.nil

        elif head == enums.SF.SET:
            while not lst.is_nil(tail):
                var_sym = lst.car(tail)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("expected symbol, got " + ast.show_ast(var_sym) + " in:\n" + ast.show_ast(value))
                tail = lst.cdr(tail)

                if lst.is_nil(tail):
                    raise ValueError("expected even number of arguments to set:\n" + ast.show_ast(value))

                e.set(var_sym, eval(lst.car(tail), e))

                tail = lst.cdr(tail)

            return lst.nil

        elif head == enums.SF.LAMBDA:
            dambda_args = get_args(tail, 2, repr(value))
            # TODO check that args are symbols
            if not lst.is_cons_list(dambda_args[0]):
                raise ValueError("Expected cons list, got " + ast.show_ast(dambda_args[0]) + " in:\n" + ast.show_ast(value))

            return ldambda.Lambda(dambda_args[0], dambda_args[1], e)

        elif head == enums.SF.DAMBDA:
            dambda_args = get_args(tail, 2, repr(value))
            # TODO check that args are symbols
            if not lst.is_cons_list(dambda_args[0]):
                raise ValueError("Expected cons list, got " + ast.show_ast(dambda_args[0]) + " in:\n" + ast.show_ast(value))

            return ldambda.Dambda(dambda_args[0], dambda_args[1])

        elif head == enums.SF.RACRO:
            dambda_args = get_args(tail, 2, repr(value))
            # TODO check that args are symbols
            if not lst.is_cons_list(dambda_args[0]):
                raise ValueError("Expected cons list, got " + ast.show_ast(dambda_args[0]) + " in:\n" + ast.show_ast(value))

            return ldambda.Racro(dambda_args[0], dambda_args[1])

        elif head == enums.SF.PANIC:
            arg = eval(get_args(tail, 1, repr(value)), e)
            raise ValueError(repr(arg))

        elif head == enums.SF.PYTHON:
            return True

        elif head == enums.SF.CURTIME:
            return time.time()

        elif head == enums.SF.DEFMACRO:
            args = get_args(tail, 3, repr(value))
            v = ldambda.Lambda(args[1], args[2], e)
            environ.macro_env.define(args[0], v)

            return lst.nil

    elif isinstance(head, ldambda.Lambda):
        new_env = environ.Env(head.env)
        tail = lst.cdr(value)
        lambda_args = head.args
        while True:
            if lst.is_nil(lambda_args):
                # TODO map_list
                out = []
                while not lst.is_nil(tail):
                    out.append(eval(lst.car(tail), e))
                    tail = lst.cdr(tail)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                break
            elif lst.is_nil(tail):
                return ldambda.Lambda(lambda_args, head.body, new_env)

            arg = eval(lst.car(tail), e)
            sym = lst.car(lambda_args)

            new_env.define(sym, arg)

            tail = lst.cdr(tail)
            lambda_args = lst.cdr(lambda_args)

        return eval(head.body, new_env)

    elif isinstance(head, ldambda.Dambda):
        new_env = environ.Env(e)
        tail = lst.cdr(value)
        dambda_args = head.args
        while True:
            if lst.is_nil(dambda_args):
                # TODO map_list
                out = []
                while not lst.is_nil(tail):
                    out.append(eval(lst.car(tail), e))
                    tail = lst.cdr(tail)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                break
            elif lst.is_nil(tail):
                raise ValueError("Dambda partial application not allowed in:\n" + ast.show_ast(value))

            arg = eval(lst.car(tail), e)
            sym = lst.car(dambda_args)

            new_env.define(sym, arg)

            tail = lst.cdr(tail)
            dambda_args = lst.cdr(dambda_args)

        return eval(head.body, new_env)

    elif isinstance(head, ldambda.Racro):
        new_env = environ.Env(None)
        tail = lst.cdr(value)
        racro_args = head.args
        while True:
            if lst.is_nil(racro_args):
                new_env.define(REST_ARGS, tail)
                break
            elif lst.is_nil(tail):
                return ldambda.Racro(racro_args, racroexpand(head.body, new_env))

            new_env.define(lst.car(racro_args), lst.car(tail))

            tail = lst.cdr(tail)
            racro_args = lst.cdr(racro_args)

        return eval(racroexpand(new_env, head.body), e)

    else:
        raise ValueError("head not callable:\n" + ast.show_ast(head) + "\nin:\n" + ast.show_ast(value))


# TODO
def map_list(f, l):
    return lst.nil if lst.is_nil(l) else lst.cons(f(lst.car(l)), map_list(f, lst.cdr(l)))


def macroexpand(value):
    if lst.is_cons_list(value):
        if lst.is_nil(value):
            return lst.nil

        l = None
        h = lst.car(value)
        if symbol.is_symbol(h):
            try:
                z = environ.macro_env.get(h)
                if isinstance(z, ldambda.Lambda):
                    l = z
            except Exception:
                ...

        if not (l is None):
            tail = lst.cdr(value)
            new_env = environ.Env(environ.runtime_env)
            macro_args = l.args
            while True:
                if lst.is_nil(macro_args):
                    new_env.define(REST_ARGS, map_list(macroexpand, tail))
                    break
                elif lst.is_nil(tail):
                    raise ValueError("cant partially apply macro:\n" + ast.show_ast(value))

                new_env.define(lst.car(macro_args), macroexpand(lst.car(tail)))

                tail = lst.cdr(tail)
                macro_args = lst.cdr(macro_args)

            return macroexpand(eval(l.body, new_env))
        else:
            return map_list(macroexpand, value)
    else:
        return value
