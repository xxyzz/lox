import sys

from .token import Token
from .token_type import TokenType


class Lox:
    has_error = False

    def main(self):
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
        if Lox.has_error:
            exit(1)

    def run_prompt(self):
        while True:
            line = input("> ")
            if line != "":
                self.run(line)
                Lox.has_error = False

    def run(self, source: str):
        from .parser import Parser
        from .scanner import Scanner

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        expression = parser.parse()

        # Stop if there was a syntax error
        if Lox.has_error:
            return

        print(expression)

    @staticmethod
    def error(token: Token, message: str):
        if token.type == TokenType.EOF:
            Lox.report(token.line_num, " at end", message)
        else:
            Lox.report(token.line_num, f" at '{token.lexeme}'", message)

    @staticmethod
    def report(line_num: int, where: str, message: str):
        print(f"[line {line_num}] Error{where}: {message}", file=sys.stderr)
        Lox.has_error = True


def main():
    lox = Lox()
    lox.main()
