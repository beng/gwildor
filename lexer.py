import sys
import re


def lexer(characters, token_exprs):
    """
    For each expression, it will check whether the input text matches at the
    current position. If a match is found, the matching text is extracted into a
    token, along with the regular expression's tag. If the regular expression has
    no tag associated with it, the text is discarded. This lets us get rid of junk
    characters, like comments and whitespace. If there is no matching regular
    expression, we report an error and quit. This process is repeated until there
    are no more characters left to match.

    The order we pass in the regular expressions is significant, thus we should put
    the most specific expressions first (like those matching operators and keywords),
    followed by the more general expressions (like those for identifiers and numbers).
    """
    pos = 0
    tokens = []

    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            sys.stderr.write("Illegal character: {}\n".format(characters[pos]))
            sys.exit(1)
        else:
            pos = match.end(0)
    return tokens
