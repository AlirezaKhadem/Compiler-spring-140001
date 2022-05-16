# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 2*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

from lark import Lark


class Parser:
    def __init__(self, grammar, start, parser=None):
        self.parser = Lark(grammar=grammar, start=start, parser=parser)

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


class TestParser:
    def __init__(self, tests_path):
        self.tests_path = tests_path

    def test(self):
        import os
        from compiler.parser.grammar import grammar, start

        parser = Parser(grammar, start, parser='lalr')
        for file in os.listdir(self.tests_path):

            if file[-2:] == 'in':
                file_address = self.tests_path + file
                with open(file_address[:-2] + 'out') as file_:
                    if parser.parse_file(file_address) != file_.read():
                        print(f'There is a problem parsing file : {file_address}')


if __name__ == '__main__':
    TestParser('../parser/tests/').test()
