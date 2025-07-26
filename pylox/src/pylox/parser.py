from .expr import Assign, Binary, Expr, Grouping, Literal, Logical, Unary, Variable
from .stmt import Block, Expression, If, Print, Stmt, Var, While
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

    # expression → assignment ;
    def expression(self) -> Expr:
        return self.assignment()

    # assignment → IDENTIFIER "=" assignment
    #            | logic_or ;
    def assignment(self) -> Expr:
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")

        return expr

    # logic_or → logic_and ( "or" logic_and )* ;
    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

    # logic_and → equality ( "and" equality )* ;
    def logic_and(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

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
    #           | forStmt
    #           | ifStmt
    #           | printStmt
    #           | whileStmt
    #           | block;
    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        return self.expression_statement()

    # ifStmt → "if" "(" expression ")" statement
    #        ( "else" statement )? ;
    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

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

    # block → "{" declaration* "}" ;
    def block(self) -> list[Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    # whileStmt → "while" "(" expression ")" statement ;
    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    # forStmt → "for" "(" ( varDecl | exprStmt | ";" )
    #           expression? ";"
    #           expression? ")" statement ;
    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body
