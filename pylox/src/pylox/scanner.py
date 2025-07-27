from .token import Token
from .token_type import TokenType

KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.source_len = len(source)
        self.tokens: list[Token] = []
        self.start_offset = 0
        self.current_offset = 0
        self.line_num = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            # We are at the beginning of the next lexeme
            self.start_offset = self.current_offset
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line_num))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current_offset >= self.source_len

    def scan_token(self):
        char = self.advance()
        match char:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                if self.match("/"):
                    # A comment goes until the end of the line
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":  # Ignore whitespace
                pass
            case "\n":
                self.line_num += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(char):
                    self.number()
                elif self.is_alpha(char):
                    self.identifier()
                else:
                    from .lox import Lox

                    Lox.report(self.line_num, "", "Unexpected character.")

    def advance(self) -> str:
        char = self.source[self.current_offset]
        self.current_offset += 1
        return char

    def add_token(self, token_type: TokenType, literal=None):
        text = self.source[self.start_offset : self.current_offset]
        self.tokens.append(Token(token_type, text, literal, self.line_num))

    def match(self, expected_char: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current_offset] != expected_char:
            return False
        self.current_offset += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current_offset]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line_num += 1
            self.advance()

        if self.is_at_end():
            from .lox import Lox

            Lox.report(self.line_num, "", "Unterminated string.")
            return

        # The closing "
        self.advance()
        # Trim the surrounding quotes
        value = self.source[self.start_offset + 1 : self.current_offset - 1]
        self.add_token(TokenType.STRING, value)

    def is_digit(self, char: str) -> bool:
        return char >= "0" and char <= "9"

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fractional part
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(
            TokenType.NUMBER,
            float(self.source[self.start_offset : self.current_offset]),
        )

    def peek_next(self):
        if self.current_offset + 1 >= self.source_len:
            return "\0"
        return self.source[self.current_offset + 1]

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start_offset : self.current_offset]
        self.add_token(KEYWORDS.get(text, TokenType.IDENTIFIER))

    def is_alpha(self, char: str) -> bool:
        return (
            (char >= "a" and char <= "z")
            or (char >= "A" and char <= "Z")
            or char == "_"
        )

    def is_alpha_numeric(self, char: str) -> bool:
        return self.is_alpha(char) or self.is_digit(char)
