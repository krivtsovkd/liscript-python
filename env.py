import symbol
from settings import settings


class Env:
    def __init__(self, parent):
        self.parent = parent
        self.values = dict()

    def define(self, sym, val):
        if settings.immutable_mode and symbol.name(sym) in self.values:
            raise ValueError("Cant mutate value: " + symbol.name(sym))
        self.values[symbol.name(sym)] = val

    def get(self, sym):
        cur = self
        while not (cur is None):
            if symbol.name(sym) in cur.values:
                return cur.values[symbol.name(sym)]
            cur = cur.parent

        if settings.auto_quoting:
            return sym
        else:
            raise ValueError("Uninitialized variable: " + symbol.name(sym))

    # TODO setting
    def set(self, sym, val):
        cur = self
        while not (cur is None):
            if symbol.name(sym) in cur.values:
                cur.values[symbol.name(sym)] = val
                return
            cur = cur.parent

        raise ValueError("Undefined symbol: " + symbol.name(sym))

        # if settings.immutable_mode and symbol.name(sym) in self.values:
        #     raise ValueError("Cant mutate value: " + symbol.name(sym))
        # self.values[symbol.name(sym)] = val


env = Env(None)
macro_env = Env(None)
