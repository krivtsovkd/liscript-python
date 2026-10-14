import repl


def main():
    while True:
        cmd, is_file = repl.read()
        try:
            _ = repl.evaluate(cmd, is_file)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
