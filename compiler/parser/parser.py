# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 2*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

from lark import Lark, Visitor, Tree


class SetArguments(Visitor):

    def start(self, tree):
        tree.vars = []
        tree.funcs = []
        for ch in tree.find_data("decl"):
            if ch.data == 'variabledecl':
                tree.vars.append(ch.children[0])
            elif ch.data == 'functiondecl':
                tree.funcs.append(ch)

    def is_in_loop(self, tree):
        parent = tree.parent
        while parent is not None:
            if parent.data in ['forstmt', 'whilestmt']:
                return True
        return False

    def breakstmt(self, tree):
        if not self.is_in_loop(tree):
            self.error()

    def continuestmt(self, tree):
        if not self.is_in_loop(tree):
            self.error()

    def stmtblock(self, tree):
        i = 1
        tree.vars = []
        while i < len(tree.children) and isinstance(tree, Tree) and tree.children[i].data == 'variabledecl':
            tree.vars.append(tree.children[i].children[0])

    def set_fields(self, tree):
        tree.vars = []
        tree.funcs = []
        for field in tree.find_data("field"):
            if field.children[-1].data == 'functiondecl':
                tree.funcs.append(field)
            else:
                tree.vars.append(field)

    def set_class_parents(self, tree):
        tree.class_parent = None
        tree.interface_parents = []
        if not isinstance(tree.children[2], Tree) and tree.children[2].value == 'EXTENDS':
            tree.class_parent = tree.children[3].value
        for ch in tree.find_data("implements"):
            for i in range(1, len(ch.children), 2):
                tree.interface_parents.append(ch.children[i].value)

    def classdecl(self, tree):
        self.set_fields(tree)
        self.set_class_parents(tree)

    def functiondecl(self, tree):
        tree.inputs = []
        for formal in tree.find_data("formals"):
            for var in formal.find_data("variable"):
                tree.inputs.append(var)

    def constant(self, tree):
        type_map = {"INTCONSTANT": "INTT", "BOOLCONSTANT": "BOOL", "DOUBLECONSTANT": "DOUBLE",
                    "STRINGCONSTANT": "STRING"}
        tree.exptype = type_map[tree.children[0].type]

class SemanticAnalyzer(Visitor):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes

    def error(self):
        print("Semantic Error")
        exit()

    def correct_unary_operation_type(self, tree):
        return (tree.children[0].type == "MINUS" and tree.children[1].exptype in ["INTT", "DOUBLE"]) or (
                    tree.children[0].type == "NOT" and tree.children[1].type == "BOOL")

    def correct_binary_operation_type(self, tree):
        if tree.children[0].exptype != tree.children[2].exptype:
            return False
        if tree.children[1].type == "PLUS":
            return tree.children[0].exptype in ["INTT", "DOUBLE", "STRING"] or "[]" in tree.children[0].exptype
        return (tree.children[1].type in ["MINUS", "MULT", "DIV"] and tree.children[0].exptype in ["INTT",
                                                                                                   "DOUBLE"]) or (
                           tree.children[1].type == "MOD" and tree.children[0].exptype == "INTT") or (
                           tree.children[1].type in ["MORE", "LESS", "MORQ", "LESQ"] and tree.children[0].exptype in [
                       "INTT", "DOUBLE"]) or (
                           tree.children[1].type in ["AND", "OR"] and tree.children[0].type == "BOOL")

    def check_operation(self, tree):
        if isinstance(tree.children[0], Tree) and tree.children[0].data == 'expr':
            if not self.correct_binary_operation_type(tree):
                self.error()
            if tree.children[1].type in ["PLUS", "MINUS", "MULT", "DIV", "MOD"]:
                tree.exptype = tree.children[0].exptype
            elif tree.children[1].type in ["MORE", "LESS", "MORQ", "LESQ", "EQUALS", "NEQ", "AND", "OR"]:
                tree.exptype = "BOOL"
        elif isinstance(tree.children[1], Tree) and tree.children[1].data == 'expr':
            if not self.correct_unary_operation_type(tree):
                self.error()
            tree.exptype = tree.children[1].exptype

    def type_to_string(self, type):
        if not isinstance(type, Tree):
            return "VOID"
        type_string = ""
        for token in type.children:
            type_string = type_string + token.value[:- 1]
        return type_string

    def find_ident_decl(self, scope, id, ident_mode):
        if scope.data == 'classdecl':
            return self.get_field_decl(scope, scope.children[1].value, id)
        mode_map = {"variable": scope.vars, "functiondecl": scope.funcs}
        for part in mode_map[ident_mode]:
            for decl in part.find_data(ident_mode):
                if decl.children[1].value == id:
                    return decl
        return None

    def get_ident_decl(self, tree, id, ident_mode):
        block_types = ["classdecl", "start"]
        if ident_mode == "variable":
            block_types= block_types + ["stmtblock", "functiondecl"]
        scope = tree
        while scope is not None:
            if scope.data in block_types:
                decl = self.find_ident_decl(scope, id, ident_mode)
                if decl is not None:
                    return decl
            scope = scope.parent
        self.error()

    def get_decl_type(self, tree):
        if tree is None:
            return None
        return self.type_to_string(tree.children[0])

    def check_access(self, tree, obj_type, access):
        if access in ['','PUBLIC']:
            return True
        if tree.data == 'start':
            return False
        class_name = tree.children[1].value
        return (access == 'PRIVATE' and class_name == obj_type) or (access == 'PROTECTED' and self.is_parent_of(obj_type, class_name))

    def get_field_decl(self, tree, obj_type, id, ident_mode):
        while tree.parent is not None and tree.data != 'classdecl':
            tree = tree.parent
        class_tree = self.classes[obj_type]
        while class_tree is not None:
            mode_map = {"variable": tree.vars, "functiondecl": tree.funcs}
            idents = mode_map[ident_mode]
            for field in idents:
                for decl in field.find_data(ident_mode):
                    if decl.children[1] == id and self.check_access(class_tree, obj_type, field.children[0].value):
                        return decl
            if class_tree.class_parent is None:
                self.error()
            class_tree = self.classes[class_tree.class_parent]
        return None

    def lvalue(self, tree):
        if not isinstance(tree.children[0], Tree):
            tree.exptype = self.get_decl_type(self.get_ident_decl(tree, tree.children[0].value, "variable").children[0])
        elif tree.children[1].type == 'DOT':
            if tree.children[0].exptype in ["INTT","BOOL","DOUBLE","STRING","VOID"] or '[' in tree.exptype:
                self.error()
            tree.exptype = self.get_decl_type(self.get_field_decl(tree, tree.children[0].exptype, tree.children[2].value, "variable"))
            if tree.exptype is None:
                self.error()
        elif '[' not in tree.children[0].exptype or tree.children[2].exptype != 'INTT':
            self.error()
        else:
            tree.exptype = tree.children[0].exptype[:-2]

    def is_parent_of(self, t1, t2):
        if t1.count('[') != t2.count('['):
            return False
        if t1.count('[') > 0 or t1 in ["INTT","BOOL","DOUBLE", "STRING"]:
            return t1 == t2
        if t2 == "NULL":
            return True
        clas2 = self.classes[t2]
        while clas2 is not None:
            if clas2.children[1] == t1 or t1 in clas2.interface_parents:
                return True
            clas2 = clas2.class_parent
        return False

    def check_set(self, tree):
        if isinstance(tree.children[0], Tree) and tree.children[0].data == 'lvalue':
            if self.is_parent_of(tree.children[0].exptype, tree.children[2].exptype):
                tree.exptype = 'VOID'
            else:
                self.error()

    def expr(self, tree):
        if len(tree.children) == 1 and isinstance(tree.children[0], Tree):
            tree.exptype = tree.children[0].exptype
        else:
            self.check_operation(tree)
            self.check_set(tree)

    def check_param_match(self, formals, actuals):
        if actuals.data == 'actuals':
            if len(actuals.children) == 0:
                return len(formals.children) == 0
            actuals = actuals.children[0]
        if len(formals.children) != len(actuals.children):
            return False
        formal_type = self.type_to_string(formals.children[-1].children[0])
        actual_type = actuals.children[-1].exptype
        if not self.is_parent_of(formal_type, actual_type):
            return False
        if len(actuals) == 1:
            return True
        return self.check_param_match(formals.children[0], actuals.children[0])

    def functiondecl(self, tree):
        return_type = self.type_to_string(tree.children[0])
        for stmt in tree.find_data("returnstmt"):
            if (return_type == "VOID" and len(stmt.children)>2) or (return_type != "VOID" and not self.is_parent_of(return_type, stmt.children[1].exptype)):
                return False
        return True


    def call(self, tree):
        decl = None
        if not isinstance(tree.children[0], Tree):
            decl = self.get_ident_decl(tree, tree.children[0], "functiondecl")
        else:
            decl = self.get_field_decl(tree, tree.children[0].exptype, tree.children[2], "functiondecl")
        if decl is None or not self.check_param_match(decl.children[3], tree.children[-2]):
            self.error()
        tree.exptype = self.type_to_string(decl.children[0])




class Parser:
    def __init__(self, grammar, start, parser=None):
        self.parser = Lark(grammar=grammar, start=start, parser=parser, lexer="contextual")

    def parse_tokens(self, tokens):
        try:
            self.parser.parser.parse(tokens)
            return "OK"
        except:
            return "Syntax Error"

    def parse_file(self, file_address):
        from compiler.scanner.scanner import Scanner
        with open(file_address) as file:
            file_context = file.read()
        scanner = Scanner(text=file_context)
        return self.parse_tokens(scanner.add_underline_to_identifiers(scanner.get_tokens()))


class ParserTester:
    def __init__(self, tests_path):
        self.tests_path = tests_path

    def test(self):
        import os
        from compiler.parser.grammar import grammar, start

        parser = Parser(grammar, start, parser='lalr')
        for test_file in os.listdir(self.tests_path):
            self.check_equality(test_file, parser)

    def check_equality(self, test_file, parser):
        if test_file[-2:] == 'in':
            file_address = self.tests_path + test_file
            try:
                with open(file_address[:-2] + 'out') as file_:
                    if parser.parse_file(file_address).strip() != file_.read().strip():
                        print(f'There is a problem parsing file : {file_address}')
            except FileNotFoundError:
                print(f'Error: {file_address[:-2]}out does not exist.')


if __name__ == '__main__':
    ParserTester('../parser/tests/').test()
