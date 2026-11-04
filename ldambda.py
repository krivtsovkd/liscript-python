class Lambda:
    def __init__(self, args, body, env):
        self.args = args
        self.body = body
        self.env = env


class Dambda:
    def __init__(self, args, body):
        self.args = args
        self.body = body


class Racro:
    def __init__(self, args, body):
        self.args = args
        self.body = body


class LazyCall:
    def __init__(self, exp, env):
        self.exp = exp
        self.env = env
