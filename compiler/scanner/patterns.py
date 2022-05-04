REVERSED_REGEX = {
    "true",
    "false",
    "bool",
    "break",
    "btoi",
    "class",
    "continue",
    "double",
    "dtoi",
    "else",
    "extends",
    "for",
    "if",
    "import",
    "implements",
    "int",
    "interface",
    "itob",
    "itod",
    "new",
    "NewArray",
    "null",
    "Print",
    "private",
    "public",
    "ReadInteger",
    "ReadLine",
    "return",
    "string",
    "this",
    "void",
    "while",
}
IDENTIFIER_REGEX = "[A-Za-z]([A-Za-z]|_|[0-9])*"

FIRST_INT10_REGEX = "\A([0-9]+)"

FIRST_INT16_REGEX = "\A(0(x|X)([0-9]|[a-f]|[A-F])+)"

FIRST_DOUBLE_REGEX = "\A([0-9]+[.][0-9]*)"

FIRST_DOUBEL_PATERN_SCI = "\A([0-9]+[.][0-9]*(e|E)([+]|[-])?[0-9]*)"

SINGS_REGEX = {
    "+",
    "-",
    "*",
    "/",
    "%",
    "<",
    ">",
    "<=",
    ">=",
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "==",
    "!=",
    "&&",
    "||",
    "!",
    ";",
    ",",
    ".",
    "[",
    "]",
    "{",
    "}",
    "(",
    ")",
}

SPECIAL_CHARACTERS = {
    "\n",
    '\"',
    "\'",
    "\\",
}

grammar= r"""
 ?start: macro* decl+
 ?macro: IMPORT STRINGCONSTANT
 ?decl: variabledecl | functiondecl | classdecl | interfacedecl
 ?variabledecl: VARIABLE
 ?variable: type IDENT
 ?type: INT | BOOL | DOUBLE | STRING | IDENT | type "[]"
 ?functiondecl: type IDENT "(" formals ")" stmtblock | VOID IDENT "(" formals ")" stmtblock
 ?formals: formals "," variable | variable | ""
 ?classdecl: CLASS IDENT (EXTENDS IDENT)? implements "{" field* "}" 
 ?implements: IMPLEMENTS IDENT mulidents | ""
 ?mulidents: "," IDENT mulidents | ""
 ?field: accessmode | variabledecl | accessmode functiondecl
 ?accessmode: PRIVATE | PROTECTED | PUBLIC | ""
 ?interfacedecl: INTERFACE IDENT "{" prototype* "}"
 ?stmtblock: "{" variabledecl* stmt* "}"
 ?stmt: (expr)? ";" | ifstmt | whilestmt | forstmt | breakstmt | continuestmt | reutrnstmt | printstmt | stmtblock
 ?ifstmt: IF "(" expr ")" stmt (ELSE stmt)?
 ?whilestmt: WHILE "(" expr ")" stmt
 ?forstmt: FOR "(" (expr)? ";" expr ";" (expr)? ")" stmt
 ?returnstmt: RETURN (expr)? ";"
 ?breakstmt: BREAK ";"
 ?continuestmt: CONTINUE ";"
 ?printstmt: "print(" manyexpr ");"
 ?manyexpr: expr | manyexpr "," expr
 ?expr: lvalue "=" expr | cosntant | lvalue | THIS | call | 
 "(" expr ")" | expr "+" expr | expr "-" expr | expr "*" expr | expr "/" expr | 
 expr "%" expr | "-" expr | expr "<" expr | expr "<=" expr | expr ">" expr |
 expr ">" expr | expr "==" expr | expr "!=" expr | expr "&&" expr |
 expr "||" expr | "!" expr | READINTEGER "()" | READLINE "()" | NEW IDENT |
 NEWARRAY "(" expr "," type ")" | ITOD "(" expr ")" | DTOI "(" expr ")" |
 ITOB "(" expr ")" | BTOI "(" expr ")"
 ?lvalue: IDENT | expr "." IDENT | expr "[" expr "]"
 ?call: IDENT "(" actuals ")" | expr "." IDENT "(" actuals ")"
 ?actuals: manyexprs | ""
 ?constant: INTCONSTANT | DOUBLECONSTANT | BOOLCONSTANT | STRINGCONSTANT | NULL
 
 %import common.WS
 
 %ignore WS
"""