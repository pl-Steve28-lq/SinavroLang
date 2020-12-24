from Sinavro.Interpreter.Interpreter import Interpreter
from Sinavro.Parser.Parser import analyze

def Interpret(code, moduleaddr='.', debug=False):
    try:
        intp = Interpreter()
        analyzed = analyze(code, debug)
        imports, tokens = analyzed['use'], analyzed['function'].child
        # return tokens
        for i in imports:
            intp.importFile(i, moduleaddr)
            print("", end='')
        intp.interpret(tokens)
        intp.env.get('main').call(intp, [])
    finally:
        if debug: print(intp.env.values)
    return intp

def InterpretFile(file, moduleaddr='.', debug=False):
    return Interpret(open(file).read(), moduleaddr, debug)

InterpretFile('../example/fibonacci.snvr')
