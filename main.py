import sys
import repl
from env import Env

env = Env(None)


def main():
    repl.evaluate(repl.read_file("stdlib/lib.ls")[0], env, True)

    if len(sys.argv) > 1:
        repl.evaluate(repl.read_file(sys.argv[1])[0], env, True)

    while True:
        cmd, is_file = repl.read(env)
        _ = repl.evaluate(cmd, env, is_file)


if __name__ == "__main__":
    main()
