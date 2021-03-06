from Sinavro.Interpreter.Interpreter import Interpreter
from Sinavro.Parser.Parser import analyze

def Interpret(code, intp, moduleaddr='.', debug=False):
    try:
        analyzed = analyze(code, debug)
        imports, tokens = analyzed['use'], analyzed['function'].child
        # return tokens
        for i in imports:
            intp.importFile(i, moduleaddr)
        intp.interpret(tokens)
        intp.env.get('main').call(intp, [])
    finally:
        if debug: print(intp.env.values)
    return intp

def InterpretFile(file, moduleaddr='.', debug=False):
    return Interpret(open(file).read(), Interpreter(), moduleaddr, debug)


def InterpretLine(moduleaddr='.', debug=False):
    intp = Interpreter()
    while True:
        code = input()
        if code == 'exit': break
        try:
            Interpret(code, intp, moduleaddr, debug)
        finally: continue
