import sys
import repl
import env


def main():
    repl.evaluate(repl.read_file("stdlib/lib.ls")[0], env, True)

    if len(sys.argv) > 1:
        repl.evaluate(repl.read_file(sys.argv[1])[0], env.runtime_env, True)

    while True:
        cmd, is_file = repl.read(env.runtime_env)
        # try:
        _ = repl.evaluate(cmd, env.runtime_env, is_file)
        # except Exception:
        #     ...


if __name__ == "__main__":
    main()
