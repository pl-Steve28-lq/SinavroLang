SinavroException = type("SinavroException", (Exception,), {})

def init(self, val): self.value = val
ReturnTrigger = type("ReturnTrigger", (SinavroException,), {'__init__': init})
