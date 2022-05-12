# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 2*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

from lark import Lark


class Parser(Lark):
    @staticmethod
    def read_file(file_address: str):
        with open(file_address) as file:
            content = file.read()
        return content


if __name__ == '__main__':
    from compiler.parser.grammer import grammar, start_non_terminal

    text = Parser.read_file('../parser/tests/t001-class1.in')

    parser = Lark(grammar=grammar, start=start_non_terminal)
