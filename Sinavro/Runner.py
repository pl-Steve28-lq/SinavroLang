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
        try: intp.env.get('main').call(intp, [])
        except: pass
    except Exception as e: raise e
    finally:
        if debug: print(intp.env.values)
    return intp

def InterpretFile(file, moduleaddr='.', debug=False):
    return Interpret(open(file).read(), Interpreter(), moduleaddr, debug)


def InterpretLine(moduleaddr='.', debug=False):
    intp = Interpreter()
    while True:
        code = ''
        print()
        enter = 0
        while enter < 2:
            a = input('>>> ')
            if a == '': enter += 1
            else: enter = 0
            code += a + '\n'
        if code.strip() == 'exit': break
        try:
            Interpret(code, intp, moduleaddr, debug)
        except Exception as e: print(f"Error: {e}")
        finally: continue
