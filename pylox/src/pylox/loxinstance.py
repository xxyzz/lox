from typing import Any

from .loxclass import LoxClass
from .token import Token


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: dict[str, Any] = {}

    def __str__(self):
        return self.klass.name + " instance"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        from .interpreter import LoxRuntimeError

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value
