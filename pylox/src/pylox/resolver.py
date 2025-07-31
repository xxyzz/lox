from enum import Enum, auto

from .expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Logical,
    Set,
    This,
    Unary,
    Variable,
)
from .stmt import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Var,
    While,
)
from .token import Token


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()


class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve_block(self, stmt: Block):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def resolve_statements(self, statements: list[Stmt]):
        for statement in statements:
            self.resolve_statement(statement)

    def resolve_statement(self, statement: Stmt):
        if isinstance(statement, Block):
            self.resolve_block(statement)
        elif isinstance(statement, Var):
            self.resolve_var(statement)
        elif isinstance(statement, Expression):
            self.resolve_expression(statement)
        elif isinstance(statement, Function):
            self.resolve_function(statement, FunctionType.FUNCTION)
        elif isinstance(statement, If):
            self.resolve_if(statement)
        elif isinstance(statement, Print):
            self.resolve_print(statement)
        elif isinstance(statement, Return):
            self.resolve_return(statement)
        elif isinstance(statement, While):
            self.resolve_while(statement)
        elif isinstance(statement, Class):
            self.resolve_class(statement)

    def resolve_expr(self, expr: Expr):
        if isinstance(expr, Variable):
            self.resolve_variable(expr)
        elif isinstance(expr, Assign):
            self.resolve_assign(expr)
        elif isinstance(expr, Binary):
            self.resolve_bianry(expr)
        elif isinstance(expr, Call):
            self.resolve_call(expr)
        elif isinstance(expr, Grouping):
            self.resolve_grouping(expr)
        elif isinstance(expr, Logical):
            self.resolve_logical(expr)
        elif isinstance(expr, Unary):
            self.resolve_unary(expr)
        elif isinstance(expr, Get):
            self.resolve_get(expr)
        elif isinstance(expr, Set):
            self.resolve_set(expr)
        elif isinstance(expr, This):
            self.resolve_this(expr)

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            from .lox import Lox

            Lox.error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_var(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def resolve_variable(self, expr: Variable):
        if len(self.scopes) > 0 and not self.scopes[-1].get(expr.name.lexeme, True):
            from .lox import Lox

            Lox.error(expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr: Expr, name: Token):
        for index, scope in enumerate(self.scopes[::-1]):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, index)
                break

    def resolve_assign(self, expr: Assign):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def resolve_function(self, stmt: Function, function_type: FunctionType):
        self.declare(stmt.name)
        self.define(stmt.name)
        enclosing_function = self.current_function
        self.current_function = function_type
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(stmt.body)
        self.end_scope()
        self.current_function = enclosing_function

    def resolve_expression(self, stmt: Expression):
        self.resolve_expr(stmt.expression)

    def resolve_if(self, stmt: If):
        self.resolve_expr(stmt.condition)
        self.resolve_statement(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_statement(stmt.else_branch)

    def resolve_print(self, stmt: Print):
        self.resolve_expr(stmt.expression)

    def resolve_return(self, stmt: Return):
        from .lox import Lox

        if self.current_function == FunctionType.NONE:
            Lox.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                Lox.error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve_expr(stmt.value)

    def resolve_while(self, stmt: While):
        self.resolve_expr(stmt.condition)
        self.resolve_statement(stmt.body)

    def resolve_bianry(self, expr: Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def resolve_call(self, expr: Call):
        self.resolve_expr(expr.callee)
        for argument in expr.arguments:
            self.resolve_expr(argument)

    def resolve_grouping(self, expr: Grouping):
        self.resolve_expr(expr.expression)

    def resolve_logical(self, expr: Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def resolve_unary(self, expr: Unary):
        self.resolve_expr(expr.right)

    def resolve_class(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        self.current_class = enclosing_class

    def resolve_get(self, expr: Get):
        self.resolve_expr(expr.object)

    def resolve_set(self, expr: Set):
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)

    def resolve_this(self, expr: This):
        if self.current_class != ClassType.CLASS:
            from .lox import Lox

            Lox.error(expr.keyword, "Can't use 'this' outside of a class.")
        else:
            self.resolve_local(expr, expr.keyword)
