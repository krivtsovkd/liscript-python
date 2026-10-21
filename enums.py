from enum import Enum


class OP(Enum):
    Add, Sub, Mul, Div, Mod, SConcat = range(6)


class PR(Enum):
    Eq, Gt, Lt, Gte, Lte = range(5)


class SF(Enum):
    # EVALIN
    (DEF, SET, QUOTE, TYPEOF, CONS, CAR, CDR, COND, PRINT, READ, EVAL, SYMBOL, DO, LAMBDA, DAMBDA, RACRO, PANIC, PYTHON, CURTIME, DEFMACRO, MACROEXPAND) = range(21)


ValuesToString = {
    OP.Add: "+",
    OP.Sub: "-",
    OP.Mul: "*",
    OP.Div: "/",
    OP.Mod: "%",
    OP.SConcat: "++",

    PR.Eq: "=",
    PR.Gt: ">",
    PR.Lt: "<",
    PR.Gte: ">=",
    PR.Lte: "<=",

    SF.DEF: "def",
    SF.SET: "set!",
    SF.QUOTE: "quote",
    SF.TYPEOF: "typeof",
    SF.CONS: "cons",
    SF.CAR: "car",
    SF.CDR: "cdr",
    SF.COND: "cond",
    SF.EVAL: "eval",
    SF.PRINT: "print",
    SF.READ: "read",
    SF.SYMBOL: "symbol",
    SF.DO: "do",
    SF.LAMBDA: "lambda",
    SF.DAMBDA: "dambda",
    SF.RACRO: "racro",
    SF.PANIC: "panic",
    SF.PYTHON: "python?",
    SF.CURTIME: "current-time",
    SF.DEFMACRO: "defmacro",
    SF.MACROEXPAND: "macroexpand",
}

StringToValue = dict(zip(ValuesToString.values(), ValuesToString.keys()))
