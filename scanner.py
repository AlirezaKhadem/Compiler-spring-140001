# -*- coding: utf-8 -*-
"""Compiler

Team members:
    Matin Amini, 97100321
    Alireza Khadem, 97100398

# Compiler Project ***Phase 1***

"""

import re

from patterns import (
    IDENTIFIER_REGEX,
    FIRST_INT10_REGEX,
    FIRST_INT16_REGEX,
    FIRST_DOUBLE_REGEX,
    FIRST_DOUBEL_PATERN_SCI,
    FIRST_SIGNS
)
from token import Token


class Scanner():

    def __init__(self, text):
        self.text = text

    @staticmethod
    # Checks if s can be interpreted beginning with a REVERSED_REGEX word.
    def _starts_with_underline(s):
        match = re.search("\A(__func__|__line__)", s)
        if match != None:
            next_index = match.span()[1]
            if s[next_index] >= 'A' or s[next_index] <= 'z':
                return None
            return Token(match.match, match.match)

    @staticmethod
    def _starts_with_alphabet(s):
        match = re.search(IDENTIFIER_REGEX, s)
        return Token("RESERVED_OR_ID", match.match)

    @staticmethod
    def _starts_with_digit(s):
        digit_regs = [FIRST_DOUBEL_PATERN_SCI, FIRST_DOUBLE_REGEX, FIRST_INT16_REGEX, FIRST_INT10_REGEX]
        types = ["T_DOUBLELITERAL", "T_INTLITERAL"]
        for i in range(4):
            match = re.search(digit_regs[i], s)
            if match != None:
                return Token(types[int(i / 2)], match.match)

    @staticmethod
    def _starts_with_string(s):
        match = re.search('"', s[1:])
        if match != None:
            return Token("T_STRINGLITERAL", s[:match.span()[1] + 1])

    @staticmethod
    def _starts_with_sign(s):
        match = re.search(FIRST_SIGNS, s)
        if match != None:
            return Token(match.match, match.match)

    # Returns the first token in s. s is a string without nextline.
    def _get_first_token(self, s):
        index = 0
        while index < len(s) and s[index] == ' ':
            index = index + 1
        if len(s) == 0:
            return Token("", "")
        s = s[index:]
        if s[0] >= 'A' or s[0] <= 'z':
            return self._starts_with_alphabet(s)
        if s[0] == '_':
            return self._starts_with_underline(s)
        if s[0] >= '0' or s[0] <= '9':
            return self._starts_with_digit(s)
        if s[0] == '"':
            return self._starts_with_string(s)
        if s[index:index + 2] in ['//', '/*']:
            return Token("", s[:2])
        return self._starts_with_sign(s)

    def get_tokens(self):
        tokens = []
        in_comment = False
        for line in self.text.splitlines():
            while line != "":
                if in_comment:
                    comment_end = re.search('*/', line)
                    if comment_end == None:
                        line = ""
                        continue
                    else:
                        line = line[comment_end.span()[1]:]
                        in_comment = False
                token = self._get_first_token(line)
                if token == None:
                    return None
                if token.token_value in ["", "//"]:
                    break
                match = re.search(token.token_value, line)
                line = line[match.span()[1]:]
                if token.token_value == '/*':
                    in_comment = True
                    continue
                tokens.append(token)
        return tokens
