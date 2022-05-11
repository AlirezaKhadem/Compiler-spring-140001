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
 ?macro: "import" STRINGCONSTANT
 ?decl: variabledecl | functiondecl | classdecl | interfacedecl
 ?variabledecl: variable
 ?variable: type IDENT
 ?type: "int" | "bool" | "double" | "string" | IDENT | type "[]"
 ?functiondecl: type IDENT "(" formals ")" stmtblock | "void" IDENT "(" formals ")" stmtblock
 ?formals: formals "," variable | variable | ""
 ?classdecl: "class" IDENT ("extends" IDENT)? implements "{" field* "}" 
 ?implements: "implements" IDENT mulidents | ""
 ?mulidents: "," IDENT mulidents | ""
 ?field: accessmode | variabledecl | accessmode functiondecl
 ?accessmode: "private" | "protected" | "public" | "" 
 ?interfacedecl: "interface" IDENT "{" prototype* "}"
 ?stmtblock: "{" variabledecl* stmt* "}"
 ?stmt: (expr)? ";" | ifstmt | whilestmt | forstmt | breakstmt | continuestmt | reutrnstmt | printstmt | stmtblock
 ?ifstmt: "if" "(" expr ")" stmt ("else" stmt)?
 ?whilestmt: "while" "(" expr ")" stmt
 ?forstmt: "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt
 ?returnstmt: "return" (expr)? ";"
 ?breakstmt: "break" ";"
 ?continuestmt: "continue" ";"
 ?printstmt: "print(" manyexpr ");"
 ?manyexpr: expr | manyexpr "," expr
 ?expr: lvalue "=" expr | cosntant | lvalue | "this" | call | 
 "(" expr ")" | expr "+" expr | expr "-" expr | expr "*" expr | expr "/" expr | 
 expr "%" expr | "-" expr | expr "<" expr | expr "<=" expr | expr ">" expr |
 expr ">" expr | expr "==" expr | expr "!=" expr | expr "&&" expr |
 expr "||" expr | "!" expr | "ReadInteger()" | "ReadLine()" | "new" IDENT |
 "NewArray" "(" expr "," type ")" | "itod" "(" expr ")" | "dtoi" "(" expr ")" |
 "itob" "(" expr ")" | "btoi" "(" expr ")"
 ?lvalue: IDENT | expr "." IDENT | expr "[" expr "]"
 ?call: IDENT "(" actuals ")" | expr "." IDENT "(" actuals ")"
 ?actuals: manyexprs | ""
 ?constant: INTCONSTANT | DOUBLECONSTANT | BOOLCONSTANT | STRINGCONSTANT | "null"
  
 %import common.WS
 %import common.INT
 %import common.HEXDIGIT
 %import common.DIGIT
 %import common.FLOAT
 %import common.ESCAPED_STRING
 %import common.LETTER
 INTCONSTANT: INT | "0x" HEXDIGIT+ | "0X" HEXDIGIT+
 DOUBLECONSTANT: FLOAT
 BOOLCONSTANT: "true" | "false"
 STRINGCONSTANT: ESCAPED_STRING
 IDENT: LETTER (LETTER | DIGIT | "_")*
 %ignore WS
"""
