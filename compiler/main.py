from compiler.parser.grammar import grammar, start
from compiler.parser.parser import Parser


def run(input_file_address: str) -> str:
    parser = Parser(grammar=grammar, start=start, parser="lalr")

    result = parser.parse_file(input_file_address)
    if result == "OK":
        return True
    elif result == "Syntax Error":
        return False
