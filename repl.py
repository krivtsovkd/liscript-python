import parser
import ast
import eval
import readline
from env import Env

env = Env(None)


def read():
    cmd = input(">>> ")

    if len(cmd) == 0 or cmd[0] != ':':
        return cmd, False

    if cmd[1] == 'l':
        filename = cmd[3:]
        try:
            with open(filename, "r") as file:
                return file.read(), True
        except FileNotFoundError:
            return f"file not found: {filename}", False

    return "command not found", False


def evaluate(text, is_file):
    text = parser.strip_left(text)
    out = None

    while text:
        x, text = parser.parse(text)
        text = parser.strip_left(text)
        try:
            x = eval.eval(x, env)
            out = ast.show_ast(x)
            if not is_file:
                print(out)
        except Exception as e:
            print("Error: ", e)

    if is_file and not (out is None):
        print(out)
