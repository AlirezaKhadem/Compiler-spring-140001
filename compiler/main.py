from compiler.parser.grammar import grammar, start
from compiler.parser.parser import Parser


parser = Parser(grammar=grammar, start=start, parser="lalr")