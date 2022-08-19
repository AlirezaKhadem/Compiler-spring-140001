# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 3*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

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
EXTENDS = 'extends'
EXPR = 'expr'
INTT = 'int'
BOOL = 'bool'
DOUBLE = 'double'
STRING = 'string'
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
LEFTPAR = 'LEFTPAR'
THIS = 'THIS'

output_type = {READINTEGER: INTT, READLINE: STRING, ITOD: DOUBLE, DTOI: INTT, ITOB: BOOL, BTOI: INTT}
input_type = {ITOD: INTT, DTOI: DOUBLE, ITOB: INTT, BTOI: BOOL}

semantic_error = 0

def error(tree):
    #print(tree.pretty())
    raise Exception("Semantic Error")


def is_equal(data, expected_value):
    data = remove_unnecessary(data)
    expected_value = remove_unnecessary(expected_value)
    return data == expected_value

def remove_unnecessary(data):
    data = str(data)
    data = data.replace(' ', '')
    data = data.replace('\n', '')
    return data

class SetArguments(Visitor):

    def __init__(self):
        self.var_count = 0
        self.label = 0

    def start(self, tree):
        self.initial_tree_vars(tree)
        self.initial_tree_funcs(tree)
        var_index = 0
        for declaration in tree.find_data(DECLARATION):
            if is_equal(data=declaration.children[0].data, expected_value=VARIABLE_DECLARATION):
                tree.vars.append(declaration.children[0])
                var_index += 1
                if self.is_primitive(declaration.children[0].children[0]):
                    declaration.children[0].children[0].var_num = "sp" + str(var_index)
                else:
                    declaration.children[0].children[0].var_num = "s" + str(var_index)
            elif is_equal(data=declaration.children[0].data, expected_value=FUNCTION_DECLARATION):
                tree.funcs.append(declaration.children[0])
        tree.var_needed = var_index

    def is_primitive(self, type):
        return len(type.children) == 1 and type.children[0].type in [INTT, BOOL, DOUBLE]

    @staticmethod
    def initial_tree_vars(tree):
        tree.vars = []

    @staticmethod
    def initial_tree_funcs(tree):
        tree.funcs = []

    def stmtblock(self, tree):
        iteration_index = 1
        self.initial_tree_vars(tree)
        while iteration_index < len(tree.children) \
                and isinstance(tree.children[iteration_index], Tree) \
                and tree.children[iteration_index].data == VARIABLE_DECLARATION:
            tree.vars.append(tree.children[iteration_index].children[0])
            iteration_index += 1
        if tree.parent.data == FUNCTION_DECLARATION:
            tree.var_needed = self.set_variable_number(tree)

    def set_variable_number(self, tree):
        var_count = 0
        for data in ['variable', 'expr']:
            for ch in tree.find_data(data):
                var_count += 1
                ch.var_num = "t" + str(var_count)
        return var_count

    def classdecl(self, tree):
        self.set_fields(tree)
        self.set_class_parents(tree)

    def set_fields(self, tree):
        self.initial_tree_vars(tree)
        self.initial_tree_funcs(tree)
        for field in tree.find_data(FIELD):
            if is_equal(data=field.children[-1].data, expected_value=FUNCTION_DECLARATION):
                tree.funcs.append(field)
            else:
                tree.vars.append(field)

    def set_class_parents(self, tree):
        self.set_class_parent_none(tree)
        self.initial_interface_parents(tree)
        if not isinstance(tree.children[2], Tree) and is_equal(tree.children[2].value, EXTENDS):
            tree.class_parent = tree.children[3].value

        for implement in tree.find_data(IMPLEMENTS):
            for index in range(1, len(implement.children), 2):
                tree.interface_parents.append(implement.children[index].value)

    @staticmethod
    def initial_interface_parents(tree):
        tree.interface_parents = []

    @staticmethod
    def set_class_parent_none(tree):
        tree.class_parent = None

    def functiondecl(self, tree):
        self.initial_inputs(tree)
        tree.var_needed = 0
        tree.var_needed = tree.children[-1].var_needed
        var_needed = tree.var_needed + 1
        for formal in tree.find_data(FORMALS):
            for variable in formal.find_data(VARIABLE):
                variable.var_num = "t" + str(var_needed)
                var_needed += 1
                tree.inputs.append(variable)

    @staticmethod
    def initial_inputs(tree):
        tree.inputs = []

    def set_parent_loop(self, tree):
        parent = tree.parent
        while parent is not None:
            if parent.data in ['forstmt', 'whilestmt']:
                tree.parent_loop = parent
                return
            parent = parent.parent
        error(tree)

    def breakstmt(self, tree):
        self.set_parent_loop(tree)

    def continuestmt(self, tree):
        self.set_parent_loop(tree)

    def reserve_label(self, i):
        self.label += i
        return self.label - i

    def forstmt(self, tree):
        tree.label = self.reserve_label(2)
        tree.exps = [None] * 3
        for i in range(len(tree.children)):
            ch = tree.children[i]
            if isinstance(ch, Tree) and ch.data == 'expr':
                if i == 2:
                    tree.exps[0] = ch
                elif i == len(tree.children) - 3:
                    tree.exps[2] = ch
                else:
                    tree.exps[1] = ch

    def whilestmt(self, tree):
        tree.label = self.reserve_label(2)

    def ifstmt(self, tree):
        tree.label = self.reserve_label(2)

    def expr(self, tree):
        tree.var_num = self.var_count
        self.var_count += 1

    def constant(self, tree):
        type_map = {
            "INTCONSTANT": INTT,
            "BOOLCONSTANT": BOOL,
            "DOUBLECONSTANT": DOUBLE,
            "STRINGCONSTANT": STRING,
        }
        tree.expression_type = type_map[tree.children[0].type]


class SemanticAnalyzer(Visitor):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes

    @classmethod
    def correct_unary_operation_type(self, tree):
        return self.check_unary_operation_type_condition(tree)

    @staticmethod
    def check_unary_operation_type_condition(tree):
        is_correct = False

        if is_equal(tree.children[0].type, MINUS) and tree.children[1].expression_type in [INTT, DOUBLE]:
            is_correct = True
        if is_equal(tree.children[0].type, "NOT") and is_equal(tree.children[1].expression_type, BOOL):
            is_correct = True
        if is_equal(tree.children[0].type, LEFTPAR):
            is_correct = True

        return is_correct

    @classmethod
    def correct_binary_operation_type(self, tree):
        return self.check_binary_operation_type_condition(tree)

    @staticmethod
    def check_binary_operation_type_condition(tree):
        is_correct = False

        if not is_equal(tree.children[0].expression_type, tree.children[2].expression_type):
            is_correct = False
            return is_correct

        if is_equal(tree.children[1].type, PLUS):
            is_correct = tree.children[0].expression_type in [INTT, DOUBLE, STRING] or "[]" in tree.children[
                0].expression_type
            return is_correct

        if tree.children[1].type in [MINUS, MULT, DIV] and tree.children[0].expression_type in [INTT, DOUBLE]:
            is_correct = True

        if tree.children[1].type == MOD and tree.children[0].expression_type == INTT:
            is_correct = True

        if tree.children[1].type in [MORE, LESS, MORQ, LESQ] and tree.children[0].expression_type in [INTT, DOUBLE]:
            is_correct = True

        if tree.children[1].type in [AND, OR] and tree.children[0].expression_type == BOOL:
            is_correct = True

        if tree.children[1].type in [EQUALS, NEQ]:
            is_correct = True

        return is_correct

    @classmethod
    def check_operation(self, tree):
        if isinstance(tree.children[0], Tree) and tree.children[0].data == EXPR:
            if tree.children[1].type in [PLUS, MINUS, MULT, DIV, MOD]:
                if tree.children[1].type == MULT:
                    print(tree.children[0].pretty(), tree.children[2].pretty())
                tree.expression_type = tree.children[0].expression_type
            elif tree.children[1].type in [
                MORE,
                LESS,
                MORQ,
                LESQ,
                EQUALS,
                NEQ,
                AND,
                OR,
            ]:
                tree.expression_type = BOOL
            if not self.correct_binary_operation_type(tree):
                error(tree)
        elif len(tree.children) > 1 and isinstance(tree.children[1], Tree) and tree.children[1].data == EXPR:
            if not self.correct_unary_operation_type(tree):
                error(tree)
            tree.expression_type = tree.children[1].expression_type

    def check_printable_expression(self, tree):
        if not isinstance(tree, Tree):
            return True
        if tree.data == 'expr':
            return tree.expression_type in [BOOL, STRING, INTT, DOUBLE]
        answer = self.check_printable_expression(tree.children[0])
        if len(tree.children) == 3:
            return answer and self.check_printable_expression(tree.children[2].data)
        return answer

    def printstmt(self, tree):
        if not self.check_printable_expression(tree.children[2]):
            error(tree)

    def ifstmt(self, tree):
        if tree.children[2].expression_type != BOOL:
            error(tree)

    def whilestmt(self, tree):
        if tree.children[2].expression_type != BOOL:
            error(tree)

    def get_condition(self, tree):
        index = 0
        for i in range(len(tree.children)):
            if not isinstance(tree.children[i], Tree) and tree.children[i].type == 'SEMICOLON':
                index += 1
            if index == 2:
                return tree.children[i-1]

    def forstmt(self, tree):
        if self.get_condition(tree).expression_type != BOOL:
            error(tree)

    @staticmethod
    def type_to_string(input_type):
        if not isinstance(input_type, Tree):
            return VOID
        type_string = ""
        for token in input_type.children:
            type_string = type_string + token.value[:- 1]
        return type_string

    def find_identifier_declaration(self, scope, identifier, identifier_mode):
        if scope.data == CLASS_DECLARATION:
            return self.get_field_declaration(scope.children[1].value, identifier, identifier_mode)
        if scope.data == FUNCTION_DECLARATION:
            mode_map = { VARIABLE: scope.inputs }
        else:
            mode_map = {VARIABLE: scope.vars}
        if scope.data not in [STATEMENT_BLOCK, FUNCTION_DECLARATION]:
            mode_map[FUNCTION_DECLARATION] = scope.funcs
        for part in mode_map[identifier_mode]:
            for declaration in part.find_data(identifier_mode):
                if declaration.children[1].value == identifier:
                    return declaration
        return None

    def get_identifier_declaration(self, tree, identifier, identifier_mode):
        block_types = [CLASS_DECLARATION, START]
        if identifier_mode == VARIABLE:
            block_types = block_types + [STATEMENT_BLOCK, FUNCTION_DECLARATION]
        scope = tree
        while scope is not None:
            if scope.data in block_types:
                declaration = self.find_identifier_declaration(scope, identifier, identifier_mode)
                if declaration is not None:
                    return declaration
            scope = scope.parent
        error(tree)

    def get_identifier_type(self, tree):
        if tree is None:
            return None
        return self.type_to_string(tree)

    def check_access(self, tree, obj_type, access):
        if access in ['', PUBLIC]:
            return True
        if tree.data == START:
            return False
        class_name = tree.children[1].value
        return (is_equal(access, PRIVATE) and is_equal(class_name, obj_type)) or (
                is_equal(access, PROTECTED) and self.is_parent_of(obj_type, class_name))

    def get_field_declaration(self, class_type, identifier, identifiers_mode):
        if class_type[-1] != '\n':
            class_type = class_type + '\n'
        if '[' not in class_type:
            class_tree = self.classes[class_type]
        while class_tree is not None:
            mode_map = {
                VARIABLE: class_tree.vars,
                FUNCTION_DECLARATION: class_tree.funcs
            }
            list = mode_map[identifiers_mode]
            for field in list:
                for declaration in field.find_data(identifiers_mode):
                    if is_equal(declaration.children[1], identifier):
                        if len(field.children[0].children) == 0 or self.check_access(class_tree, class_type, field.children[0].children[0].type):
                            return declaration
            if class_tree.class_parent is None:
                return None
            class_tree = self.classes[class_tree.class_parent]
        return None

    def lvalue(self, tree):
        if not isinstance(tree.children[0], Tree):
            variable = self.get_identifier_declaration(tree, tree.children[0].value, VARIABLE)
            if hasattr(variable, "var_num"):
                tree.var_num = variable.var_num
            tree.expression_type = self.type_to_string(variable.children[0])
        elif is_equal(tree.children[1].type, DOT):
            if tree.children[0].expression_type in [INTT, BOOL, DOUBLE, STRING, VOID] or '[' in tree.expression_type:
                error(tree)
            tree.expression_type = self.get_identifier_type(
                self.get_field_declaration(tree.children[0].expression_type, tree.children[2].value, VARIABLE))
            if tree.expression_type is None:
                error(tree)
        elif '[' not in tree.children[0].expression_type or tree.children[2].expression_type != INTT:
            error(tree)
        else:
            tree.expression_type = tree.children[0].expression_type[:-2]

    def is_parent_of(self, input_one, input_two):
        if input_one.count('[') != input_two.count('['):
            return False
        if input_one.count('[') > 0 or input_one in [INTT, BOOL, DOUBLE, STRING, VOID] or input_two in [INTT, BOOL, DOUBLE, STRING, VOID]:
            return is_equal(input_one, input_two)
        if input_two == NULL:
            return True
        if input_two[-1] != '\n':
            class_ = self.classes[input_two + '\n']
        else:
            class_ = self.classes[input_two]
        while class_ is not None:
            if is_equal(class_.children[1], input_one) or (remove_unnecessary(input_one) + '\n') in class_.interface_parents:
                return True
            class_ = class_.class_parent
        return False

    def check_set(self, tree):
        if isinstance(tree.children[0], Tree) and is_equal(tree.children[0].data, LVALUE):
            if len(tree.children) == 3:
                if self.is_parent_of(tree.children[0].expression_type, tree.children[2].expression_type):
                    tree.expression_type = VOID
                else:
                    error(tree)
            else:
                print(tree.children[0].children[0].value)
                tree.expression_type = tree.children[0].expression_type

    def check_array(self, tree):
        if not isinstance(tree.children[0], Tree) and tree.children[0].type == NEWARRAY:
            if tree.children[2].expression_type != INTT:
                error(tree)
            else:
                tree.expression_type = self.type_to_string(tree.children[-2]) + '[]'

    def find_current_class(self, tree):
        while tree.parent is not None and tree.data is not CLASS_DECLARATION:
            tree = tree.parent
        if tree.parent is None:
            error(tree)
        else:
            return tree.children[1]

    def check_others(self, tree):
        if isinstance(tree.children[0], Tree):
            return
        first_word = tree.children[0].type
        if first_word not in [NEW, READINTEGER, READLINE, ITOB, ITOD, BTOI, DTOI, THIS]:
            return
        if first_word == NEW:
            tree.expression_type = tree.children[1]
        elif first_word == THIS:
            tree.expression_type = self.find_current_class(tree)
        else:
            tree.expression_type = output_type[first_word]
        if first_word in [ITOB, ITOD, DTOI, BTOI] and input_type[first_word] != tree.children[2].expression_type:
            error(tree)

    def expr(self, tree):
        if len(tree.children) == 1 and isinstance(tree.children[0], Tree):
            tree.expression_type = tree.children[0].expression_type
        else:
            self.check_operation(tree)
            self.check_set(tree)
            self.check_array(tree)
            self.check_others(tree)

    def check_param_match(self, formals, actuals):

        if is_equal(actuals.data, ACTUALS):
            if len(actuals.children) == 0:
                return len(formals.children) == 0
            actuals = actuals.children[0]

        formal_type = ""
        actual_type = ""
        if formals.data == VARIABLE and actuals.data == EXPR:
            formal_type = self.type_to_string(formals.children[0])
            actual_type = actuals.expression_type
        elif isinstance(formals.children[-1], Tree) and isinstance(actuals.children[-1], Tree) and \
                formals.children[-1].data == VARIABLE and actuals.children[-1].data == EXPR:
            formal_type = self.type_to_string(formals.children[-1].children[0])
            actual_type = actuals.children[-1].expression_type
        else:
            return False

        if not self.is_parent_of(formal_type, actual_type):
            return False
        elif formals.data == VARIABLE and actuals.data == EXPR:
            return True
        return self.check_param_match(formals.children[0], actuals.children[0])

    def functiondecl(self, tree):
        return_type = self.type_to_string(tree.children[0])
        for statement in tree.find_data(RETURN_STATEMENT):
            if return_type == VOID and len(statement.children) > 2:
                error(tree)
            if not is_equal(return_type, VOID):
                if not self.is_parent_of(return_type, statement.children[1].expression_type):
                    error(tree)

    def call(self, tree):
        declaration = None
        if not isinstance(tree.children[0], Tree):
            declaration = self.get_identifier_declaration(
                tree,
                tree.children[0],
                FUNCTION_DECLARATION
            )
        elif '[' in tree.children[0].expression_type:
            if tree.children[2].value[1:-1] == 'length':
                tree.expression_type = INTT
            else:
                error(tree)
            return
        else:
            declaration = self.get_field_declaration(
                tree.children[0].expression_type,
                tree.children[2],
                FUNCTION_DECLARATION
            )
        if (declaration is None or not self.check_param_match(declaration.children[3], tree.children[-2])):
            error(tree)
        tree.expression_type = self.type_to_string(declaration.children[0])
