# TODO make strict th edefault
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

    out = eval(lst.car(values), e, False)
    out = repr(out) if op == enums.OP.SConcat else out

    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values), e, False)
        out = Operations[op](out, elem)
        values = lst.cdr(values)

    return out


def fold_pr(pr, values, e):
    if lst.is_nil(values):
        return True

    cur = eval(lst.car(values), e, False)
    values = lst.cdr(values)
    while not lst.is_nil(values):
        elem = eval(lst.car(values), e, False)
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


def eval(value, e, is_lazy):
    if symbol.is_symbol(value):
        return e.get(value)

    if not lst.is_cons_list(value):
        return value

    if lst.is_nil(value):
        return value

    head = eval(lst.car(value), e, is_lazy if lst.is_nil(lst.cdr(value)) else False)

    if isinstance(head, enums.OP):
        return fold_op(head, lst.cdr(value), e)
    elif isinstance(head, enums.PR):
        return fold_pr(head, lst.cdr(value), e)
    elif isinstance(head, enums.SF):
        tail = lst.cdr(value)

        if head == enums.SF.QUOTE:
            return get_args(tail, 1, repr(value))[0]

        elif head == enums.SF.TYPEOF:
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)

            if lst.is_cons_list(arg):
                return "list"
            elif symbol.is_symbol(arg):
                return "symbol"
            else:
                return type(arg).__name__

        elif head == enums.SF.CONS:
            dambda_args = get_args(tail, 2, repr(value))
            dambda_args[0] = eval(dambda_args[0], e, False)
            dambda_args[1] = eval(dambda_args[1], e, False)

            if not lst.is_cons_list(dambda_args[1]):
                raise ValueError("expected cons list, got " + ast.show_ast(dambda_args[1]) + " in:\n" + ast.show_ast(value))

            return lst.cons(dambda_args[0], dambda_args[1])

        elif head == enums.SF.CAR:
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)

            if not lst.is_cons_list(arg):
                if settings.settings.implicit_list_interface:
                    return arg
                else:
                    raise ValueError("expected cons list, got " + ast.show_ast(arg) + " in:\n" + ast.show_ast(value))
            elif lst.is_nil(arg):
                raise ValueError("expected nonempty list in:\n" + ast.show_ast(value))

            return lst.car(arg)

        elif head == enums.SF.CDR:
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)

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
            while not lst.is_nil(tail) and not lst.is_nil(lst.cdr(tail)):
                cond = eval(lst.car(tail), e, False)
                if cond:
                    return eval(lst.car(lst.cdr(tail)), e, is_lazy)
                tail = lst.cdr(lst.cdr(tail))

            return lst.nil if lst.is_nil(tail) else eval(lst.car(tail), e, is_lazy)

        elif head == enums.SF.EVAL:
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)
            return eval(arg, e, False)

        elif head == enums.SF.SYMBOL:
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)
            return symbol.symbol(repr(arg))

        elif head == enums.SF.DO:
            out = lst.nil

            while not lst.is_nil(tail):
                out = eval(lst.car(tail), e, is_lazy if lst.is_nil(lst.cdr(tail)) else False)
                tail = lst.cdr(tail)

            return out

        elif head == enums.SF.PRINT:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail), e, False)))
                tail = lst.cdr(tail)

            print(" ".join(out))
            return lst.nil

        elif head == enums.SF.READ:
            out = []

            while not lst.is_nil(tail):
                out.append(repr(eval(lst.car(tail), e, False)))
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

                e.define(var_sym, eval(lst.car(tail), e, False))

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

                e.set(var_sym, eval(lst.car(tail), e, False))

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
            arg = eval(get_args(tail, 1, repr(value))[0], e, False)
            raise ValueError(ast.show_ast(arg))

        elif head == enums.SF.PYTHON:
            return True

        elif head == enums.SF.CURTIME:
            return time.time()

        elif head == enums.SF.DEFMACRO:
            args = get_args(tail, 3, repr(value))
            v = ldambda.Lambda(args[1], args[2], e)
            environ.macro_env.define(args[0], v)

            return lst.nil

        elif head == enums.SF.WHILE:
            cond = lst.car(tail)
            body = lst.cdr(tail)
            while eval(cond, e, False):
                t = body
                while not lst.is_nil(t):
                    eval(lst.car(t), e, False)
                    t = lst.cdr(t)

            return lst.nil

        elif head == enums.SF.EVALIN:
            # TODO error checking
            eval_lambda = eval(lst.car(tail), e, False)
            if not isinstance(eval_lambda, ldambda.Lambda):
                raise ValueError("Expected lambda in evalin, got:\n" + ast.show_ast(eval_lambda))
            special_e = eval_lambda.env
            tail = lst.cdr(tail)
            out = lst.nil

            while not lst.is_nil(tail):
                out = eval(lst.car(tail), special_e, is_lazy if lst.is_nil(lst.cdr(tail)) else False)
                tail = lst.cdr(tail)

            return out

    elif isinstance(head, ldambda.Lambda):
        new_env = environ.Env(head.env)
        tail = lst.cdr(value)
        lambda_args = head.args
        while True:
            if lst.is_nil(lambda_args):
                # TODO map_list
                out = []
                while not lst.is_nil(tail):
                    out.append(eval(lst.car(tail), e, False))
                    tail = lst.cdr(tail)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                break
            elif lst.is_nil(tail):
                return ldambda.Lambda(lambda_args, head.body, new_env)

            arg = eval(lst.car(tail), e, False)
            sym = lst.car(lambda_args)

            new_env.define(sym, arg)

            tail = lst.cdr(tail)
            lambda_args = lst.cdr(lambda_args)

        out = ldambda.LazyCall(head.body, new_env)
        if not is_lazy:
            while isinstance(out, ldambda.LazyCall):
                out = eval(out.exp, out.env, True)
        return out

    elif isinstance(head, ldambda.Dambda):
        new_env = environ.Env(e)
        tail = lst.cdr(value)
        dambda_args = head.args
        while True:
            if lst.is_nil(dambda_args):
                # TODO map_list
                out = []
                while not lst.is_nil(tail):
                    out.append(eval(lst.car(tail), e, False))
                    tail = lst.cdr(tail)

                cons_out = lst.nil
                for elem in out[::-1]:
                    cons_out = lst.cons(elem, cons_out)
                new_env.define(REST_ARGS, cons_out)
                break
            elif lst.is_nil(tail):
                raise ValueError("Dambda partial application not allowed in:\n" + ast.show_ast(value))

            arg = eval(lst.car(tail), e, False)
            sym = lst.car(dambda_args)

            new_env.define(sym, arg)

            tail = lst.cdr(tail)
            dambda_args = lst.cdr(dambda_args)

        # return eval(head.body, new_env, False)
        out = ldambda.LazyCall(head.body, new_env)
        if is_lazy:
            return out
        else:
            while isinstance(out, ldambda.LazyCall):
                out = eval(out.exp, out.env, True)
            return out

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

        return eval(racroexpand(new_env, head.body), e, False)

    else:
        raise ValueError("head not callable:\n" + ast.show_ast(head) + "\nin:\n" + ast.show_ast(value))


class StackItem:
    def __init__(self, evaled, unevaled, e):
        self.evaled = evaled
        self.unevaled = unevaled
        self.e = e

    def __repr__(self):
        return "" + str(self.evaled) + " " + repr(self.unevaled)

    # def __iter__(self):
    #     yield self.evaled
    #     yield self.unevaled


def eval_iter(value, init_e, max_stack_size):
    if symbol.is_symbol(value):
        return init_e.get(value)

    if not lst.is_cons_list(value):
        return value

    if lst.is_nil(value):
        return value

    stack = [StackItem([], value, init_e)]
    while True:
        max_stack_size[0] = max(max_stack_size[0], len(stack))
        if not stack:
            raise ValueError("empty stack")

        # print(stack, len(stack), len(stack[-1].evaled), len(stack[-1].unevaled), end="\n\n\n\n")
        # print(stack)

        evaled = stack[-1].evaled
        unevaled = stack[-1].unevaled
        stack_e = stack[-1].e
        if symbol.is_symbol(unevaled):
            res = stack_e.get(unevaled)
            stack.pop()

            if not stack:
                return res
            else:
                stack[-1].evaled.append(res)
                continue

        elif not lst.is_cons_list(unevaled):
            res = unevaled
            stack.pop()

            if not stack:
                return res
            else:
                stack[-1].evaled.append(res)
                continue

        elif lst.is_nil(unevaled) and not isinstance(evaled[0], ldambda.Lambda) and not isinstance(evaled[0], ldambda.Racro) and evaled[0] != enums.SF.EVAL:
            res = apply(evaled, stack_e)
            stack.pop()

            if not stack:
                return res
            else:
                stack[-1].evaled.append(res)
                continue
        else:
            head = lst.car(unevaled)
            stack[-1].unevaled = lst.cdr(unevaled)
            evaled_head = evaled[0] if evaled else None

            if evaled_head == enums.SF.QUOTE:
                res = head
            elif (evaled_head == enums.SF.DEF or evaled_head == enums.SF.SET) and len(evaled) % 2 == 1:
                res = head
            elif evaled_head == enums.SF.LAMBDA or evaled_head == enums.SF.DAMBDA or evaled_head == enums.SF.RACRO:
                res = head
            elif evaled_head == enums.SF.COND and (len(evaled) == 2 or lst.is_nil(lst.cdr(unevaled))):
                # TODO check bool
                cond_var = evaled[1] if len(evaled) >= 2 else None
                if lst.is_nil(lst.cdr(unevaled)) or cond_var:
                    stack.pop()
                    if lst.is_cons_list(head):
                        stack.append(StackItem([], head, stack_e))
                        continue
                    elif symbol.is_symbol(head):
                        res = stack_e.get(head)
                    else:
                        res = head

                    if not stack:
                        return res
                else:
                    stack[-1].unevaled = lst.cdr(unevaled)
                    stack[-1].evaled = evaled[:1]
                    continue
            elif evaled_head == enums.SF.EVAL and lst.is_nil(unevaled):
                # TODO check evaled[1]
                stack.pop()
                if lst.is_cons_list(evaled[1]):
                    stack.append(StackItem([], evaled[1], stack_e))
                    continue
                elif symbol.is_symbol(evaled[1]):
                    res = stack_e.get(evaled[1])
                else:
                    res = evaled[1]

                if not stack:
                    return res
            elif isinstance(evaled_head, ldambda.Lambda) and lst.is_nil(unevaled):
                new_e = environ.Env(evaled_head.env)
                tail_vec = evaled[1:]
                lambda_args = evaled_head.args
                big_break = False
                while True:
                    if lst.is_nil(lambda_args):
                        rest_args = lst.nil
                        for x in tail_vec[::-1]:
                            rest_args = lst.cons(x, rest_args)
                        new_e.define(REST_ARGS, rest_args)
                        break
                    elif not tail_vec:
                        # TODO fix this
                        res = ldambda.Lambda(lambda_args, evaled_head.body, new_e)
                        stack.pop()
                        stack[-1].evaled.append(res)
                        big_break = True
                        break

                    new_e.define(lst.car(lambda_args), tail_vec[0])
                    tail_vec = tail_vec[1:]
                    lambda_args = lst.cdr(lambda_args)

                if big_break:
                    continue

                stack.pop()
                stack.append(StackItem([], evaled_head.body, new_e))
                continue

            elif isinstance(evaled_head, ldambda.Racro):
                if not lst.is_nil(unevaled):
                    res = head
                else:
                    new_e = environ.Env(None)
                    tail_vec = evaled[1:]
                    racro_args = evaled_head.args
                    while True:
                        if lst.is_nil(racro_args):
                            rest_args = lst.nil
                            for x in tail_vec[::-1]:
                                rest_args = lst.cons(x, rest_args)
                            new_e.define(REST_ARGS, rest_args)
                            break
                        elif not tail_vec:
                            # TODO fix this
                            raise ValueError("TODO")

                        new_e.define(lst.car(racro_args), tail_vec[0])
                        tail_vec = tail_vec[1:]
                        racro_args = lst.cdr(racro_args)

                    stack.pop()
                    stack.append(StackItem([], racroexpand(new_e, evaled_head.body), stack_e))
                    continue

            elif lst.is_cons_list(head):
                stack.append(StackItem([], head, stack_e))
                continue
            elif symbol.is_symbol(head):
                res = stack_e.get(head)
            else:
                res = head

            stack[-1].evaled.append(res)


def apply(vec, e):
    if not vec:
        raise ValueError("cant apply empty vec")

    head = vec[0]
    if isinstance(head, enums.OP):
        # TODO empty list
        out = vec[1] if head != enums.OP.SConcat else repr(vec[1])
        for x in vec[2:]:
            out = Operations[head](out, x)
        return out
    elif isinstance(head, enums.PR):
        if not vec:
            return True

        cur = vec[1]
        for next in vec[2:]:
            if not Predicates[head](cur, next):
                return False
            cur = next
        return True

    elif isinstance(head, enums.SF):
        tail = vec[1:]
        # TODO (def a 1 b (+ a 1))
        if head == enums.SF.DEF:
            while tail:
                e.define(tail[0], tail[1])
                tail = tail[2:]
            return lst.nil
        elif head == enums.SF.SET:
            while tail:
                e.set(tail[0], tail[1])
                tail = tail[2:]
            return lst.nil
        elif head == enums.SF.QUOTE:
            # TODO check tail length
            return tail[0]
        elif head == enums.SF.TYPEOF:
            if lst.is_cons_list(tail[0]):
                return "list"
            elif symbol.is_symbol(tail[0]):
                return "symbol"
            else:
                return type(tail[0]).__name__
        elif head == enums.SF.CONS:
            # TODO check tail length
            return lst.cons(tail[0], tail[1])
        elif head == enums.SF.CAR:
            # TODO check tail length
            return lst.car(tail[0])
        elif head == enums.SF.CDR:
            # TODO check tail length
            return lst.cdr(tail[0])
        # elif head == enums.SF.COND:
        # elif head == enums.SF.EVAL:
        elif head == enums.SF.PRINT:
            for x in tail:
                print(repr(x), end=" ")
            print()
        elif head == enums.SF.READ:
            for x in tail:
                print(repr(x), end=" ")
            print()
            user_input = input()
            x, y = parser.parse(user_input)
            return x
        elif head == enums.SF.SYMBOL:
            return symbol.symbol(repr(tail[0]))
        elif head == enums.SF.DO:
            return tail[-1]
        elif head == enums.SF.LAMBDA:
            return ldambda.Lambda(tail[0], tail[1], e)
        elif head == enums.SF.DAMBDA:
            return ldambda.Dambda(tail[0], tail[1])
        elif head == enums.SF.RACRO:
            return ldambda.Racro(tail[0], tail[1])
        # TODO the rest of them


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

            return macroexpand(eval(l.body, new_env, False))
        else:
            return map_list(macroexpand, value)
    else:
        return value
