class Lambda:
    def __init__(self, args, body, env):
        self.args = args
        self.body = body
        self.env = env


class Dambda:
    def __init__(self, args, body):
        self.args = args
        self.body = body
