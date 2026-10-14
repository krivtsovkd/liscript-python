import symbol
from settings import settings


class Env:
    def __init__(self):
        self.values = dict()

    def define(self, sym, val):
        if settings.immutable_mode and symbol.name(sym) in self.values:
            raise ValueError("Cant mutate value: " + symbol.name(sym))
        self.values[symbol.name(sym)] = val

    def get(self, sym):
        if settings.auto_quoting:
            return self.values.get(symbol.name(sym), sym)
        else:
            if symbol.name(sym) in self.values:
                return self.values[symbol.name(sym)]
            else:
                raise ValueError("Uninitialized variable: " + symbol.name(sym))

    def set(self, sym, val):
        if settings.immutable_mode and symbol.name(sym) in self.values:
            raise ValueError("Cant mutate value: " + symbol.name(sym))
        self.values[symbol.name(sym)] = val
