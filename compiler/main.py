from compiler.scanner.scanner import Scanner
from compiler.parser.grammer import grammar, start_non_terminal
from lark import Lark

def run(input_file_address: str) -> str:
    result: str = ''
    scanner = Scanner()

    with open(input_file_address) as input_file:
        scanner.set_text(input_file.read())

    for token in scanner.get_tokens():
        if token.token_type=='T_ID':
            result += '_'
        result += token.token_value + '\n'

    print(result)
    parser = Lark(grammar=grammar, start=start_non_terminal)
    parse= parser.parse
    return parse(result)

if __name__ == '__main__':
    file_address= 'parser/tests/t001-class1.in'
    print(run(file_address))
