from dataclasses import dataclass
from typing import Any

from .environment import Environment
from .expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    This,
    Unary,
    Variable,
)
from .loxcallable import LoxCallable
from .loxclass import LoxClass
from .loxfunction import LoxFunction
from .loxinstance import LoxInstance
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
from .token_type import TokenType


@dataclass
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str


@dataclass
class ReturnException(RuntimeError):
    value: Any


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.globals.define("clock", Clock())
        self.environment = self.globals
        self.locals: dict[Expr, int] = {}

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as exc:
            from .lox import Lox

            Lox.runtime_error(exc)

    def stringfy(self, obj) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
                return text
        return str(obj)

    def execute(self, stmt: Stmt):
        if isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Print):
            self.execute_print(stmt)
        elif isinstance(stmt, Var):
            self.execute_var(stmt)
        elif isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, If):
            self.execute_if(stmt)
        elif isinstance(stmt, While):
            self.execute_while(stmt)
        elif isinstance(stmt, Function):
            self.execute_function(stmt)
        elif isinstance(stmt, Return):
            self.execute_return(stmt)
        elif isinstance(stmt, Class):
            self.execute_class(stmt)

    def execute_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringfy(value))

    def execute_var(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def execute_if(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def execute_while(self, stmt: While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def execute_function(self, stmt: Function):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def execute_return(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def execute_class(self, stmt: Class):
        self.environment.define(stmt.name.lexeme, None)
        methods = {}
        for method in stmt.methods:
            function = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)

    def evaluate(self, expr: Expr):
        if isinstance(expr, Binary):
            return self.evaluate_binary(expr)
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Unary):
            return self.evaluate_unary(expr)
        elif isinstance(expr, Variable):
            return self.evaluate_variable(expr)
        elif isinstance(expr, Assign):
            return self.evaluate_assign(expr)
        elif isinstance(expr, Logical):
            return self.evaluate_logical(expr)
        elif isinstance(expr, Call):
            return self.evaluate_call(expr)
        elif isinstance(expr, Get):
            return self.evaluate_get(expr)
        elif isinstance(expr, Set):
            return self.evaluate_set(expr)
        elif isinstance(expr, This):
            return self.evaluate_this(expr)

    def evaluate_binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right

                raise LoxRuntimeError(
                    self.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

        return None

    def evaluate_unary(self, expr: Unary):
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right

        return None

    def evaluate_variable(self, expr: Variable):
        return self.look_up_variable(expr.name, expr)

    def look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def evaluate_assign(self, expr: Assign):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

    def evaluate_logical(self, expr: Logical):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        elif not self.is_truthy(left):
            return left

        return self.evaluate(expr.right)

    def evaluate_call(self, expr: Call):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )
        return callee.call(self, arguments)

    def evaluate_get(self, expr: Get):
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def evaluate_set(self, expr: Set):
        object = self.evaluate(expr.object)
        if not isinstance(object, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value

    def evaluate_this(self, expr: This):
        return self.look_up_variable(expr.keyword, expr)

    def is_truthy(self, obj) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def is_equal(self, a, b) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def check_number_operand(self, operator: Token, operand):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth


class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter: Interpreter, arguments):
        import time

        return time.time()

    def __str__(self):
        return "<native fn>"

    def __repr__(self):
        return self.__str__()
