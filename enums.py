from enum import Enum


class OP(Enum):
    Add, Sub, Mul, Div, Mod, SConcat = range(6)


class PR(Enum):
    Eq, Gt, Lt, Gte, Lte = range(5)


class SF(Enum):
    (#DEF, SET,
        QUOTE, TYPEOF, CONS, CAR, CDR, IF, PRINT, READ,
     # EVAL, EVALIN, LAMBDA, MACRO,
        SYMBOL, DO) = range(10)


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

    SF.QUOTE: "quote",
    SF.TYPEOF: "typeof",
    SF.CONS: "cons",
    SF.CAR: "car",
    SF.CDR: "cdr",
    SF.IF: "if",
    SF.PRINT: "print",
    SF.READ: "read",
    SF.SYMBOL: "symbol",
    SF.DO: "do",
}

StringToValue = dict(zip(ValuesToString.values(), ValuesToString.keys()))
