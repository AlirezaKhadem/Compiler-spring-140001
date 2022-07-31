start = "start"
grammar = r"""
    start: macro* decl+

    macro: IMPORT STRINGCONSTANT

    decl: variabledecl | functiondecl | classdecl | interfacedecl

    variabledecl: variable SEMICOLON

    variable: type IDENT

    functiondecl: type IDENT LEFTPAR formals RIGHTPAR stmtblock
                 | VOID IDENT LEFTPAR formals RIGHTPAR stmtblock

    classdecl: CLASS IDENT (EXTENDS IDENT)? implements? LEFTACO field* RIGHTACO

    implements: IMPLEMENTS IDENT (COMMA IDENT)*

    field: accessmode (variabledecl | functiondecl)

    accessmode: PRIVATE 
               | PROTECTED 
               | PUBLIC 
               | 

    interfacedecl: INTERFACE IDENT LEFTACO prototype* RIGHTACO

    prototype: type IDENT LEFTPAR formals RIGHTPAR SEMICOLON 
              | VOID IDENT LEFTPAR formals RIGHTPAR SEMICOLON 

    stmtblock: LEFTACO variabledecl* stmt* RIGHTACO

    stmt: expr? SEMICOLON 
         | ifstmt 
         | whilestmt 
         | forstmt 
         | breakstmt 
         | continuestmt 
         | returnstmt 
         | printstmt 
         | stmtblock

    whilestmt: WHILE LEFTPAR expr RIGHTPAR stmt

    forstmt: FOR LEFTPAR expr? SEMICOLON expr SEMICOLON expr? RIGHTPAR stmt

    returnstmt: RETURN expr? SEMICOLON

    breakstmt: BREAK SEMICOLON

    continuestmt: CONTINUE SEMICOLON

    printstmt: PRINT LEFTPAR manyexpr RIGHTPAR SEMICOLON

    ifstmt: IF LEFTPAR expr RIGHTPAR stmt (ELSE stmt)?

    expr: constant 
         | THIS
         | call
         | LEFTPAR expr RIGHTPAR
         | NOT expr 
         | MINUS expr
         | expr MULT expr 
         | expr DIV expr 
         | expr MOD expr 
         | expr PLUS expr 
         | expr MINUS expr  
         | expr LESS expr 
         | expr LESQ expr 
         | expr MORQ expr
         | expr MORE expr 
         | expr EQUALS expr 
         | expr NEQ expr 
         | expr AND expr 
         | expr OR expr  
         | lvalue (SET expr)?
         | READINTEGER LEFTPAR RIGHTPAR 
         | READLINE LEFTPAR RIGHTPAR 
         | NEW IDENT 
         | NEWARRAY LEFTPAR expr COMMA type RIGHTPAR 
         | ITOD LEFTPAR expr RIGHTPAR 
         | DTOI LEFTPAR expr RIGHTPAR 
         | ITOB LEFTPAR expr RIGHTPAR 
         | BTOI LEFTPAR expr RIGHTPAR

    call: IDENT LEFTPAR actuals RIGHTPAR 
         | expr DOT IDENT LEFTPAR actuals RIGHTPAR

    actuals: manyexpr
            |

    manyexpr: expr 
             | manyexpr COMMA expr

    lvalue: IDENT 
           | expr DOT IDENT 
           | expr LEFTCRO expr RIGHTCRO

    constant: INTCONSTANT 
             | DOUBLECONSTANT 
             | BOOLCONSTANT 
             | STRINGCONSTANT 
             | NULL 

    formals: formals COMMA variable 
            | variable 
            | 

    type: (INTT | BOOL | DOUBLE | STRING | IDENT) DOUBLECRO*

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
    DOUBLECRO: "[]\n"
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
    PRINT: "Print\n"
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

