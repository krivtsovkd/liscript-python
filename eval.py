# important !!! (def a 1 b (+ 1 a)) must work in ocaml
# TODO read-number (in the lisp ? in the future)
# HOMWORK load stdlib on start
import lst
import enums
import ast
import symbol
import settings
import parser
import ldambda
import env

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
        passed_values = lst.cdr(value)

        if head == enums.SF.QUOTE:
            return get_args(passed_values, 1, repr(value))[0]

        elif head == enums.SF.TYPEOF:
            arg = eval(get_args(passed_values, 1, repr(value))[0], e)

            if lst.is_cons_list(arg):
                return "list"
            elif symbol.is_symbol(arg):
                return "symbol"
            else:
                return type(arg).__name__

        elif head == enums.SF.CONS:
            lambda_args = get_args(passed_values, 2, repr(value))
            lambda_args[0] = eval(lambda_args[0], e)
            lambda_args[1] = eval(lambda_args[1], e)

            if not lst.is_cons_list(lambda_args[1]):
                raise ValueError("expected cons list, got " + ast.show_ast(lambda_args[1]) + " in:\n" + ast.show_ast(value))

            return lst.cons(lambda_args[0], lambda_args[1])

        elif head == enums.SF.CAR:
            arg = eval(get_args(passed_values, 1, repr(value))[0], e)

            if not lst.is_cons_list(arg):
                if settings.settings.implicit_list_interface:
                    return arg
                else:
                    raise ValueError("expected cons list, got " + ast.show_ast(arg) + " in:\n" + ast.show_ast(value))
            elif lst.is_nil(arg):
                raise ValueError("expected nonempty list in:\n" + ast.show_ast(value))

            return lst.car(arg)

        elif head == enums.SF.CDR:
            arg = eval(get_args(passed_values, 1, repr(value))[0], e)

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
            while not lst.is_nil(passed_values):
                var_sym = eval(lst.car(passed_values), e)
                passed_values = lst.cdr(passed_values)

                if lst.is_nil(passed_values):
                    return var_sym

                if not isinstance(var_sym, bool):
                    raise ValueError("expected bool, got " + ast.show_ast(var_sym) + " in:\n" + ast.show_ast(value))

                if var_sym:
                    return eval(lst.car(passed_values), e)
                else:
                    passed_values = lst.cdr(passed_values)

            raise ValueError("none of the conditions are true in\n" + ast.show_ast(value))

        elif head == enums.SF.EVAL:
            arg = eval(get_args(passed_values, 1, repr(value))[0], e)
            return eval(arg, e)

        elif head == enums.SF.SYMBOL:
            arg = eval(get_args(passed_values, 1, repr(value))[0], e)
            return symbol.symbol(repr(arg), e)

        elif head == enums.SF.DO:
            out = lst.nil

            while not lst.is_nil(passed_values):
                out = eval(lst.car(passed_values), e)
                passed_values = lst.cdr(passed_values)

            return out

        elif head == enums.SF.PRINT:
            out = []

            while not lst.is_nil(passed_values):
                out.append(repr(eval(lst.car(passed_values), e)))
                passed_values = lst.cdr(passed_values)

            print(" ".join(out))
            return lst.nil

        elif head == enums.SF.READ:
            out = []

            while not lst.is_nil(passed_values):
                out.append(repr(eval(lst.car(passed_values), e)))
                passed_values = lst.cdr(passed_values)

            user_input = input(" ".join(out) + "\n")
            x, y = parser.parse(user_input)
            return x

        elif head == enums.SF.DEF:
            while not lst.is_nil(passed_values):
                var_sym = lst.car(passed_values)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("TODO def not sym")
                passed_values = lst.cdr(passed_values)

                if lst.is_nil(passed_values):
                    raise ValueError("TODO no def value")

                e.define(var_sym, eval(lst.car(passed_values), e))

                passed_values = lst.cdr(passed_values)

            return lst.nil

        elif head == enums.SF.SET:
            while not lst.is_nil(passed_values):
                var_sym = lst.car(passed_values)
                if not symbol.is_symbol(var_sym):
                    raise ValueError("TODO def not sym")
                passed_values = lst.cdr(passed_values)

                if lst.is_nil(passed_values):
                    raise ValueError("TODO no def value")

                e.set(var_sym, eval(lst.car(passed_values), e))

                passed_values = lst.cdr(passed_values)

            return lst.nil

        elif head == enums.SF.LAMBDA:
            lambda_args = get_args(passed_values, 2, repr(value))
            # TODO check that args are symbols
            if not lst.is_cons_list(lambda_args[0]):
                raise ValueError("TODO expected cons list")

            return ldambda.Lambda(lambda_args[0], lambda_args[1], e)

        elif head == enums.SF.DAMBDA:
            lambda_args = get_args(passed_values, 2, repr(value))
            # TODO check that args are symbols
            if not lst.is_cons_list(lambda_args[0]):
                raise ValueError("TODO expected cons list")

            return ldambda.Dambda(lambda_args[0], lambda_args[1])

    elif isinstance(head, ldambda.Lambda):
        new_env = env.Env(head.env)
        passed_values = lst.cdr(value)
        lambda_args = head.args
        while True:
            if lst.is_nil(lambda_args) and lst.is_nil(passed_values):
                return eval(head.body, new_env)
            if lst.is_nil(passed_values):
                return ldambda.Lambda(lambda_args, head.body, new_env)
            if lst.is_nil(lambda_args):
                out = []
                while not lst.is_nil(passed_values):
                    out.append(eval(lst.car(passed_values), e))
                    passed_values = lst.cdr(passed_values)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                return eval(head.body, new_env)

            arg = eval(lst.car(passed_values), e)
            sym = lst.car(lambda_args)

            new_env.define(sym, arg)

            passed_values = lst.cdr(passed_values)
            lambda_args = lst.cdr(lambda_args)

    elif isinstance(head, ldambda.Dambda):
        new_env = env.Env(e)
        passed_values = lst.cdr(value)
        lambda_args = head.args
        while True:
            if lst.is_nil(lambda_args) and lst.is_nil(passed_values):
                return eval(head.body, new_env)
            if lst.is_nil(passed_values):
                return ldambda.Lambda(lambda_args, head.body)
            if lst.is_nil(lambda_args):
                out = []
                while not lst.is_nil(passed_values):
                    out.append(eval(lst.car(passed_values), e))
                    passed_values = lst.cdr(passed_values)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                return eval(head.body, new_env)

            arg = eval(lst.car(passed_values), e)
            sym = lst.car(lambda_args)

            new_env.define(sym, arg)

            passed_values = lst.cdr(passed_values)
            lambda_args = lst.cdr(lambda_args)

    else:
        raise ValueError("head not callable: " + ast.show_ast(value))
