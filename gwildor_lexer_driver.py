import sys
from gwildor_lexer import gwildor_lexer


def parse_source_code(args):
    with open(args[1]) as f:
        characters = f.read()
        return gwildor_lexer(characters)


if __name__ == '__main__':
    tokens = parse_source_code(sys.argv)
    for token in tokens:
        print token