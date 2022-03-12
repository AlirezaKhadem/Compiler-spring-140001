from compiler.scanner.scanner import Scanner


def run(input_file_address: str) -> str:
    result: str = ''
    scanner = Scanner()

    with open(input_file_address) as input_file:
        scanner.set_text(input_file.read())

    for token in scanner.get_tokens():
        result += token.__str__() + '\n'

    return result
