from dataclasses import dataclass
from typing import Any

from .token import Token
from .token_type import TokenType


class Expr:
    def parenthesize(self, name: str, exprs: list["Expr"]) -> str:
        s = f"({name}"
        for expr in exprs:
            s += f" {expr}"
        s += ")"
        return s

    def interpret(self):
        pass


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.left, self.right])

    def interpret(self):
        left = self.left.interpret()
        right = self.right.interpret()

        match self.operator.type:
            case TokenType.GREATER:
                check_number_operands(self.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                check_number_operands(self.operator, left, right)
                return left >= right
            case TokenType.LESS:
                check_number_operands(self.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                check_number_operands(self.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                check_number_operands(self.operator, left, right)
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
                check_number_operands(self.operator, left, right)
                return left / right
            case TokenType.STAR:
                check_number_operands(self.operator, left, right)
                return left * right
            case TokenType.BANG_EQUAL:
                return not is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return is_equal(left, right)

        return None


@dataclass
class Grouping(Expr):
    expression: Expr

    def __str__(self):
        return self.parenthesize("group", [self.expression])

    def interpret(self):
        return self.expression.interpret()


@dataclass
class Literal(Expr):
    value: Any

    def __str__(self):
        return str(self.value) if self.value is not None else "nil"

    def interpret(self):
        return self.value


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.right])

    def interpret(self):
        right = self.right.interpret()
        match self.operator.type:
            case TokenType.BANG:
                return not is_truthy(right)
            case TokenType.MINUS:
                check_number_operand(self.operator, right)
                return -right

        return None


def is_truthy(obj) -> bool:
    if obj is None:
        return False
    if isinstance(obj, bool):
        return obj
    return True


def is_equal(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None:
        return False
    return a == b


@dataclass
class LoxRuntimeError(RuntimeError):
    token: Token
    message: str


def check_number_operand(operator: Token, operand):
    if isinstance(operand, float):
        return
    raise LoxRuntimeError(operator, "Operand must be a number.")


def check_number_operands(operator: Token, left, right):
    if isinstance(left, float) and isinstance(right, float):
        return
    raise LoxRuntimeError(operator, "Operand must be a number.")


def interpret(expression: Expr):
    try:
        value = expression.interpret()
        print(stringfy(value))
    except LoxRuntimeError as exc:
        from .lox import Lox

        Lox.runtime_error(exc)


def stringfy(obj) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, float):
        text = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    return str(obj)
