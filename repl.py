import parser
import ast
import eval
import readline
import env


def read_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read(), True
    except FileNotFoundError:
        return f"file not found: {filename}", False


def read(e):
    cmd = input(">>> ")

    if len(cmd) == 0 or cmd[0] != ':':
        return cmd, False

    if cmd[1] == 'l':
        filename = cmd[3:]
        return read_file(filename)

    return "command not found", False


def evaluate(text, e, is_file):
    text = parser.strip_left(text)
    out = None

    while text:
        x = ()
        try:
            x, text = parser.parse(text)
            text = parser.strip_left(text)
        except ValueError as err:
            print("Parser Error:", err)
            break

        try:
            # x = eval.macroexpand(x)
            # print("macroexpand:")
            # print(ast.show_ast(x))
            x = eval.eval(x, env.runtime_env)
            out = ast.show_ast(x)
            if not is_file:
                print(out)
        except ValueError as err:
            print("Eval Error:", err)

    if is_file and not (out is None):
        print(out)
