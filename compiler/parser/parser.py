# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 2*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

from lark import Lark, Visitor, Tree

class SetParents(Visitor):
    def __default__(self, tree):
        for subtree in tree.children:
            if isinstance(subtree, Tree):
                subtree.parent = tree


class SemanticAnalyzer(Visitor):
    def __init__(self, classes):
        super().__init__()
        self.error = 0
        self.classes = classes

    def correct_unary_operation_type(self, tree):
            return (tree.children[0].type == "MINUS" and tree.children[1].exptype in ["INTT","DOUBLE"]) or (tree.children[0].type == "NOT" and tree.children[1].type == "BOOL")

    def correct_binary_operation_type(self, tree):
        if tree.children[0].exptype != tree.children[2].exptype:
            return False
        if tree.children[1].type == "PLUS":
            return tree.children[0].exptype in ["INTT", "DOUBLE", "STRING"] or "[]" in tree.children[0].exptype
        return (tree.children[1].type in ["MINUS","MULT","DIV"] and tree.children[0].exptype in ["INTT","DOUBLE"]) or (tree.children[1].type == "MOD" and tree.children[0].exptype == "INTT") or (tree.children[1].type in ["MORE","LESS","MORQ","LESQ"] and tree.children[0].exptype in ["INTT","DOUBLE"]) or (tree.children[1].type in ["AND","OR"] and tree.children[0].type == "BOOL")

    def check_operation(self, tree):
        if isinstance(tree.children[0], Tree):
            if tree.children[0].data == 'expr':
                if not self.correct_binary_operation_type(tree):
                    self.error = 1
                    return
                if tree.children[1].type in ["PLUS","MINUS","MULT","DIV","MOD"]:
                    tree.exptype = tree.children[0].exptype
                elif tree.children[1].type in ["MORE","LESS","MORQ","LESQ","EQUALS", "NEQ", "AND", "OR"]:
                    tree.exptype= "BOOL"
        elif isinstance(tree.children[1]) and tree.children[1].data=='expr':
            if not self.correct_unary_operation_type(tree):
                self.error = 1
                return
            tree.exptype = tree.children[1].exptype

    def check_constant(self, tree):
        if tree.children[0].data == 'constant':
            type_map= {"INTCONSTANT":"INTT", "BOOLCONSTANT":"BOOL", "DOUBLECONSTANT": "DOUBLE", "STRINGCONSTANT": "STRING"}
            tree.exptype = type_map[tree.children[0].children[0].type]


    def lvalue_type(self, tree):
        if not isinstance(tree.children[0], Tree):
            while

    def expr(self, tree):
        if self.error == 1:
            return
        self.check_operation(tree)
        self.check_constant(tree)
        self.check_call(tree)


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
