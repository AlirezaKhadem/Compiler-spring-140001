from lark import Lark

from compiler.parser.grammar import grammar, start_non_terminal
from compiler.scanner.scanner import Scanner


def run(input_file_address: str) -> str:
    result: str = ''
    scanner = Scanner()

    with open(input_file_address) as input_file:
        scanner.set_text(input_file.read())

    tokens= []
    for token in scanner.get_tokens():
        if token.token_type == 'T_ID':
            result += '_'
        tokens.append(token.token_value)
        result += token.token_value + '\n'

    print(len(tokens))
    parser = Lark(grammar=grammar, start=start_non_terminal, parser="lalr")
    return parser.parser(result)


if __name__ == '__main__':
    file_address = 'parser/tests/t001-class1.in'
    print(run(file_address))
