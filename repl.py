import parser
import ast
import eval
import readline


def read_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read(), True
    except FileNotFoundError:
        return f"file not found: {filename}", False


def read(env):
    cmd = input(">>> ")

    if len(cmd) == 0 or cmd[0] != ':':
        return cmd, False

    if cmd[1] == 'l':
        filename = cmd[3:]
        return read_file(filename)

    return "command not found", False


def evaluate(text, env, is_file):
    text = parser.strip_left(text)
    out = None

    while text:
        try:
            x, text = parser.parse(text)
            text = parser.strip_left(text)
            x = eval.eval(x, env)
            out = ast.show_ast(x)
            if not is_file:
                print(out)
        except ValueError as e:
            print("Error: ", e)

    if is_file and not (out is None):
        print(out)
