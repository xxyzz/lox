from .environment import Environment
from .loxcallable import LoxCallable
from .stmt import Function


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment):
        self.closure = closure
        self.declaration = declaration

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def call(self, interpreter, arguments):
        from .interpreter import ReturnException

        environment = Environment(self.closure)
        for arg_name, arg_value in zip(self.declaration.params, arguments):
            environment.define(arg_name.lexeme, arg_value)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
