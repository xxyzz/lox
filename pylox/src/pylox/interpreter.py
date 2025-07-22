from dataclasses import dataclass

from .environment import Environment
from .expr import Binary, Expr, Grouping, Literal, Unary, Variable
from .stmt import Expression, Print, Stmt, Var
from .token import Token
from .token_type import TokenType


@dataclass
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str


class Interpreter:
    environment = Environment()

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

    def execute_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(self.stringfy(value))

    def execute_var(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

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
        return self.environment.get(expr.name)

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
