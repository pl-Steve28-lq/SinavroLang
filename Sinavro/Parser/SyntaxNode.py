class Node(object):
    parent = None
    scope = {}
    
    def __repr__(self):
        return f"<{self.__class__.__name__}>"




class MainNode(Node):
    def __init__(self, functions):
        self.child = functions




class FunctionNode(Node):
    def __init__(self, tokens):
        if len(list(tokens)) == 3:
            self.name, self.args, self.code = tokens
            self.type = 'none'
        else:
            self.name, self.args, self.type, self.code = tokens
        
        
    def execute(self, env):
        return env.visit_function(self)




class LambdaNode(Node):
    def __init__(self, tokens):
        self.args, self.result = tokens


    def execute(self, env):
        return env.visit_lambda(self)




class LambdaCallNode(Node):
    def __init__(self, tokens):
        self.lambdaf, self.args = tokens


    def execute(self, env):
        return env.visit_lambdacall(self)




class ForNode(Node):
    def __init__(self, tokens):
        self.init, self.cond, self.act, self.code = tokens
        

    def execute(self, env):
        return env.visit_for(self)




class ForEachNode(Node):
    def __init__(self, tokens):
        self.var, self.array, self.code = tokens


    def execute(self, env):
        return env.visit_foreach(self)




class RepeatNode(Node):
    def __init__(self, tokens):
        self.times, self.code = tokens
        

    def execute(self, env):
        return env.visit_repeat(self)




class IfNode(Node):
    def __init__(self, tokens):
        if len(tokens) == 3:
            self.cond, self.code, self.elsecode = tokens
        elif len(tokens) == 2:
            self.cond, self.code = tokens
            self.elsecode = None
        

    def execute(self, env):
        return env.visit_if(self)




class TernaryNode(Node):
    def __init__(self, tokens):
        self.true, self.cond, self.false = tokens


    def execute(self, env):
        return env.visit_ternary(self)




class WhileNode(Node):
    def __init__(self, tokens):
        self.cond, self.code = tokens
        

    def execute(self, env):
        return env.visit_while(self)




class CallNode(Node):
    def __init__(self, tokens):
        self.function, self.args = tokens
        

    def execute(self, env):
        return env.visit_call(self)




class ArrayIndexNode(Node):
    def __init__(self, tokens):
        self.array, self.args = tokens


    def execute(self, env):
        return env.visit_arrayindex(self)




class StringIndexNode(Node):
    def __init__(self, tokens):
        self.string, self.arg = tokens


    def execute(self, env):
        return env.visit_stringindex(self)




class AssignNode(Node):
    def __init__(self, tokens):
        self.name, self.value = tokens
        
        
    def execute(self, env):
        return env.visit_assign(self)




class ArrayAssignNode(Node):
    def __init__(self, tokens):
        self.array, self.index = tokens[0].function, tokens[0].args
        self.value = tokens[1]


    def execute(self, env):
        return env.visit_arrayassign(self)




class BinOpNode(Node):
    def __init__(self, tokens):
        self.left, self.operator, self.right = tokens[0]
        self.child = list(tokens[0])

    def execute(self, env):
        return env.visit_binop(self)




class UnOpNode(Node):
    def __init__(self, tokens):
        self.operator, self.right = tokens[0]
        self.child = list(tokens[0])

    def execute(self, env):
        return env.visit_unop(self)




class ReturnNode(Node):
    def __init__(self, tokens):
        self.ret = tokens[0]
        self.child = [tokens[0]]

    def execute(self, env):
        return env.visit_return(self)




class VarNode(Node):
    def __init__(self, tokens):
        self.name = tokens[0]
        self.child = list(tokens[0])

    def execute(self, env):
        return env.visit_var(self)




class ImportNode(Node):
    def __init__(self, tokens):
        self.name = tokens[-1]

    def execute(self, env):
        return env.visit_import(self)



class ArrayNode(Node):
    def __init__(self, tokens):
        self.items = tokens

    def execute(self, env):
        return env.visit_array(self)




def Types(typename):
    class LiteralNode(Node):
        def __init__(self, tokens):
            self.value = tokens[0]
            self.type = typename

        def execute(self, env):
            return env.visit_literal(self)
    return LiteralNode




IntNode = Types('int')
StringNode = Types('string')
FloatNode = Types('float')
BoolNode = Types('bool')
ArrayNode = Types('array')
