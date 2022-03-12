REVERSED_REGEX = {
    "true",
    "false",
    "__func__",
    "__line__",
    "bool",
    "break",
    "btoi",
    "class",
    "continue",
    "define",
    "double",
    "dtoi",
    "else",
    "for",
    "if",
    "import",
    "int",
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

MACROS = {
    'define'
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
