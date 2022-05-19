from compiler.parser.grammar import grammar, start
from compiler.parser.parser import Parser


def run(input_file_address: str) -> str:
    parser = Parser(grammar=grammar, start=start, parser="lalr")
    parse_result = parser.parse_file(input_file_address)

    if parse_result == "OK":
        return True
    elif parse_result == "Syntax Error":
        return False
