from Sinavro.Interpreter.Exceptions import ReturnTrigger
from Sinavro.Types.Environment import Environment

class Function:
    def __init__(self, function, closure):
        self.function = function
        self.closure = closure

    def arity(self) -> int:
        return len(self.function.args)

    def call(self, interpreter, arguments):
        env = Environment(self.closure, False)
        for arg, argument in zip(self.function.args, arguments):
            env.define(arg[0].name, argument)

        try:
            interpreter.execute_block(self.function.code, env)
        except ReturnTrigger as trigger:
            return trigger.value

        return None
