# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 1*** Sharif University of Technology

"""
__author__ = 'Matin Amini, Alireza Khadem'

import re

from scanner.patterns import (
    IDENTIFIER_REGEX,
    FIRST_INT10_REGEX,
    FIRST_INT16_REGEX,
    FIRST_DOUBLE_REGEX,
    FIRST_DOUBEL_PATERN_SCI,
    SINGS_REGEX,
    MACROS,
)
from scanner.tocen import Token


class Scanner:

    def __init__(self, text=None):
        self.text = text
        self.definitions = dict()

    def set_text(self, text):
        self.text = text

    @staticmethod
    # Checks if s can be interpreted beginning with a REVERSED_REGEX word.
    def _starts_with_underline(input_string):
        match = re.search("\A(__func__|__line__)", input_string)
        if match is not None:
            next_index = match.span()[1]
            if input_string[next_index] >= 'A' or input_string[next_index] <= 'z':
                return None
            return Token(match.group(), match.group())

    def _starts_with_alphabet(self, input_string):
        match = re.search(IDENTIFIER_REGEX, input_string)
        if match.group() in self.definitions.keys():
            return Token("", self.definitions.get(match.group()), define=match.group())

        return Token("RESERVED_OR_ID", match.group())

    def _add_to_definitions(self, define_name, define_value):
        self.definitions.update({define_name.__str__, define_value})

    @staticmethod
    def _starts_with_digit(input_string):
        digit_regs = [FIRST_DOUBEL_PATERN_SCI, FIRST_DOUBLE_REGEX, FIRST_INT16_REGEX, FIRST_INT10_REGEX]
        types = ["T_DOUBLELITERAL", "T_INTLITERAL"]
        for i in range(4):
            match = re.search(digit_regs[i], input_string)
            if match is not None:
                return Token(types[int(i / 2)], match.group())

    @staticmethod
    def _starts_with_string(input_string):
        match = re.search('"', input_string[1:])
        if match is not None:
            return Token("T_STRINGLITERAL", input_string[:match.span()[1] + 1])

    @staticmethod
    def _starts_with_sign(input_string):
        matches = ["", ]
        for index, st in enumerate(input_string):
            if input_string[:index + 1] in SINGS_REGEX and len(input_string[:index + 1]) > len(matches[-1]):
                matches.append(input_string[:index + 1])

        return Token("", matches[-1])

    # Returns the first token in input_string. input_string is a string without next line.
    def _get_first_token(self, input_string):
        offset, input_string = len(input_string) - len(input_string.lstrip()), input_string.lstrip()

        if not input_string:
            return Token("", ""), offset

        token = None
        if input_string[0].isalpha():
            token = self._starts_with_alphabet(input_string)
        if input_string[0] == '_':
            token = self._starts_with_underline(input_string)
        if input_string[0].isdigit():
            token = self._starts_with_digit(input_string)
        if input_string[0] == '"':
            token = self._starts_with_string(input_string)
        if input_string[:2] in ['//', '/*']:
            token = Token("", input_string[:2])
        if token is None:
            token = self._starts_with_sign(input_string)

        if token.define is not None:
            return token, input_string[len(token.define) + offset:]
        return token, input_string[len(token.token_value) + offset:]

    def get_tokens(self):
        tokens = []
        in_comment = False
        for line in self.text.splitlines():
            while line != "":
                if in_comment:
                    comment_end = re.search('*/', line)
                    if comment_end is None:
                        line = ""
                        continue
                    else:
                        line = line[comment_end.span()[1]:]
                        in_comment = False
                token, line = self._get_first_token(line)
                if token is None:
                    return None
                if token.token_value in ["", "//"]:
                    break
                if token.token_value == '/*':
                    in_comment = True
                    continue

                if token.token_value in MACROS:
                    define_key_token, line = self._get_first_token(line)
                    define_value_token, line = self._get_first_token(line)

                    self.definitions.update({
                        define_key_token.token_value: define_value_token.token_value
                    })
                    continue

                tokens.append(token)
        return tokens
