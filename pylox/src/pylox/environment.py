from .token import Token


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing: Environment | None = enclosing

    def define(self, name: str, value):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        from .interpreter import LoxRuntimeError

        raise LoxRuntimeError(name, f"Undefinied variable '{name.lexeme}'.")

    def assign(self, name: Token, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            from .interpreter import LoxRuntimeError

            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def ancestor(self, distance: int):
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def assign_at(self, distance: int, name: Token, value):
        self.ancestor(distance).values[name.lexeme] = value
