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
T3 = "$t3"
T4 = "$t4"
T5 = "$t5"
T6 = "$t6"
RA = "$ra"
F0 = "$f0"
F1= "$f1"
F2 = "$f2"
ARRAYMERGE = 'arraymerge'
S0 = "$s0"
SEQUALS = "S" + EQUALS
SNEQ = "S" + NEQ

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
        if tree.children[0].expression_type == STRING and not isinstance(tree.children[3], Tree):
            if tree.children[3].type == PLUS:
                op = CONCAT
            elif tree.children[3].type in [EQUALS, NEQ]:
                op = 'S' + tree.children[3].type
        elif '[' in tree.children[0].expression_type:
            op = ARRAYMERGE
        else:
            op = tree.children[1].type
        self.add_command(tree.var_num, SET, tree.children[0].var_num, op, tree.children[2].var_num)

    def lvalue(self, tree):
        if isinstance(tree.children[0], Tree):
            tree.parent.var_num = tree.parent.var_num + "_" + tree.children[2].var_num

    def expr(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree):
                self.add_command(ch, '', '')
        if isinstance(tree.children[0], Tree):
            if tree.children[0].data == 'constant':
                self.add_command(tree.var_num, SET, tree.children[0].children[0].value)
            elif tree.children[0].data == EXPR:
                self.two_op(tree)
            else:
                if len(tree.children) == 1:
                    if tree.children[0].data == LVALUE:
                        self.add_command(tree.var_num, SET, tree.children[0].var_num)
                    else:
                        self.add_command(tree.var_num, SET, RETURN_VALUE)
                else:
                    self.add_command(tree.var_num, SET, tree.children[2].var_num)
        elif tree.children[0].type in [MINUS, NOT]:
            if tree.children[1].expression_type == DOUBLE:
                self.add_command(tree.var_num, SET, tree.children[1].type, tree.children[1].var_num, DOUBLE)
            else:
                self.add_command(tree.var_num, SET, tree.children[1].type, tree.children[1].var_num)
        elif tree.children[0].type == LEFTPAR:
            self.add_command(tree.var_num, SET, tree.children[1].var_num)
        elif tree.children[0].type == NEWARRAY:
            self.add_command(tree.children[0].type, tree.children[2].var_num)
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

    def convert(self):
        for line in self.code.split('\n'):
            parts = self.load_arguments(line)
            self.convert_line(parts)

    def convert_line(self, parts):
        if len(parts) == 1:
            self.add_command(parts[0])
            return
        if parts[0] == GOTO:
            self.jump(parts[1])
        elif parts[0] == IF0:
            self.if0(T0, parts[3])
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
        self.load_word(RA, SP)
        self.addi(SP, SP, 4)
        self.add_command("jr", RA)
            
    def push(self, var):
        if var == RA:
            self.function_input_space.append(0)
            self.save_word(RA, SP, -4)
        else:
            self.load_word(T3, var)
            self.save_word(T3, SP, -4)
            self.function_input_space[-1] += 4
        self.reference_point += 4
        self.addi(SP, SP, -4)

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
        elif parts[-1] == DOUBLE:
            self.double_operate(parts)
            return
        elif parts[-2] in [ITOD, DTOI, BTOI, ITOB]:
            self.type_conversion(parts)
        else:
            self.math_operate(parts)
        self.save_word(T0, S0)

    # move from int register to float register
    def move_cl(self, t, f):
        self.add_command("mtcl", t, f)

    def type_conversion(self, parts):
        if parts[-2] in [ITOD, DTOI]:
            self.move_cl(T1, F1)
            if parts[-2] == ITOD:
                self.itod()
            else:
                self.dtoi()
            self.add_command("mfcl", T0, F0)
        else:
            if parts[-2] == BTOI:
                self.btoi()
            else:
                self.add(T0, T1, ZERO)

    def get_label(self, offset = 0):
        return "P" + str(self.label_index + offset)

    def btoi(self):
        self.if0(T1, self.get_label(1))
        self.addi(T0, ZERO, 1)
        self.add_label()

    def itod(self):
        self.add_command("cvt.s.w", F0, F1)

    def dtoi(self):
        self.add_command("cvt.w.s", F0, F1)

    def double_operate(self, parts):
        self.move_cl(T1, F1)
        self.move_cl(T2, F2)
        if parts[3] == PLUS:
            self.add_command("add.s", F0, F1, F2)
        elif parts[3] == MINUS:
            self.add_command("sub.s", F0, F1, F2)
        elif parts[3] == MULT:
            self.add_command("mul.s", F0, F1, F2)
        elif parts[3] == DIV:
            self.divf(F0, F1, F2)
        elif parts[2] == MINUS:
            self.add_command("neg.s", F0, F1)
        elif parts[3] == LESS:
            self.add_command("c.lt.s", F0, F1, F2)
        elif parts[3] == MORE:
            self.add_command("c.lt.s", F0, F2, F1)
        elif parts[3] == LESQ:
            self.add_command("c.le.s", F0, F1, F2)
        elif parts[3] == MORQ:
            self.add_command("c.lt.s", F0, F1, F2)
        self.save_word(F0, S0)

    def divf(self, dest, r1, r2):
        self.check_zero_division(r2)
        self.add_command("div.s", dest, r1, r2)

    def math_operate(self, parts):
        if parts[3] == AND:
            self.andd(T0, T1, T2)
        elif parts[3] == OR:
            self.orr(T0, T1, T2)
        elif parts[3] == PLUS:
            self.add(T0, T1, T2)
        elif parts[3] == MINUS:
            self.sub(T0, T1, T2)
        elif parts[3] == MULT:
            self.mult(T0, T1, T2)
        elif parts[3] == DIV:
            self.div(T0, T1, T2)
        elif parts[3] == MOD:
            self.mod(T0, T1, T2)
        elif parts[3] == CONCAT:
            self.concat()
        elif parts[3] == ARRAYMERGE:
            self.merge_arrays()
        elif parts[3] == LESS:
            self.slt(T0, T1, T2)
        elif parts[3] == MORE:
            self.slt(T0, T2, T1)
        elif parts[3] == EQUALS:
            self.equals()
        elif parts[3] == NEQ:
            self.neq()
        elif parts[3] == SEQUALS:
            self.string_equals()
        elif parts[3] == SNEQ:
            self.string_neq()
        elif parts[2] == NEWARRAY:
            self.new_array()
        elif parts[2] == NOT:
            self.nor(T0, T1, T1)

    def new_array(self):
        self.addi("$a0", T1, 1)
        self.addi(T2, ZERO, 4)
        self.mult("$a0", "$a0", T2)
        self.syscall(9)
        self.add(T0, "$v0", ZERO)

    def string_equals(self):
        self.add(T0, ZERO, ZERO)
        self.add_label()
        self.load_byte(T3, T1)
        self.load_byte(T4, T2)
        self.bne(T3, T4, self.get_label(2))
        self.if0(T3, self.get_label(1))
        self.addi(T1, T1, 1)
        self.addi(T2, T2, 1)
        self.jump(self.get_label())
        self.add_label()
        self.addi(T0, ZERO, 1)
        self.add_label()

    def string_neq(self):
        self.string_equals()
        self.nor(T0, T0, T0)

    def bne(self, r1, r2, label):
        self.add_command("bne", r1, r2, label)

    def nor(self, dest, r1, r2):
        self.add_command("nor", dest, r1, r2)

    def equals(self):
        self.slt(T0, T1, T2)
        self.slt(T4, T2, T1)
        self.nor(T0, T0, T4)

    def neq(self):
        self.slt(T0, T1, T2)
        self.slt(T4, T2, T1)
        self.orr(T0, T0, T4)

    def merge_arrays(self):
        self.load_word(T3, T1)
        self.load_word(T4, T2)
        self.add("$a0", T3, T4)
        self.addi("$a0", "$a0", 1)
        self.syscall(9)
        self.add(T0, ZERO, "$v0")
        self.addi("$a0", "$a0", -1)
        self.save_word(T0, "$a0")
        self.addi(T5, T0, 4)
        self.addi(T3, T3, 4)
        self.addi(T4, T4, 4)
        self.copy_array(T5, T1, T3)
        self.copy_array(T5, T2, T4)

    def copy_array(self, dest, source, len_reg):
        self.add_label()
        self.if0(len_reg, self.get_label(1))
        self.load_word(T6, source)
        self.save_word(T6, dest)
        self.addi(source, source, 4)
        self.addi(dest, dest, 4)
        self.addi(len_reg, -1)
        self.jump(self.get_label())
        self.add_label()

    def concat(self):
        self.strlen(T3, T1)
        self.strlen(T4, T2)
        self.add("$a0", T3, T4)
        self.syscall(9)
        self.add(T0, ZERO, "$v0")
        self.copy_string(T0, T1, T3)
        self.copy_string(T3, T2, T4)

    def strlen(self, st, len_reg):
        self.add(T5, st, ZERO)
        self.add(len_reg, ZERO, ZERO)
        self.add_label()
        self.load_byte(T6, T5)
        self.if0(T6, self.get_label(1))
        self.addi(len_reg, len_reg, 1)
        self.addi(T5, T5, 1)
        self.add_label()

    # t5 address of copy destination
    # t6 content of current location in source
    def copy_string(self, dest, source, last_written_address):
        self.add(T5, dest, ZERO)
        self.add_label()
        self.load_byte(T6, source)
        self.add(last_written_address, T6, ZERO)
        self.if0(T6, self.get_label(1))
        self.save_byte(T6, T5)
        self.addi(T5, T5, 1)
        self.addi(source, source, 1)
        self.add_label()

    def load_byte(self, reg, address, offset = ""):
        self.add_command("lb", reg, address, str(offset) + '(' + address + ')')

    def save_byte(self, reg, address, offset=""):
        self.add_command("sb", reg, address, str(offset) + '(' + address + ')')

    def check_zero_division(self, reg):
        self.bne(reg, ZERO, self.get_label(1))
        self.print_string_by_address("zero_div")
        self.syscall(10)
        self.add_label()

    def div(self, dest, r1, r2):
        self.check_zero_division(r2)
        self.add_command("div", r1, r2)
        self.add(dest, ZERO, "lo")

    def mod(self, dest, r1, r2):
        self.add_command("div", r1, r2)
        self.add(dest, ZERO, "hi")

    def mult(self, dest, r1, r2):
        self.add_command("mul", dest, r1, r2)

    def sub(self, dest, r1, r2):
        self.add_command("sub", dest, r1, r2)

    def andd(self, dest, r1, r2):
        self.add_command("and", dest, r1, r2)

    def orr(self, dest, r1, r2):
        self.add_command("or", dest, r1, r2)

    def load_arguments(self, line):
        parts = line.split()
        for i in range(len(parts)):
            if parts[i][0] in ['s', 't']:
                if i == 0:
                    self.load_var_or_array("$s"+str(i), parts[i], True)
                else:
                    self.load_var_or_array("$t" + str(i), parts[i], False)

    def load_var_or_array(self, dest, var, by_address):
        parts = var.split('_')
        if by_address:
            self.load_address(dest, parts[0])
        else:
            self.load_var(T3, parts[0])
        if len(parts) == 2:
            self.load_array(T3, parts[1], by_address)
        self.load_word(dest, T3)

    def load_var(self, dest, var):
        if var[:2] == 'sp':
            self.load_word(dest, var)
        elif var[0] == 's':
            self.load_address(dest, var)
        else:
            self.addi(dest, SP, int(var[1:])*4 + self.reference_point)

    def load_array(self, address, index_var, load_address):
        self.load_var(T4, index_var)
        self.check_array_index(address, T4)
        self.addi(address, address, 4)
        self.addi(T5, ZERO, 4)
        self.mult(T4, T4, T5)
        self.add(address, address, T4)
        if not load_address:
            self.load_word(address, address)

    def check_array_index(self, address, index):
        self.slt(T5, index, ZERO)
        self.load_word(T6, address)
        self.addi(T6, T6, -1)
        self.slt("$t7", T6, index)
        self.orr(T5, T5, "$t7")
        self.if0(T5, self.get_label(1))
        self.print_string_by_address("bound_error")
        self.syscall(10)
        self.add_label()

    def slt(self, dest, r1, r2):
        self.add_command("slt", dest, r1, r2)

    def load_address(self, dest, var):
        self.add_command("la", dest, var)

    def if0(self, reg, label):
        self.add_command("beq", reg, ZERO, label)

    def jump(self, label):
        self.add_command("j", label)

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
        self.add_command("bound_error:\t.asciiz\t\"Array index out of bound.\"")
        self.add_command("zero_div:\t.asciiz\t\"Division by zero.\"")
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
        
    def load_word(self, reg, address, offset = ""):
        self.add_command('lw', reg, str(offset)+'('+address+')')

    def save_word(self, reg, address, offset = ""):
        self.add_command('sw', reg, str(offset)+'('+address+')')

    def add_command(self, *args):
        self.final_code = self.final_code + args[0]
        for i in range(1, len(args)):
            if i == len(args)-1:
                self.final_code = self.final_code + args[i] + '\n'
            else:
                self.final_code = self.final_code + args[i] + ','