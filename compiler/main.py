from scanner.scanner import Scanner


def main(input_file_address: str) -> str:
    scanner = Scanner()

    with open(input_file_address) as input_file:
        scanner.set_text(input_file.read())

    return scanner.get_tokens()


if __name__ == '__main__':
    input_file_address = './../scanner/tests/t12-simple2.in'
    for token in main(input_file_address):
        print(token)
