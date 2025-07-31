from dataclasses import dataclass

from .loxcallable import LoxCallable
from .loxfunction import LoxFunction


@dataclass
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction]

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        from .loxinstance import LoxInstance

        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name: str) -> LoxFunction | None:
        return self.methods.get(name)
