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


def is_equal(data, expected_value):
    return data == expected_value


class SetArguments(Visitor):

    @classmethod
    def start(cls, tree):
        cls.initial_tree_vars(tree)
        cls.initial_tree_funcs(tree)
        for declaration in tree.find_data(DECLARATION):
            if is_equal(data=declaration.data, expected_value=VARIABLE_DECLARATION):
                tree.vars.append(declaration.children[0])
            elif is_equal(data=declaration.data, expected_value=FUNCTION_DECLARATION):
                tree.funcs.append(declaration)

    @staticmethod
    def initial_tree_vars(tree):
        tree.vars = []

    @staticmethod
    def initial_tree_funcs(tree):
        tree.funcs = []

    @classmethod
    def statement_block(cls, tree):
        iteration_index = 1
        cls.initial_tree_vars(tree)
        while iteration_index < len(tree.children) \
                and isinstance(tree, Tree) \
                and tree.children[iteration_index].data == VARIABLE_DECLARATION:
            tree.vars.append(tree.children[iteration_index].children[0])
            iteration_index += 1

    @classmethod
    def class_declaration(cls, tree):
        cls.set_fields(tree)
        cls.set_class_parents(tree)

    @classmethod
    def set_fields(cls, tree):
        cls.initial_tree_vars(tree)
        cls.initial_tree_funcs(tree)
        for field in tree.find_data(FIELD):
            if is_equal(data=field.children[-1].data, expected_value=FUNCTION_DECLARATION):
                tree.funcs.append(field)
            else:
                tree.vars.append(field)

    @classmethod
    def set_class_parents(cls, tree):
        cls.set_class_parent_none(tree)
        cls.initial_interface_parents(tree)

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

    @classmethod
    def function_declaration(cls, tree):
        cls.initial_inputs(tree)
        for formal in tree.find_data(FORMALS):
            for variable in formal.find_data(VARIABLE):
                tree.inputs.append(variable)

    @staticmethod
    def initial_inputs(tree):
        tree.inputs = []

    @staticmethod
    def constant(tree):
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

    @staticmethod
    def error():
        print("Semantic Error")
        exit()

    @classmethod
    def correct_unary_operation_type(cls, tree):
        return cls.check_unary_operation_type_condition(tree)

    @staticmethod
    def check_unary_operation_type_condition(tree):
        is_correct = False

        if is_equal(tree.children[0].type, MINUS) and tree.children[1].expression_type in ["INTT", "DOUBLE"]:
            is_correct = True
        if is_equal(tree.children[0].type, "NOT") and is_equal(tree.children[1].type, BOOL):
            is_correct = True

        return is_correct

    @classmethod
    def correct_binary_operation_type(cls, tree):
        return cls.check_binary_operation_type_condition(tree)

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

        if tree.children[1].type in [AND, OR] and tree.children[0].type == BOOL:
            is_correct = True

        return is_correct

    @classmethod
    def check_operation(cls, tree):
        if isinstance(tree.children[0], Tree) and tree.children[0].data == EXPR:
            if tree.children[1].type in [PLUS, MINUS, MULT, DIV, MOD]:
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
            if not cls.correct_binary_operation_type(tree):
                cls.error()
        elif isinstance(tree.children[1], Tree) and tree.children[1].data == EXPR:
            if not cls.correct_unary_operation_type(tree):
                cls.error()
            tree.expression_type = tree.children[1].expression_type

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
            return self.get_field_type(scope, scope.children[1].value, identifier)
        mode_map = {
            VARIABLE: scope.vars,
            FUNCTION_DECLARATION: scope.funcs
        }
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
        self.error()

    def get_identifier_type(self, tree):
        if tree is None:
            return None
        return self.type_to_string(tree.children[0])

    def check_access(self, tree, obj_type, access):
        if access in ['', PUBLIC]:
            return True
        if tree.data == START:
            return False
        class_name = tree.children[1].value
        return (is_equal(access, PRIVATE) and is_equal(class_name, obj_type)) or (
                is_equal(access, PROTECTED) and self.is_parent_of(obj_type, class_name))

    def get_field_declaration(self, tree, obj_type, identifier, identifiers_mode):
        while tree.parent is not None and not is_equal(tree.data, CLASS_DECLARATION):
            tree = tree.parent
        class_tree = self.classes[obj_type]
        while class_tree is not None:
            mode_map = {
                VARIABLE: tree.vars,
                FUNCTION_DECLARATION: tree.funcs
            }
            identifier = mode_map[identifiers_mode]
            for field in identifier:
                for declaration in field.find_data(identifiers_mode):
                    if is_equal(declaration.children[1], identifier):
                        if self.check_access(class_tree, obj_type, field.children[0].value):
                            return declaration

            if class_tree.class_parent is None:
                self.error()
            class_tree = self.classes[class_tree.class_parent]
        return None

    def lvalue(self, tree):
        if not isinstance(tree.children[0], Tree):
            tree.expression_type = self.get_identifier_type(
                self.get_identifier_declaration(tree, tree.children[0].value, VARIABLE).children[0])
        elif is_equal(tree.children[1].type, DOT):
            if tree.children[0].expression_type in [INTT, BOOL, DOUBLE, STRING, VOID] or '[' in tree.expression_type:
                self.error()
            tree.expression_type = self.get_identifier_type(
                self.get_field_declaration(tree, tree.children[0].expression_type, tree.children[2].value, VARIABLE))
            if tree.expression_type is None:
                self.error()
        elif '[' not in tree.children[0].expression_type or tree.children[2].expression_type != INTT:
            self.error()
        else:
            tree.expression_type = tree.children[0].expression_type[:-2]

    def is_parent_of(self, input_one, input_two):
        if input_one.count('[') != input_two.count('['):
            return False
        if input_one.count('[') > 0 or input_one in [INTT, BOOL, DOUBLE, STRING]:
            return input_one == input_two
        if input_two == NULL:
            return True

        class_ = self.classes[input_two]
        while class_ is not None:
            if class_.children[1] == input_one or input_one in class_.interface_parents:
                return True
            class_ = class_.class_parent
        return False

    def check_set(self, tree):
        if isinstance(tree.children[0], Tree) and is_equal(tree.children[0].data, LVALUE):
            if self.is_parent_of(tree.children[0].expression_type, tree.children[2].expression_type):
                tree.expression_type = VOID
            else:
                self.error()

    def expression(self, tree):
        if is_equal(len(tree.children), 1) and isinstance(tree.children[0], Tree):
            tree.expression_type = tree.children[0].expression_type
        else:
            self.check_operation(tree)
            self.check_set(tree)

    def check_param_match(self, formals, actuals):

        if is_equal(actuals.data, ACTUALS):
            if is_equal(len(actuals.children), 0):
                return is_equal(len(formals.children), 0)
            actuals = actuals.children[0]

        if not is_equal(len(formals.children), len(actuals.children)):
            return False

        formal_type = self.type_to_string(formals.children[-1].children[0])
        actual_type = actuals.children[-1].expression_type

        if not self.is_parent_of(formal_type, actual_type):
            return False

        if is_equal(len(actuals), 1):
            return True
        return self.check_param_match(formals.children[0], actuals.children[0])

    def function_declaration(self, tree):
        return_type = self.type_to_string(tree.children[0])
        for statement in tree.find_data(RETURN_STATEMENT):
            if return_type == VOID and len(statement.children) > 2:
                return False
            if not is_equal(return_type, VOID):
                if not self.is_parent_of(return_type, statement.children[1].expression_type):
                    return False
        return True

    def call(self, tree):
        declaration = None
        if not isinstance(tree.children[0], Tree):
            declaration = self.get_identifier_declaration(
                tree,
                tree.children[0],
                FUNCTION_DECLARATION
            )
        else:
            declaration = self.get_field_declaration(
                tree,
                tree.children[0].expression_type,
                tree.children[2],
                FUNCTION_DECLARATION
            )
        if declaration is None or not self.check_param_match(declaration.children[3], tree.children[-2]):
            self.error()

        tree.expression_type = self.type_to_string(declaration.children[0])
