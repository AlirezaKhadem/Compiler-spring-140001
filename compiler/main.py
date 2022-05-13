from lark import Lark

from compiler.parser.grammar import grammar, start_non_terminal
from compiler.scanner.scanner import Scanner


def run(input_file_address: str) -> str:
    result: str = ''
    scanner = Scanner()

    with open(input_file_address) as input_file:
        scanner.set_text(input_file.read())

    for token in scanner.get_tokens():
        if token.token_type == 'T_ID':
            result += '_'
        result += token.token_value + '\n'

    parser = Lark(grammar=g2, start=start_non_terminal, parser="lalr")
    return parser.parser.parse("bool\n_s\n(\n)\n{\n}\n")


if __name__ == '__main__':
    file_address = 'parser/tests/t001-class1.in'
    g2= r"""
    ?start: macro* decl+
    
    ?macro: IMPORT STRINGCONSTANT
    
    ?decl: variabledecl | functiondecl
    
    ?variabledecl: variable SEMICOLON
    
    ?variable: type IDENT
    
    ?functiondecl: type IDENT LEFTPAR formals RIGHTPAR stmtblock
                 | VOID IDENT LEFTPAR formals RIGHTPAR stmtblock
                 
    ?stmtblock: LEFTACO variabledecl* stmt* RIGHTACO
    
    ?stmt: ifstmt
    
    ?ifstmt: IF LEFTPAR expr RIGHTPAR stmt (ELSE stmt)?
    
    ?expr: constant
    
    ?constant: INTCONSTANT 
             | DOUBLECONSTANT 
             | BOOLCONSTANT 
             | STRINGCONSTANT 
             | NULL 
                 
    ?formals: formals COMMA variable 
            | variable 
            | 
    
    ?type: INTT
         | BOOL 
         | DOUBLE 
         | STRING 
         | IDENT 
         | type LEFTCRO RIGHTCRO
         
    %import common.INT
    %import common.HEXDIGIT
    %import common.DIGIT
    %import common.FLOAT
    %import common.ESCAPED_STRING
    %import common.LETTER
    
    INTCONSTANT: (INT | "0x" HEXDIGIT+ | "0X" HEXDIGIT+) "\n"
    DOUBLECONSTANT: FLOAT "\n"
    BOOLCONSTANT: ("true" | "false") "\n"
    STRINGCONSTANT: ESCAPED_STRING "\n"
    IDENT: "_" LETTER (LETTER | DIGIT | "_")* "\n"
    
    INTT: "int\n"
    BOOL: "bool\n"
    DOUBLE: "double\n"
    STRING: "string\n"
    VOID: "void\n"
    LEFTCRO: "[\n"
    RIGHTCRO: "]\n"
    LEFTPAR: "(\n"
    RIGHTPAR: ")\n"
    LEFTACO: "{\n"
    RIGHTACO: "}\n"
    IMPORT: "import\n"
    COMMA: ",\n"
    CLASS: "class\n"
    EXTENDS: "extends\n"
    IMPLEMENTS: "implements\n"
    PUBLIC: "public\n"
    PRIVATE: "private\n"
    PROTECTED: "protected\n"
    INTERFACE: "interface\n"
    SEMICOLON: ";\n"
    IF: "if\n"
    ELSE: "else\n"
    WHILE: "while\n"
    FOR: "for\n"
    RETURN: "return\n"
    BREAK: "break\n"
    CONTINUE: "continue\n"
    PRINT: "print\n"
    SET: "=\n"
    EQUALS: "==\n"
    THIS: "this\n"
    PLUS: "+\n"
    MINUS: "-\n"
    MULT: "*\n"
    DIV: "/\n"
    MOD: "%\n"
    LESS: "<\n"
    MORE: ">\n"
    LESQ: "<=\n"
    MORQ: ">=\n"
    NEQ: "!=\n"
    AND: "&&\n"
    OR: "||\n"
    NOT: "!\n"
    READLINE: "ReadLine\n"
    READINTEGER: "ReadInteger\n"
    NEW: "new\n"
    NEWARRAY: "NewArray\n"
    ITOD: "itod\n"
    ITOB: "itob\n"
    BTOI: "btoi\n"
    DTOI: "dtoi\n"
    DOT: ".\n"
    NULL: "null\n"
    """
    run(file_address)
