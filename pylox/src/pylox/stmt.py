from dataclasses import dataclass

from .expr import Expr
from .token import Token


class Stmt:
    pass


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None


@dataclass
class Block(Stmt):
    statements: list[Stmt]
