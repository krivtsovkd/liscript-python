import parser
import ast
import eval
import readline


def read():
    cmd = input(">>> ")

    if len(cmd) == 0 or cmd[0] != ':':
        return cmd

    if cmd[1] == 'l':
        filename = cmd[3:]
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            return f"file not found: {filename}"

    return "command not found"


def evaluate(text):
    text = parser.strip_left(text)

    while text:
        x, text = parser.parse(text)
        x = eval.eval(x)
        if not (x is None):
            print(ast.show_ast(x))
