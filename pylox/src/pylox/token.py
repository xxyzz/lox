from .token_type import TokenType


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal, line_num: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line_num = line_num

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
