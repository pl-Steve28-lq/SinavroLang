from Sinavro.Interpreter.Exceptions import SinavroException

class Environment:
    def __init__(self, enclosing=None, send=True):
        self.values = {}
        self.enclosing = enclosing
        self.send = send

    def define(self, key, value):
        self.values[key] = value

    def assign(self, key, value):
        if key in self.values:
            self.values[key] = value
            return

        if self.enclosing and self.send:
            self.enclosing.assign(key, value)
            return

        self.define(key, value)

    def get(self, key):
        if key in self.values:
            return self.values[key]

        if self.enclosing:
            return self.enclosing.get(key)

        raise SinavroException(f"Cannot find variable '{key}'")
        
