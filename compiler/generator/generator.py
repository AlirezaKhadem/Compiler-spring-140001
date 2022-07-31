from lark import Visitor, Tree

VARIABLE_DECLARATION = 'variabledecl'
FUNCTION_DECLARATION = 'functiondecl'
CLASS_DECLARATION = 'classdecl'
STATEMENT_BLOCK = 'stmtblock'
RETURN_STATEMENT = 'returnstmt'
DECLARATION = 'decl'
IMPLEMENTS = 'implements'
VARIABLE = 'variable'
FORMALS = 'formals'
FIELD = 'field'
EXTENDS = 'EXTENDS'
EXPR = EXPR
INTT = 'INTT'
BOOL = 'BOOL'
DOUBLE = 'DOUBLE'
STRING = 'STRING'
PLUS = 'PLUS'
MINUS = 'MINUS'
MULT = 'MULT'
DIV = 'DIV'
MOD = 'MOD'
MORE = 'MORE'
LESS = 'LESS'
MORQ = 'MORQ'
LESQ = 'LESQ'
EQUALS = 'EQUALS'
NEQ = 'NEQ'
AND = 'AND'
OR = 'OR'
START = 'start'
PUBLIC = 'PUBLIC'
PRIVATE = 'PRIVATE'
PROTECTED = 'PROTECTED'
ACTUALS = 'actuals'
VOID = 'VOID'
LVALUE = 'lvalue'
NULL = 'NULL'
DOT = 'DOT'
NEWARRAY = 'NEWARRAY'
NEW = 'NEW'
READINTEGER = 'READINTEGER'
READLINE = 'READLINE'
ITOD = 'ITOD'
DTOI = 'DTOI'
ITOB = 'ITOB'
BTOI = 'BTOI'
THIS = 'THIS'
LEFTPAR = 'LEFTPAR'
PUSH = 'PUSH'
POP = 'POP'
ALLOC = 'ALLOC'
CONCAT = 'CONCAT'
NOT = 'NOT'
SP = "$sp"
PRINT = 'print'
EXPR = 'expr'

class Generator(Visitor):

    def __init__(self):
        self.code = []

    def clean(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree):
                ch.code = None
        tree.code = self.code
        self.code = []

    def stmtblock(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree) and ch.data == 'stmt':
                self.add_command(ch.code, '', '')
        self.clean(tree)

    def stmt(self, tree):
        if isinstance(tree.children[0], Tree):
            self.add_command(tree.children[0].code, '', '')
        self.clean(tree)

    def whilestmt(self, tree):
        self.add_label(tree.label)
        self.add_command(tree.children[2].code, '', '')
        self.add_command("if0", tree.children[2].var, "goto", self.index_label(tree.label + 1))
        self.add_command(tree.children[4].code, '', '')
        self.add_command("goto", self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def forstmt(self, tree):
        if tree.exps[0] is not None:
            self.add_command(tree.exps[0].code, '', '')
        self.add_label(tree.label)
        self.add_command(tree.exps[1].code, '', '')
        self.add_command("if0", tree.exps[1].var, "goto", self.index_label(tree.label + 1))
        self.add_command(tree.children[-1].code, '', '')
        if tree.exps[2] is not None:
            self.add_command(tree.exps[2].code)
        self.add_command("goto", self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def continuestmt(self, tree):
        self.add_command("goto", tree.parent_loop.label)
        self.clean(tree)

    def breakstmt(self, tree):
        self.add_command("goto", tree.parent_loop.label + 1)
        self.clean(tree)

    def ifstmt(self, tree):
        self.add_command(tree.children[2].code, '', '')
        self.add_command("if0", tree.children[2].var, "goto", self.index_label(tree.label))
        self.add_command(tree.children[4].code, '', '')
        self.add_label(tree.label)
        if len(tree.children) > 4:
            self.add_command(tree.children[6].code, '', '')
        self.clean(tree)

    def printstmt(self, tree):
        self.print_expression(tree.children[2])
        self.add_command(PRINT, STRING, '\n')
        self.clean(tree)

    def print_expression(self, tree):
        if tree.children[0].data == EXPR:
            self.add_command(PRINT, tree.children[0].expression_type, tree.children[0].var_num)
        else:
            self.print_expression(tree.children[0])
            self.print_expression(tree.children[2])

    def decl(self, tree):
        self.code = tree.children[0].code
        self.clean(tree)

    def add_label(self, index):
        self.add_command(self.index_label(index) + ":")

    def index_label(self, index):
        return "L" + str(index)

    def expr(self, tree):
        if isinstance(tree.children[0], Tree):
            if tree.children[0].data == 'constant':
                self.add_command(tree.parent.var_num, "=", tree.children[0].children[0].value)
            elif tree.children[0].data == EXPR:
                op = None
                if tree.children[0].expression_type == STRING:
                    op = CONCAT
                else:
                    op = tree.children[1].type
                self.add_command(tree.var_num, "=", tree.children[0].var_num, op, tree.children[2].var_num)
            else:
                if len(tree.children) == 1:
                    self.add_command(tree.var_num, "=", tree.children[0].var_num)
                else:
                    self.add_command(tree.children[0].var_num, "=", tree.children[2].var_num)
        elif tree.children[0].type in [MINUS, NOT]:
            self.add_command(tree.var_num, '=', tree.children[1].type, tree.children[1].var_num)
        elif tree.children[0].type == LEFTPAR:
            self.add_command(tree.var_num, "=", tree.children[1].var_num)
        elif tree.children[0].type == NEWARRAY:
            self.add_command(tree.children[2].type)
        elif tree.children[0].type in [ITOD, ITOB, DTOI, BTOI]:
            self.add_command(tree.var_num, "=", tree.children[0].type, tree.children[2].var_num)
        elif tree.children[0].type in [READINTEGER, READLINE]:
            self.add_command(tree.var_num, "=", tree.children[0].type)
        self.clean(tree)

    def add_command(self, *args, sep=' ', end='\n'):
        for i in range(len(args)):
            self.code = self.code + args[i]
            if i < len(args) - 1:
                self.code = self.code + sep
            else:
                self.code = self.code + end


class final_generator:


    def __init__(self, code):
        self.code = code
        self.final_code = ""

    def reserve(self, n):
        self.addi(SP, SP, "-"+n)

    def free(self, n):
        self.addi(SP, SP, n)

    def addi(self, dest, r1, r2):
        self.add_command("addi", dest+','+r1+','+r2)

    def operation(self, t1, t2, dest, op):
        self.load_word()

    def load_word(self, reg, address, offset = ""):
        self.add_command('lw', reg+',', offset+'('+address+')')

    def save_word(self, reg, address, offset = ""):
        self.add_command('sw', reg+',', offset+'('+address+')')

    def add_command(self, *args):
        for i in range(len(args)):
            if i == len(args)-1:
                self.final_code = self.final_code + args[i] + '\n'
            else:
                self.final_code = self.final_code + args[i] + ' '
