from dataclasses import dataclass
from typing import Any

from .token import Token


class Expr:
    def parenthesize(self, name: str, exprs: list["Expr"]) -> str:
        s = f"({name}"
        for expr in exprs:
            s += f" {expr}"
        s += ")"
        return s


@dataclass
class Assign:
    name: Token
    value: Expr


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.left, self.right])


@dataclass
class Grouping(Expr):
    expression: Expr

    def __str__(self):
        return self.parenthesize("group", [self.expression])


@dataclass
class Literal(Expr):
    value: Any

    def __str__(self):
        return str(self.value) if self.value is not None else "nil"


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.right])


@dataclass
class Variable(Expr):
    name: Token
