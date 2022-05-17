from Sinavro.Types.Environment import Environment
from Sinavro.Types.BaseClass import *
from Sinavro.Types.Function import Function
from Sinavro.Parser.SyntaxNode import *
from Sinavro.Parser.Parser import analyze
from Sinavro.Interpreter.Exceptions import *

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.env = self.globals
        self.imports = []

        self.env.define('true', SinavroBool('true'))
        self.env.define('false', SinavroBool('false'))


    ''' Executing Part '''

    def interpret(self, node):
        last_value = None
        try:
            for statement in node:
                last_value = self.execute(statement)
        except SinavroException as e:
            print(e)
        return str(last_value)

    def execute(self, node):
        return node.execute(self) if isinstance(node, Node) else node

    def evaluate(self, item):
        if isinstance(item, SinavroObject):
            return item.value
        elif isinstance(item, Node):
            executed = self.execute(item)
            if isinstance(executed, SinavroObject):
                return executed.value
            else: return executed
        else:
            return item

    def execute_block(self, node, env):
        previous = self.env
        try:
            self.env = env
            for statement in node:
                self.execute(statement)
        except Exception as e: raise e
        finally:
            self.env = previous

    

    ''' Function Part '''

    def visit_function(self, node):
        func = Function(node, self.env)
        self.env.assign(node.name, func)

    def visit_call(self, node):
        n = node.function
        args = list(map(self.execute, node.args))

        if n == "show":
            args = list(map(lambda x: self.stringify(x), node.args))
            print(' '.join(list(map(str, args))))
            return
        if n == "get":
            return input()
        if n == "typeof":
            return args[0].type
        if n == "len":
            if args[0].type in ['array', 'string']:
                return len(args[0].value)
        if n == "readFile":
            return open(args[0].value).read()
        if n == "writeFile":
            try:
                with open(args[0].value, 'w') as f:
                    f.write(args[1].value)
                return self.env.get('true')
            except: return self.env.get('false')
            
        if n == "toInt":
            if isinstance(args[0].value, (float, int)): return int(args[0].value)
            if isinstance(args[0].value, (str)):
                try: return int(args[0].value)
                except: raise SinavroException(f"The string '{args[0].value}' can't be casted as int.")

        callee = self.env.get(n) if isinstance(n, str) else n

        if isinstance(callee, Function):
            if len(args) != callee.arity():
                raise SinavroException(f'Expected {callee.arity()} arguments but got {len(args)}.')
            return callee.call(self, args)
        elif isinstance(callee, SinavroArray):
            return self.arrayindexing(callee, args)
        elif isinstance(callee, SinavroString):
            return callee.value[args[0].value]
        elif isinstance(callee, list):
            return self.arrayindexing(SinavroArray(callee), args)
        else:
            raise SinavroException("Only functions, arrays and strings are callable.")

    def visit_arrayindex(self, node):
        callee = node.array.asList()
        args = list(map(self.execute, node.args)) 
        return self.arrayindexing(callee, args)
    
    def arrayindexing(self, array, args):
        callee = array
        for v in args:
            v = v.value
            if not isinstance(callee, SinavroArray): raise SinavroException(f'Excepted Array but got {callee.type}')
            if abs(v) >= len(callee.value): raise SinavroException(f'Index out of range, [{-v}, {v-1}].')
            callee = callee.value[v]
        return callee

    def visit_stringindex(self, node):
        callee = node.string
        return node.string[int(node.arg.value)]

    def visit_lambda(self, node):
        if isinstance(node.result, Node): res = [ReturnNode([node.result])]
        else: res = node.result
        return Function(FunctionNode(['_lambda', node.args, res]), self.env)

    def visit_lambdacall(self, node):
        L = self.visit_lambda(node.lambdaf)
        return L.call(self, node.args)
        
        
    def visit_return(self, node):
        value = self.execute(node.ret) if node else None
        raise ReturnTrigger(value)


    
    ''' Assignment Part '''
    
    def visit_assign(self, node):
        self.env.assign(node.name.name, self.execute(node.value))

    def visit_var(self, node):
        return self.env.get(node.name)

    def visit_literal(self, node):
        t = node.type
        v = node.value
        if t == 'int': return SinavroInt(int(v))
        elif t == 'string': return SinavroString(v)
        elif t == 'float': return SinavroFloat(float(v))
        elif t == 'bool': return SinavroBool(v == 'true')
        elif t == 'array':
            return SinavroArray(list(map(self.evaluate, v)))

    def visit_arrayassign(self, node):
        n = list(map(self.evaluate, node.index))
        value = self.evaluate(node.value)
        arr = self.env.get(node.array)
        item = arr
        for i in range(len(n)):
            v = n[i]
            if i == len(n)-1:
                item.value[v] = value
            else: item = item.value[v]



    ''' Statement Part '''

    def visit_if(self, node):
        if is_truthy(self.execute(node.cond)):
            self.execute_block(node.code, Environment(self.env))
        elif node.elsecode:
            self.execute_block(node.elsecode, Environment(self.env))

    def visit_while(self, node):
        while is_truthy(self.evaluate(node.cond)):
            self.execute_block(node.code, Environment(self.env))

    def visit_for(self, node):
        env = Environment(self.env)
        self.execute_block(node.init, env)
        while is_truthy(self.evaluate(node.cond)):
            self.execute_block(node.code, env)
            for i in node.act:
                self.execute_block([i], env)
                if not is_truthy(self.evaluate(node.cond)): break

    def visit_repeat(self, node):
        times = self.evaluate(node.times)
        if isinstance(times, int):
            for i in [0]*times:
                self.execute_block(node.code, Environment(self.env))

    def visit_ternary(self, node):
        if is_truthy(self.execute(node.cond)):
            return self.evaluate(node.true)
        else: return self.evaluate(node.false)

    def visit_foreach(self, node):
        env = Environment(self.env)
        if isinstance(node.array, str): array = self.env.get(node.array)
        else: array = self.execute(node.array)
        env.define(node.var, self.execute(CallNode([array, [SinavroInt(0)]])))
        for i in range(len(array.value)):
            env.assign(node.var, self.execute(CallNode([array, [SinavroInt(i)]])))
            self.execute_block(node.code, env)
            
        
        
    ''' Operator Part '''
    
    def visit_binop(self, node):
        A, op, B = node.left, node.operator, node.right
        a, b = map(self.evaluate, [A, B])

        if op == '+':
            if checkAll(str, a, b): return SinavroString(a+b)
            if checkAll(bool, a, b): return SinavroBool(a or b)
            if checkAll(int, a, b): return SinavroInt(a+b)
            if checkAll((int, float), a, b): return SinavroFloat(a+b)
            if isinstance(a, list): return SinavroArray(a+[b])
        if op == '-':
            if checkAll(int, a, b): return SinavroInt(a-b)
            if checkAll((int, float), a, b): return SinavroFloat(a-b)
        if op == '*':
            if checkAll(int, a, b): return SinavroInt(a*b)
            if checkAll((int, float), a, b): return SinavroFloat(a*b)
            if checkAll(bool, a, b): return SinavroBool(a and b)
            if checkEach((a, str), (b, int)): return SinavroString(a*b)
            if checkEach((a, list), (b, int)): return SinavroArray(a*b)
        if op == '/':
            if checkAll((int, float), a, b) and\
               is_truthy(b): return SinavroFloat(a/b)
            raise SinavroException("Dividing by 0 is not allowed.")
        if op == '**':
            if isinstance(b, int):
                return SinavroInt(a**b) if isinstance(a, int) else SinavroFloat(a**b)
            elif a > 0:
                return SinavroFloat(a**b)
            elif a == 0 and not b < 0:
                return SinavroInt(int(b==0))
            raise SinavroException("Float power of negative is not allowed.")
        if op == '%':
            if checkAll(int, a, b): return SinavroInt(a%b)
        if op == '<':
            if checkAll((int, float), a, b): return SinavroBool(a < b)
        if op == '<=':
            if checkAll((int, float), a, b): return SinavroBool(a <= b)
        if op == '>':
            if checkAll((int, float), a, b): return SinavroBool(a > b)
        if op == '>=':
            if checkAll((int, float), a, b): return SinavroBool(a >= b)
        if op == '==':
            return SinavroBool(a == b)
        if op == '!=':
            return SinavroBool(a != b)
        if op == '+=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '+', B]])))
                return
        if op == '-=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '-', B]])))
                return
        if op == '*=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '*', B]])))
                return
        if op == '/=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '/', B]])))
                return
        if op == '%=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '%', B]])))
                return
        if op == '**=':
            if isinstance(A, VarNode):
                self.env.assign(A.name, self.visit_binop(BinOpNode([[A, '**', B]])))
                return
        typeerror2(op, a, b)

    def visit_unop(self, node):
        op, right = node.operator, node.right
        a = self.execute(right)
        if op == '-':
            if isinstance(a, int): return SinavroInt(-a)
            if isinstance(a, float): return SinavroFloat(-a)
        if op == '!':
            if isinstance(a, (int, float, bool)): return SinavroBool(not is_truthy(a))
        if op == '~':
            if isinstance(a, int): return SinavroInt(~a)
        typeerror1(op, a)



    ''' Import Part '''
    
    def importFile(self, name, addr='.'):
        file = analyze(open(f"{addr}/{name}.snvr").read())
        filename = lambda name: name.split("/")[-1] if "/" in name else name
        self.interpret(file['function'].child)
        self.imports.append(filename(name))
        if file['use']:
            for i in file['use']:
                if not filename(i) in self.imports: self.importFile(i)
        self.env.get('main').call(self, [])


    def stringify(self, obj):
        if isinstance(obj, SinavroArray): return str(obj.value).replace("[", "<").replace("]", ">")
        elif isinstance(obj, SinavroObject): return obj.value
        elif isinstance(obj, Node): return self.stringify(self.execute(obj))
        else: return self.evaluate(obj)


def is_truthy(obj):
    if not obj: return False
    if obj == 'False': return False
    if isinstance(obj, SinavroObject):
        if obj.type == 'int' and obj.value != 0: return True
        elif obj.type == 'float' and obj.value != 0.0: return True
        elif obj.type == 'bool' and obj.value == True: return True
        elif obj.type == 'array' and obj.value != []: return True
        else: return False

    return True

def checkEach(*x):
    return all(map(lambda x: isinstance(x[0], x[1]), x))
def checkAll(t, *x):
    return all(map(lambda x: isinstance(x, t), x))
def types(t):
    ty = type(t)
    return ty if ty != 'str' else 'string'
def typeerror1(op, a):
    raise SinavroException(f"Using '{op}' operator with type {types(a)} is not allowed.")
def typeerror2(op, a, b):
    raise SinavroException(f"Using '{op}' operator with type ({types(a)}, {types(b)}) is not allowed.")
