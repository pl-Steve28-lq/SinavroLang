from pyparsing import *
from Sinavro.Parser.SyntaxNode import *


ParserElement.enablePackrat()
sk = lambda x: Suppress(Keyword(x))



import sys
sys.setrecursionlimit(5000)




LPAREN = Suppress(Literal('('))
RPAREN = Suppress(Literal(')'))
NEG = Literal('-')
SEMICOLON = Suppress(Literal(';'))

# Constant Keywords
use = Keyword('use')
func = sk('func')

using = (use - Word(alphas + '_' + '/', alphanums + '_' + '/'))

# Built-in Types
literal = Forward()
expr = Forward()

vartype = ( Keyword('int') | Keyword('float') | Keyword('string') | Keyword('bool') | Keyword('Function') | Keyword('array'))
string = QuotedString('"', escChar='\\') | QuotedString('\'', escChar='\\')
integer = (Regex(r'0x[0-9a-fA-F]+') | Regex(r'\d+'))
floats = Regex(r'\d+(\.\d*)([eE]\d+)?')
array = Suppress(Literal('<')) + Group(Optional(delimitedList(literal | expr))) + Suppress(Literal('>'))
literal << ( string | floats | integer | array )

# Variables

name = Word(alphas + '_' + '.', alphanums + '_' + '.', asKeyword=True) # VarNode
name.ignore(use)

call = Forward()
ternary = Forward()

expr << infixNotation(call | name | literal | LPAREN + ternary + RPAREN, [
        (oneOf('- ! ~'), 1, opAssoc.RIGHT, UnOpNode),
        (oneOf('* / % **'), 2, opAssoc.LEFT, BinOpNode),
        (oneOf('+ -'), 2, opAssoc.RIGHT, BinOpNode),
        (oneOf('< <= > >='), 2, opAssoc.LEFT, BinOpNode),
        (oneOf('== !='), 2, opAssoc.LEFT, BinOpNode),
    ]
) # BinOpNode, UnOpNode
expr |= LPAREN + expr + RPAREN

ternary << ( expr('true') + sk('if') + expr('cond') + sk('else') + expr('false') )

args = Optional(delimitedList(expr))
funccall = (name("name") + LPAREN - Group(args)("args") - RPAREN) # CallNode
arrayindex = (array("array") + LPAREN - Group(args)("args") - RPAREN) # ArrayIndexNode
stringindex = (string("string") + LPAREN - args("args") - RPAREN) # StringIndexNode

call << (funccall | arrayindex | stringindex)

assign = (name + Suppress(Literal('=')) - expr) # AssignNode

blockst = Forward()
ifst = Forward()
whilest = Forward()
forst = Forward()
repeatst = Forward()
retst = Forward()
function = Forward()

st = (function | blockst | ifst | whilest | forst | repeatst | ((
    retst |
    Keyword('break') |
    assign |
    expr
    ))
)
blockst << Suppress(Literal('[')) - Group(ZeroOrMore(st)) - Suppress(Literal(']'))

elsest = (sk('else') - st)
ifst << (sk('if') - expr - st - Optional(elsest)) # IfNode
whilest << (sk('while') + expr + st) # WhileNode
forst << (sk('for') - LPAREN + Group(delimitedList(Optional(assign, None))) + SEMICOLON +
                 Optional(expr, None) + SEMICOLON +
                 Group(delimitedList(Optional(assign, None))) + RPAREN + st) # ForNode
repeatst << (sk('repeat') - expr - st) # RepeatNode
retst << (sk('return') - Optional(expr)) # ReturnNode

typedecl = Optional(sk("->") + vartype)

function << func + name("name") +\
           LPAREN - Group(Optional(delimitedList(Group(name + typedecl))))("args") + RPAREN -\
           typedecl("type") - ZeroOrMore(blockst)("code")
function.ignore("::" + SkipTo("\n")) # FunctionNode
function.ignore("##" + SkipTo("##"))



# Parsing with Nodes
retst.setParseAction(ReturnNode)
function.setParseAction(FunctionNode)
funccall.setParseAction(CallNode)
arrayindex.setParseAction(ArrayIndexNode)
stringindex.setParseAction(StringIndexNode)

assign.setParseAction(AssignNode)
repeatst.setParseAction(RepeatNode)
name.setParseAction(VarNode)
ifst.setParseAction(IfNode)
forst.setParseAction(ForNode)
whilest.setParseAction(WhileNode)

integer.setParseAction(IntNode)
string.setParseAction(StringNode)
floats.setParseAction(FloatNode)
array.setParseAction(ArrayNode)
using.setParseAction(ImportNode)
ternary.setParseAction(TernaryNode)



def printAll(*x):
    for i in x: print(i);print()

def analyze(code, debug=False):
    impres = []
    for item, _, _ in using.scanString(code):
        if debug: print(item[0].name)
        impres.append(item[0].name)
    res = []
    for item, _, _ in function.scanString(code):
        if debug: print(item[0].code)
        res.append(item[0])
    return {'use': impres, 'function': MainNode(res)}
        
