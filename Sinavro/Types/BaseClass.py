class SinavroObject: pass

def init(self, val): self.value = val
gencls = lambda n: type(f'Sinavro{n.title()}', (SinavroObject,), {'__init__': init, 'type': n})

SinavroInt = gencls('int')
SinavroFloat = gencls('float')
SinavroString = gencls('string')
SinavroBool = gencls('bool')
SinavroArray = gencls('array')
