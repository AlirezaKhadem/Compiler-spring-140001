# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 3*** Sharif University of Technology

"""

from lark import Visitor, Tree

from compiler.parser.grammar import grammar
from compiler.parser.grammar import start
from compiler.parser.parser import Parser
from compiler.parser.semantic_analyser import SetArguments, SemanticAnalyzer

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
F1 = "$f1"
F2 = "$f2"
V0 = "$v0"
INDEX = 'INDEX'
ARRAYMERGE = 'arraymerge'
S0 = "$s0"
SEQUALS = "S" + EQUALS
SNEQ = "S" + NEQ
INTCONSTANT = "INTCONSTANT"
DOUBLECONSTANT = "DOUBLECONSTANT"
BOOLCONSTANT = "BOOLCONSTANT"
STRINGCONSTANT = "STRINGCONSTANT"
A0 = "$a0"
MAIN = 'main'
UNRESERVE = 'UNRESERVE'
LENGTH = 'LENGTH'


class Generator(Visitor):

    def __init__(self):
        self.code = ""

    def start(self, tree):
        main_tree = None
        for func in tree.funcs:
            if self.is_main_function(func):
                main_tree = func
                self.code = func.parent.code + EXIT + '\n' + self.code
            else:
                self.code = self.code + func.parent.code
        if main_tree is None:
            self.code = ""
        self.code = str(tree.var_needed) + '\n' + self.code

    def is_main_function(self, func):
        return func.children[1].value[1:-1] == MAIN

    def clean(self, tree):
        for children in tree.children:
            if isinstance(children, Tree):
                children.code = None
        tree.code = self.code
        self.code = ""

    def functiondecl(self, tree):
        if tree.children[1].value[1:-1] == MAIN:
            self.add_command("main:")
        self.add_command(tree.children[1].value[:-1] + ":")
        self.add_command(RESERVE, str(tree.var_needed))
        for children in tree.children:
            if isinstance(children, Tree) and children.data == STATEMENT_BLOCK:
                self.add_command(children.code, '', '')
        self.add_command("_end" + tree.children[1].value[:-1] + ":")
        if tree.children[1].value[1:-1] != MAIN:
            self.add_command(UNRESERVE, str(tree.var_needed))
            self.add_command(POP)
        self.clean(tree)

    def push_parameters(self, tree):
        if tree.data == EXPR:
            self.add_command(PUSH, tree.var_num)
            return 1
        answer = self.push_parameters(tree.children[0])
        if len(tree.children) == 3:
            answer += self.push_parameters(tree.children[2])
        return answer

    def call(self, tree):
        if isinstance(tree.children[0], Tree) and '[' in tree.children[0].expression_type:
            self.add_command(tree.parent.var_num, SET, LENGTH, tree.children[0].var_num)
        else:
            num_params = 0
            if len(tree.children[2].children) > 0:
                self.add_command(PUSH, RA)
                num_params = self.push_parameters(tree.children[2].children[0])
            self.add_command(CALL, tree.children[0].value[:-1])
        self.clean(tree)

    def stmtblock(self, tree):
        for children in tree.children:
            if isinstance(children, Tree) and children.data == 'stmt':
                self.add_command(children.code, '', '')
        self.clean(tree)

    def stmt(self, tree):
        if isinstance(tree.children[0], Tree):
            self.add_command(tree.children[0].code, '', '')
        self.clean(tree)

    def function_parent(self, tree):
        while tree.data != FUNCTION_DECLARATION:
            tree = tree.parent
        return tree.children[1].value[:-1]

    def returnstmt(self, tree):
        function_parent = self.function_parent(tree)
        if function_parent[1:] == MAIN:
            self.add_command(EXIT)
        elif len(tree.children) == 3:
            self.add_command(tree.children[1].code)
            self.add_command(RETURN, function_parent, tree.children[1].var_num)
        else:
            self.add_command(RETURN, function_parent)
        self.clean(tree)

    def whilestmt(self, tree):
        self.add_label(tree.label)
        self.add_command(tree.children[2].code, '', '')
        self.add_command(IF0, tree.children[2].var_num, GOTO, self.index_label(tree.label + 1))
        self.add_command(tree.children[4].code, '', '')
        self.add_command(GOTO, self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def forstmt(self, tree):
        if tree.exps[0] is not None:
            self.add_command(tree.exps[0].code, '', '')
        self.add_label(tree.label)
        self.add_command(tree.exps[1].code, '', '')
        self.add_command(IF0, tree.exps[1].var_num, GOTO, self.index_label(tree.label + 1))
        self.add_command(tree.children[-1].code, '', '')
        if tree.exps[2] is not None:
            self.add_command(tree.exps[2].code)
        self.add_command(GOTO, self.index_label(tree.label))
        self.add_label(tree.label + 1)
        self.clean(tree)

    def continuestmt(self, tree):
        self.add_command(GOTO, str(self.index_label(tree.parent_loop.label)))
        self.clean(tree)

    def breakstmt(self, tree):
        self.add_command(GOTO, str(self.index_label(tree.parent_loop.label + 1)))
        self.clean(tree)

    def ifstmt(self, tree):
        self.add_command(tree.children[2].code, '', '')
        self.add_command(IF0, tree.children[2].var_num, GOTO, self.index_label(tree.label))
        self.add_command(tree.children[4].code, '', '')
        self.add_command(GOTO, self.index_label(tree.label + 1))
        self.add_label(tree.label)
        if len(tree.children) > 5:
            self.add_command(tree.children[6].code, '', '')
        self.add_label(tree.label + 1)
        self.clean(tree)

    def printstmt(self, tree):
        self.print_expression(tree.children[2])
        self.add_command(PRINT, NEXTLINE)
        self.clean(tree)

    def print_expression(self, tree):
        if not isinstance(tree, Tree):
            return
        if tree.data == EXPR:
            self.add_command(tree.code, '', '')
            self.add_command(PRINT, tree.expression_type, tree.var_num)
        else:
            self.print_expression(tree.children[0])
            if len(tree.children) == 3:
                self.print_expression(tree.children[2])

    def decl(self, tree):
        if tree.children[0].data == FUNCTION_DECLARATION:
            self.code = tree.children[0].code
        self.clean(tree)

    def add_label(self, index):
        self.add_command(str(self.index_label(index)) + ":")

    def index_label(self, index):
        return "L" + str(index)

    def two_op(self, tree):
        op = None
        try:
            if tree.children[0].expression_type == STRING and not isinstance(tree.children[3], Tree):
                if tree.children[3].type == PLUS:
                    op = CONCAT
                elif tree.children[3].type in [EQUALS, NEQ]:
                    op = 'S' + tree.children[3].type
            elif '[' in tree.children[0].expression_type:
                op = ARRAYMERGE
            else:
                op = tree.children[1].type
        except:
            print(tree.children[0].pretty())
        self.add_command(tree.var_num, SET, tree.children[0].var_num, op, tree.children[2].var_num)

    def lvalue(self, tree):
        if isinstance(tree.children[0], Tree):
            tree.parent.var_num = tree.parent.var_num + "_" + tree.children[2].var_num

    def constant(self, tree):
        self.clean(tree)

    def expr(self, tree):
        for child in tree.children:
            if isinstance(child, Tree):
                if hasattr(child, "code"):
                    self.add_command(child.code, '', '')
        if isinstance(tree.children[0], Tree):
            if tree.children[0].data == 'constant':
                self.add_command(
                    tree.var_num,
                    SET,
                    tree.children[0].children[0].type,
                    tree.children[0].children[0].value,
                )
            elif tree.children[0].data == EXPR:
                self.two_op(tree)
            else:
                if len(tree.children) == 1:
                    if tree.children[0].data == LVALUE:
                        if len(tree.children[0].children) > 1:
                            self.add_command(tree.var_num, SET, INDEX, tree.children[0].children[0].var_num, tree.children[0].children[2].var_num)
                    else:
                        self.add_command(tree.var_num, SET, RETURN_VALUE)
                else:
                    self.add_command(tree.var_num, SET, tree.children[2].var_num)
        elif tree.children[0].type in [MINUS, NOT]:
            if tree.children[1].expression_type == DOUBLE:
                self.add_command(
                    tree.var_num,
                    SET,
                    tree.children[0].type,
                    tree.children[1].var_num,
                    DOUBLE,
                )
            else:
                self.add_command(
                    tree.var_num,
                    SET,
                    tree.children[0].type,
                    tree.children[1].var_num,
                )
        elif tree.children[0].type == LEFTPAR:
            self.add_command(tree.var_num, SET, tree.children[1].var_num)
        elif tree.children[0].type == NEWARRAY:
            self.add_command(tree.var_num, SET, tree.children[0].type, tree.children[2].var_num)
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


class FinalGenerator:

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
        if len(parts) == 0:
            return
        if len(parts) == 1 and parts[0] != POP:
            if parts[0] == EXIT:
                self.syscall(10)
            else:
                self.add_command(parts[0])
            return
        if parts[0] == GOTO:
            self.jump(parts[1])
        elif parts[0] == RETURN:
            self.returnn(parts)
        elif parts[0] == IF0:
            self.if0(T0, parts[3])
        elif parts[0] == CALL:
            self.call(parts[1])
        elif parts[0] == PRINT:
            self.print(parts)
        elif parts[0] == PUSH:
            self.push(parts[1])
        elif parts[0] == POP:
            self.pop()
        elif parts[0] == RESERVE:
            self.reserve(parts[1])
        elif parts[0] == UNRESERVE:
            self.unreserve(parts[1])
        else:
            self.operation(parts)

    def unreserve(self, number):
        self.addi(SP, SP, str(4*int(number)))

    def reserve(self, number):
        self.addi(SP, SP, "-" + str(4*int(number)))

    def returnn(self, parts):
        if len(parts) == 3:
            self.add(V0, T1, ZERO)
        self.jump("_end" + parts[1])

    def call(self, function):
        self.reference_point = 0
        if function[0] != '_':
            function = '_' + function
        self.add_command("jal", function)

    def pop(self):
        if len(self.function_input_space) > 0:
            self.addi(SP, SP, self.function_input_space[-1] * 4)
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
        self.label_index += 1
        self.add_command("P" + str(self.label_index) + ":")

    def print_string_by_address(self, var):
        self.load_address(A0, var)
        self.syscall(4)

    def print_string(self, var):
        self.add(A0, var, ZERO)
        self.syscall(4)

    def print_bool(self, var):
        self.if0(T0, "P" + str(self.label_index + 1))
        self.print_string_by_address("true")
        self.jump("P" + str(self.label_index + 2))
        self.add_label()
        self.print_string_by_address("false")
        self.add_label()

    def print_int(self, var):
        self.add(A0, ZERO, var)
        self.syscall(1)

    def print_double(self, var):
        self.move_cl(var, "$f12")
        self.syscall(2)

    def print(self, parts):
        if 'bool' in parts[1]:
            self.print_bool(parts[2])
        elif 'int' in parts[1]:
            self.print_int(parts[2])
        elif 'double' in parts[1]:
            self.print_double(parts[2])
        elif parts[1] == 'nextline':
            self.print_next_line()
        else:
            self.print_string(parts[2])

    def print_next_line(self):
        self.load_address(A0, "next_line")
        self.syscall(4)

    def operation(self, parts):
        if parts[-1] == READINTEGER:
            self.read_integer(T0)
        # elif parts[-1] == READLINE:
        # self.read_line(T0)
        elif parts[-1] == RETURN_VALUE:
            self.add(T0, V0, V0)
        elif parts[-1] == DOUBLE or parts[2] == DOUBLECONSTANT:
            self.double_operate(parts)
            return
        elif parts[-2] in [ITOD, DTOI, BTOI, ITOB]:
            self.type_conversion(parts)
        else:
            self.math_operate(parts)
        self.save_word(T0, S0)

    # move from int register to float register
    def move_cl(self, t, f):
        self.add_command("mtc1", t, f)

    def movf_cl(self, t, f):
        self.add_command("mfc1", t, f)

    def type_conversion(self, parts):
        if parts[-2] in [ITOD, DTOI]:
            self.move_cl(T1, F1)
            if parts[-2] == ITOD:
                self.itod()
            else:
                self.dtoi()
            self.movf_cl(T0, F0)
        else:
            if parts[-2] == BTOI:
                self.btoi()
            else:
                self.add(T0, T1, ZERO)

    def get_label(self, offset=0):
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
        if parts[2] == DOUBLECONSTANT:
            self.add_command("li.s", F0, parts[3])
        elif parts[3] == PLUS:
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

        self.movf_cl(T0, F0)
        self.save_word(T0, S0)

    def divf(self, dest, r1, r2):
        self.check_zero_division(r2, False)
        self.add_command("div.s", dest, r1, r2)

    def bool_constant(self, con):
        if 'true' in con:
            self.addi(T0, ZERO, 1)
        else:
            self.addi(T0, ZERO, 0)

    def math_operate(self, parts):
        if len(parts) == 3:
            self.add(T0, T1, ZERO)
        elif parts[2] == INTCONSTANT:
            self.addi(T0, ZERO, parts[-1])
        elif parts[2] == BOOLCONSTANT:
            self.bool_constant(parts[-1])
        elif parts[2] == STRINGCONSTANT:
            self.save_string(parts[-1])
        elif parts[-2] == LENGTH:
            self.load_word(T0, T1)
        elif parts[3] == AND:
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
        elif parts[3] == LESQ:
            self.morq(T0, T2, T1)
        elif parts[3] == MORQ:
            self.morq(T0, T1, T2)

    def save_string(self, string):
        string = string[1:-1]
        self.addi(A0, A0, len(string) + 1)
        self.syscall(9)
        self.add(T0, V0, ZERO)
        self.add(T1, T0, ZERO)
        for i in range(len(string)):
            self.addi(T2, ZERO, ord(string[i]))
            self.save_byte(T2, T1)
            self.addi(T1, T1, 1)
        self.save_byte(ZERO, T1)

    def morq(self, dest, r1, r2):
        self.slt(dest, r1, r2)
        self.nor(dest, r1, r2)

    def new_array(self):
        self.addi(A0, T1, 1)
        self.addi(T2, ZERO, 4)
        self.mult(A0, A0, T2)
        self.syscall(9)
        self.add(T0, V0, ZERO)

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
        self.add(A0, T3, T4)
        self.addi(A0, A0, 1)
        self.syscall(9)
        self.add(T0, ZERO, V0)
        self.addi(A0, A0, -1)
        self.save_word(T0, A0)
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
        self.add(A0, T3, T4)
        self.syscall(9)
        self.add(T0, ZERO, V0)
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

    def load_byte(self, reg, address, offset=""):
        self.add_command("lb", reg, str(offset) + '(' + address + ')')

    def save_byte(self, reg, address, offset=""):
        self.add_command("sb", reg, str(offset) + '(' + address + ')')

    def check_zero_division(self, reg, is_int):
        if is_int:
            self.bne(reg, ZERO, self.get_label(1))
        else:
            self.add_command("sub.s", "$f4", "$f4", "$f4")
            self.bne(reg, "$f4", self.get_label(1))
        self.print_string_by_address("zero_div")
        self.syscall(10)
        self.add_label()

    def div(self, dest, r1, r2):
        self.check_zero_division(r2, True)
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
        if '\"' in line:
            line_except_string = line[:line.find('\"')]
            parts = line_except_string.split()
            parts.append(line[len(line_except_string):])
        else:
            parts = line.split()
        index = 0
        is_set = SET in parts
        for i in range(len(parts)):
            if parts[i][0] in ['s', 't'] and parts[i] != 'true':
                if i == 0 and is_set:
                    self.load_var_or_array("$s" + str(index), parts[i], True)
                    parts[i] = "$s" + str(i)
                else:
                    self.load_var_or_array("$t" + str(index), parts[i], False)
                    parts[i] = "$t" + str(index)
                index += 1
        return parts

    def load_var_or_array(self, dest, var, by_address):
        parts = var.split('_')
        if by_address:
            self.load_var(dest, parts[0], True)
            if len(parts) == 1:
                return
        else:
            self.load_var(T3, parts[0], False)
        if len(parts) == 2:
            self.add(T3, dest, ZERO)
            self.load_array(T3, parts[1], by_address)
        self.add(dest, T3, ZERO)


    def load_var(self, dest, var, by_address = False):
        if var[:2] == 'sp' and not by_address:
            self.load_word(dest, var)
        elif var[0] in ['s', 'sp']:
            self.load_address(dest, var)
        else:
            self.addi(dest, SP, int(var[1:]) * 4 + self.reference_point)
            if not by_address:
                self.load_word(dest, dest)

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
        self.add(dest, V0, ZERO)

    def initialize(self):
        self.add_command(".data")
        index = self.code.find("\n")
        global_num = int(self.code[:index])
        for i in range(1, global_num + 1):
            self.add_command("s" + str(i) + ":\t.word\t0\n")
        self.add_command("next_line:\t.asciiz\t\"\\n\"\n")
        self.add_command("true:\t.asciiz\t\"true\"\n")
        self.add_command("false:\t.asciiz\t\"false\"\n")
        self.add_command("bound_error:\t.asciiz\t\"Array index out of bound.\"\n")
        self.add_command("zero_div:\t.asciiz\t\"Division by zero.\"\n")
        self.code = self.code[index + 1 :]
        self.add_command(".text\n")
        #self.add_command(".globl main\n")

    def syscall(self, sys_code):
        self.addi('$v0', ZERO, str(sys_code))
        self.add_command("syscall")

    def addi(self, dest, r1, r2):
        self.add_command("addi", dest, r1, r2)

    def add(self, dest, r1, r2):
        self.add_command("add", dest, r1, r2)

    def load_word(self, reg, address, offset=""):
        self.add_command('lw', reg, str(offset) + '(' + address + ')')

    def save_word(self, reg, address, offset=""):
        self.add_command('sw', reg, str(offset) + '(' + address + ')')

    def add_command(self, *args):
        self.final_code = self.final_code + args[0] + ' '
        for i in range(1, len(args)):
            if i == len(args) - 1:
                self.final_code = self.final_code + str(args[i]) + '\n'
            else:
                self.final_code = self.final_code + str(args[i]) + ','
        if self.final_code[-1] != '\n':
            self.final_code = self.final_code + '\n'


class GeneratorTester:
    def __init__(self, tests_path):
        self.tests_path = tests_path
        self.parser = Parser(grammar=grammar, start=start, parser='earley')


    def test(self):
        import os
        argument_set_visitor = SetArguments()
        generator = Generator()
        contains_class = False
        for root, dirs, files in os.walk(self.tests_path):
            for file in files:
                if file[-2:] == '.d':
                    file = 't131-array-10.d'
                    print(file)
                    tree, _ = self.get_tree(root + '/' + file)
                    self.set_parents(tree)
                    try:
                        argument_set_visitor.visit(tree)
                        SemanticAnalyzer(self.get_classes(tree)).visit(tree)
                    except Exception as e:
                        print(e)
                        if str(e) != 'Semantic Error':
                            exit(1)
                        else:
                            continue


                    for classdecl in tree.find_data("classdecl"):
                        contains_class = True
                        break
                    if contains_class:
                        contains_class = False
                        continue


                    generator.visit(tree)

                    final_generator = FinalGenerator(generator.code)
                    final_generator.convert()
                    code = final_generator.final_code
                    print(generator.code)
                    generator.code = ""
                    print(code)
                    exit()

    def get_tree(self, file_address):
        return self.get_parser().parse_file(file_address)

    def get_parser(self):
        return self.parser

    def set_parents(self, tree):
        if tree.data == 'start':
            tree.parent = None
        for children in tree.children:
            if isinstance(children, Tree):
                children.parent = tree
                self.set_parents(children)

    @staticmethod
    def get_classes(tree):
        classes = tree.find_pred(lambda v: isinstance(v, Tree) and v.data in ["classdecl", "interfacedecl"])
        final_classes = {}
        for class_ in classes:
            final_classes[class_.children[1].value] = class_
        return final_classes


if __name__ == "__main__":
    GeneratorTester('../generator/tests/Arrays').test()

# a = b should not be void cause of many of errors
# Boolean...
# Condition -142 -143
# Functions -sort
# Global t274
# IntegerExp t217 t255
# Loop t162-4