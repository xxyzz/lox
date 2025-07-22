from dataclasses import dataclass

from .token import Token


@dataclass
class Environment:
    values = {}

    def define(self, name: str, value):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        from .interpreter import LoxRuntimeError

        raise LoxRuntimeError(name, f"Undefinied variable '{name.lexeme}'.")
