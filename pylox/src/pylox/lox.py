class Lox:
    has_error = False

    def main(self):
        import sys

        args = sys.argv
        if len(args) > 2:
            print("Usage: pylox [script]", file=sys.stderr)
        elif len(args) == 2:
            self.run_file(args[1])
        else:
            self.run_prompt()

    def run_file(self, script_path: str):
        with open(script_path) as f:
            self.run(f.read())
        if self.has_error:
            exit(1)

    def run_prompt(self):
        while True:
            line = input("> ")
            if line != "":
                self.run(line)
                self.has_error = False

    def run(self, source: str):
        from .scanner import Scanner

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token)

    def error(self, line_num: int, message: str):
        self.report(line_num, "", message)

    def report(self, line_num: int, where: str, message: str):
        print(f"[line {line_num}] Error{where}: {message}")
        self.has_error = True


def main():
    lox = Lox()
    lox.main()
