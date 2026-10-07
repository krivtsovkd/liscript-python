import repl


def main():
    while True:
        print(">>> ", end="")
        cmd = repl.read()
        try:
            _ = repl.evaluate(cmd)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
