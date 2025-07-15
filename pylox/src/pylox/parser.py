from .expr import Binary, Expr, Grouping, Literal, Unary
from .token import Token
from .token_type import TokenType


class ParseError(RuntimeError):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def match(self, types: TokenType) -> bool:
        if self.check(types):
            self.advance()
            return True
        return False

    def check(self, types: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type in types

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    # expression → equality
    def expression(self) -> Expr:
        return self.equality()

    # equality → comparison ( ( "!=" | "==" ) comparison )*
    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL | TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    # comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER
            | TokenType.GREATER_EQUAL
            | TokenType.LESS
            | TokenType.LESS_EQUAL
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    # term → factor ( ( "-" | "+" ) factor )*
    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS | TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    # factor → unary ( ( "/" | "*" ) unary )*
    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH | TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    # unary → ( "!" | "-" ) unary
    #       | primary
    def unary(self) -> Expr:
        if self.match(TokenType.BANG | TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    # primary → NUMBER | STRING | "true" | "false" | "nil"
    #         | "(" expression ")"
    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER | TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        self.error(self.peek(), "Expect expression.")

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(TokenType.RIGHT_PAREN):
            return self.advance()
        self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        from .lox import Lox

        Lox.error(token, message)
        raise ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if (
                self.peek().type
                in TokenType.CLASS
                | TokenType.FUN
                | TokenType.VAR
                | TokenType.FOR
                | TokenType.IF
                | TokenType.WHILE
                | TokenType.PRINT
                | TokenType.RETURN
            ):
                return

            self.advance()

    def parse(self) -> Expr | None:
        try:
            return self.expression()
        except ParseError:
            return None
