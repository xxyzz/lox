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


@dataclass(frozen=True)
class Assign:
    name: Token
    value: Expr


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.left, self.right])


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]


@dataclass(frozen=True)
class Get(Expr):
    object: Expr
    name: Token


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def __str__(self):
        return self.parenthesize("group", [self.expression])


@dataclass(frozen=True)
class Literal(Expr):
    value: Any

    def __str__(self):
        return str(self.value) if self.value is not None else "nil"


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr


@dataclass(frozen=True)
class Super(Expr):
    keyword: Token
    method: Token


@dataclass(frozen=True)
class This(Expr):
    keyword: Token


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def __str__(self):
        return self.parenthesize(self.operator.lexeme, [self.right])


@dataclass(frozen=True)
class Variable(Expr):
    name: Token
