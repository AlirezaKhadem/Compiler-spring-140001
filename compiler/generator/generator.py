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
EXPR = 'expr'
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
RESERVE = 'RESERVE'
CONCAT = 'CONCAT'
NOT = 'NOT'
SP = "$sp"
PRINT = 'PRINT'
FREE = 'FREE'
SET = '='
RETURN_VALUE = 'retval'
CALL = 'call'
RETURN = 'RETURN'
EXIT = 'EXIT'
ZERO = '$zero'
GOTO = "goto"
IF0 = "if0"
NEXTLINE = 'nextline'
T0 = "$t0"
T1 = "$t1"
T2 = "$t2"
RA = "$ra"

class Generator(Visitor):

    def __init__(self):
        self.code = []

    def start(self, tree):
        self.add_command(str(tree.var_needed))
        main_tree = None
        for func in tree.funcs:
            if func.children[1:-1].value == 'main':
                main_tree = func
            else:
                self.code = self.code + func.code
        if main_tree is None:
            self.code = ""
        else:
            self.code = main_tree.code[1:] + EXIT + '\n' + self.code

    def clean(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree):
                ch.code = None
        tree.code = self.code
        self.code = ""

    def functiondecl(self, tree):
        self.add_command(tree.children[1].value[:-1]+":")
        self.add_command(RESERVE, str(tree.var_needed))
        for ch in tree.children:
            if isinstance(ch, Tree) and ch.data == STATEMENT_BLOCK:
                self.add_command(ch.code, '', '')
        self.add_command(FREE, str(tree.var_needed))
        self.clean(tree)

    def push_parameters(self, tree):
        if tree.children[0].data == EXPR:
            self.add_command(tree.children[0].code, '', '')
            self.add_command(PUSH, tree.children[0].var_num)
            return 1
        return self.push_parameters(tree.children[0]) + self.push_parameters(tree.children[2])

    def call(self, tree):
        num_params = 0
        if len(tree.children[2].children) > 0:
            self.add_command(PUSH, "RA")
            num_params = self.push_parameters(tree.children[2].children[0])
        self.add_command(CALL, tree.children[1].value[:-1])
        self.add_command(POP, str(num_params))
        self.clean(tree)

    def stmtblock(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree) and ch.data == 'stmt':
                self.add_command(ch.code, '', '')
        self.clean(tree)

    def stmt(self, tree):
        if isinstance(tree.children[0], Tree):
            self.add_command(tree.children[0].code, '', '')
        self.clean(tree)

    def returnstmt(self, tree):
        if len(tree.children) == 3:
            self.add_command(tree.children[1].code)
            self.add_command(RETURN, tree.children[1])
        else:
            self.add_command(RETURN)
        self.clean(tree)

    def whilestmt(self, tree):
        self.add_label(tree.label)
        self.add_command(tree.children[2].code, '', '')
        self.add_command(IF0, tree.children[2].var, GOTO, self.index_label(tree.label + 1))
        self.add_command(tree.children[4].code, '', '')
        self.add_command(GOTO, self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def forstmt(self, tree):
        if tree.exps[0] is not None:
            self.add_command(tree.exps[0].code, '', '')
        self.add_label(tree.label)
        self.add_command(tree.exps[1].code, '', '')
        self.add_command(IF0, tree.exps[1].var, GOTO, self.index_label(tree.label + 1))
        self.add_command(tree.children[-1].code, '', '')
        if tree.exps[2] is not None:
            self.add_command(tree.exps[2].code)
        self.add_command(GOTO, self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def continuestmt(self, tree):
        self.add_command(GOTO, tree.parent_loop.label)
        self.clean(tree)

    def breakstmt(self, tree):
        self.add_command(GOTO, tree.parent_loop.label + 1)
        self.clean(tree)

    def ifstmt(self, tree):
        self.add_command(tree.children[2].code, '', '')
        self.add_command(IF0, tree.children[2].var, GOTO, self.index_label(tree.label))
        self.add_command(tree.children[4].code, '', '')
        self.add_label(tree.label)
        if len(tree.children) > 4:
            self.add_command(tree.children[6].code, '', '')
        self.clean(tree)

    def printstmt(self, tree):
        self.print_expression(tree.children[2])
        self.add_command(PRINT, NEXTLINE)
        self.clean(tree)

    def print_expression(self, tree):
        if tree.children[0].data == EXPR:
            self.add_command(tree.children[0].code, '', '')
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

    def two_op(self, tree):
        op = None
        if tree.children[0].expression_type == STRING:
            op = CONCAT
        else:
            op = tree.children[1].type
        self.add_command(tree.var_num, SET, tree.children[0].var_num, op, tree.children[2].var_num)

    def expr(self, tree):
        if isinstance(tree.children[0], Tree):
            if tree.children[0].data == 'constant':
                self.add_command(tree.parent.var_num, SET, tree.children[0].children[0].value)
            elif tree.children[0].data == EXPR:
                self.two_op(tree)
            else:
                if len(tree.children) == 1:
                    if tree.children[0].data == LVALUE:
                        self.add_command(tree.var_num, SET, tree.children[0].var_num)
                    else:
                        self.add_command(tree.var_num, SET, RETURN_VALUE)
                else:
                    self.add_command(tree.children[0].var_num, SET, tree.children[2].var_num)
        elif tree.children[0].type in [MINUS, NOT]:
            self.add_command(tree.var_num, SET, tree.children[1].type, tree.children[1].var_num)
        elif tree.children[0].type == LEFTPAR:
            self.add_command(tree.var_num, SET, tree.children[1].var_num)
        elif tree.children[0].type == NEWARRAY:
            self.add_command(tree.children[2].type)
        elif tree.children[0].type in [ITOD, ITOB, DTOI, BTOI]:
            self.add_command(tree.var_num, SET, tree.children[0].type, tree.children[2].var_num)
        elif tree.children[0].type in [READINTEGER, READLINE]:
            self.add_command(tree.var_num, SET, tree.children[0].type)
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
        self.label_index = 0
        self.reference_point = 0
        self.function_input_space = []
        self.code = code
        self.final_code = ""
        self.initialize()

    def next_label(self):
        self.label_index += 1
        return "P" + str(self.label_index)

    def convert(self):
        for line in self.code.split('\n'):
            parts = self.translate_vars(line)
            self.convert_line(parts)

    def convert_line(self, parts):
        if len(parts) == 1:
            self.add_command(parts[0])
            return
        if parts[0] == GOTO:
            self.jump(parts[1])
        elif parts[0] == IF0:
            self.if0(parts[1], parts[3])
        elif parts[0] == CALL:
            self.call(parts[1])
        elif parts[0] == PRINT:
            self.print(parts)
        elif parts[0] == PUSH:
            self.push(parts[1])
        elif parts[0] == POP:
            self.pop(parts[1])
        else:
            self.operation(parts)

    def call(self, function):
        self.reference_point = 0
        self.add_command("jal", function)

    def pop(self, num):
        self.addi(SP, SP, (int(num)+self.function_input_space[-1])*4)
        del self.function_input_space[-1]
        i = 0
        for reg in [T0, T1, T2, RA]:
            self.load_word(reg, SP, i)
            i += 4
        self.addi(SP, SP, -16)
        self.add_command("jr", RA)
            
    def push(self, var):
        if var == RA:
            self.function_input_space.append(0)
            self.reference_point += 16
            self.addi(SP, SP, -16)
            i = 0
            for reg in [T0, T1, T2, RA]:
                self.save_word(reg, SP, i)
                i += 4
        else:
            self.load_word("$t3", var)
            self.save_word("$t3", SP, -4)
            self.reference_point += 4
            self.addi(SP, SP, -4)
            self.function_input_space[-1] += 4


    def add_label(self):
        self.add_command(str(self.next_label()) + ":")

    def print_string_by_address(self, var):
        self.load_address("$a0", var)
        self.syscall(4)

    def print_string(self, var):
        self.load_word("$a0", var)
        self.syscall(4)

    def print_bool(self, var):
        self.load_word(T0, var)
        self.if0(T0, "P" + str(self.label_index+1))
        self.print_string_by_address("true")
        self.jump("P" + str(self.label_index + 2))
        self.add_label()
        self.print_string_by_address("false")
        self.add_label()

    def print_int(self, var):
        self.load_word("$a0", var)
        self.syscall(1)

    def print_double(self, var):
        self.load_word("$f12", var)
        self.syscall(2)

    def print(self, parts):
        if parts[1] == BOOL:
            self.print_bool(parts[2])
        elif parts[1] == INTT:
            self.print_int(parts[2])
        elif parts[1] == DOUBLE:
            self.print_double(parts[2])
        else:
            self.print_string(parts[2])

    def operation(self, parts):
        if parts[-1] == READINTEGER:
            self.read_integer(T0)
        elif parts[-1] == READLINE:
            self.read_line(T0)
        self.save_word(T0, parts[0])


    def load_address(self, dest, var):
        self.add_command("la", dest, var)

    def if0(self, var, label):
        self.load_word(T0, var)
        self.add_command("beq", T0, ZERO, label)

    def jump(self, label):
        self.add_command("j", label)

    def translate_vars(self, line):
        parts = line.split()
        for part in parts:
            if part[0] == 't':
                part = str(int(part[1:])*4 + self.reference_point) + "(" + SP + ")"
        return parts

    def read_integer(self, dest):
        self.syscall(5)
        self.add(dest, "$v0", ZERO)

    def initialize(self):
        self.add_command(".data")
        index = self.code.find("\n")
        global_num = int(self.code[:index])
        for i in range(1, global_num + 1):
            self.add_command("s" + str(i) + ":\t.word\t0" )
        self.add_command("true:\t.asciiz\t\"true\"")
        self.add_command("false:\t.asciiz\t\"false\"")
        self.code = self.code[index+1, :]
        self.add_command(".text")
        self.add_command(".globl main")

    def syscall(self, sys_code):
        self.addi('$v0', ZERO, str(sys_code))
        self.add_command("syscall")

    def addi(self, dest, r1, r2):
        self.add_command("addi", dest, r1, r2)

    def add(self, dest, r1, r2):
        self.add_command("add", dest, r1, r2)
        
    def load_word(self, reg, address, offset = 0):
        self.add_command('lw', reg, str(offset)+'('+address+')')

    def save_word(self, reg, address, offset = 0):
        if offset == 0:
            offset = ""
        self.add_command('sw', reg, str(offset)+'('+address+')')

    def add_command(self, *args):
        self.final_code = self.final_code + args[0]
        for i in range(1, len(args)):
            if i == len(args)-1:
                self.final_code = self.final_code + args[i] + '\n'
            else:
                self.final_code = self.final_code + args[i] + ','
