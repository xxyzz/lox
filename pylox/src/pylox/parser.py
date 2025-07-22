from .expr import Binary, Expr, Grouping, Literal, Unary, Variable
from .stmt import Expression, Print, Stmt, Var
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
    #         | IDENTIFIER ;
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

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        self.error(self.peek(), "Expect expression.")

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
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

    # program → statement* EOF ;
    def parse(self) -> list[Stmt]:
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    # declaration → varDecl
    #             | statement ;
    def declaration(self) -> Stmt | None:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    # varDecl → "var" IDENTIFIER ( "=" expression )? ";" ;
    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaraction.")
        return Var(name, initializer)

    # statement → exprStmt
    #           | printStmt;
    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    # printStmt → "print" expression ";" ;
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    # exprStmt → expression ";" ;
    def expression_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(value)
