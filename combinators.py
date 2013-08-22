"""
A combinator is a function which produces a parser as its output, usually after
taking one or more parsers as input, hence the name "combinator". You can use
combinators to create a complete parser for a language by creating lots
of smaller parsers for parts of the language, then using combinators to build
the final parser.
"""


class Result(object):
    def __init__(self, value, pos):
        """
        Every parser will return a Result object on success or None on failure.
        A Result comprises a value (part of the AST), and a position
        (the index of the next token in the stream).
        """
        self.value = value
        self.pos = pos

    def __repr__(self):
        return 'Result({}, {})'.format(self.value, self.pos)


class Parser(object):
    def __call__(self, tokens, pos):
        """
        A parser object will behave as if it were a function, but we can also
        provide additional functionality by defining some operators

        :tokens     full list of tokens (returned by the lexer)
        :pos        index into the list indicating the next token
        """
        return None

    def __add__(self, other):
        """Override default `+` operator"""
        return Concat(self, other)

    def __mul__(self, other):
        """Overrride default `*` operator"""
        return Exp(self, other)

    def __or__(self, other):
        """Override default `|` operator"""
        return Alternate(self, other)

    def __xor__(self, fn):
        """Override default `^` operator"""
        return Process(self, fn)


class Reserved(Parser):
    def __init__(self, value, tag):
        """
        Accept a tokens that are used to parse `RESERVED` words and operators.
        A token is a value-tag pair represented as a tuple: (value, tag)
        """
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        logic = [
            pos < len(tokens),
            tokens[pos][0] == self.value,
            tokens[pos][1] is self.tag
        ]
        return Result(tokens[pos][0], pos + 1) if all(logic) else None


class Tag(Parser):
    def __init__(self, tag):
        """Match any token which has a particular tag"""
        self.tag = tag

    def __call__(self, tokens, pos):
        logic = [
            pos < len(tokens),
            tokens[pos][1] is self.tag
        ]
        return Result(tokens[pos][0], pos + 1) if all(logic) else None


class Concat(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        """
        Apply the left parser followed by the right parser.
        Useful for parsing specific sequeneces of tokens, e.g. `1 + 2` could be
        written as:
        1) `parser = Concat(Concat(Tag(INT), Reserved('+', RESERVED)), Tag(INT))`
        2) `parser = Tag(INT) + Reserved('+', RESERVED) + Tag(INT)
        """
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.value)
        return None


class Alternate(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        """
        Applies the left parser if successful, otherwise applies the right parser.
        It is useful for choosing among several possible parsers, e.g.
        parser = Reserved('+', RESERVED) |
                 Reserved('-', RESERVED) |
                 Reserved('*', RESERVED) |
                 Reserved('/', RESERVED)
        """
        left_result = self.left(tokens, pos)
        if not left_result:
            right_result = self.right(tokens, pos)
            return right_result
        return left_result


class Opt(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        """
        Opt is useful for optional text, such as the else-clause of an if-statement.
        It takes one parser as input. If that parser is successful when applied,
        the result is returned normally. If it fails, a successful result is
        still returned, but the value of that result is None. No tokens are
        consumed in the failure case; the result position is the same as the
        input position.
        """
        result = self.parser(tokens, pos)
        return result if result else Result(None, pos)


class Rep(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        """
        `Rep` is useful for generating lists of things. It applies its input
        parser repeatedly until it fails, but note that `Rep` will successfully
        match an empty list and consume no tokens if its parser fails the first
        time it's applied.
        """
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)


class Process(Parser):
    """Combinator used to manipulate result values"""
    def __init__(self, parser, fn):
        self.parser = parser
        self.fn = fn

    def __call__(self, tokens, pos):
        """
        Builds the AST nodes out of the pairs and lists that
        `Concat` and `Rep` return.
        """
        result = self.parser(tokens, pos)
        if result:
            result.value = self.fn(result.value)
            return result


class Lazy(Parser):
    def __init__(self, parser_fn):
        self.parser = None
        self.parser_fn = parser_fn

    def __call__(self, tokens, pos):
        """
        Takes a zero-argument function which returns a parser. Lazy will not
        call the function to get the parser until it's applied. This is needed to
        build recursive parsers (like how arithmetic expressions can include
        arithmetic expressions). Since such a parser refers to itself, we can't
        just define it by referencing it directly; at the time the parser's
        defining expression is evaluated, the parser is not defined yet.
        """
        if not self.parser:
            self.parser = self.parser_fn()
        return self.parser(tokens, pos)


class Phrase(Parser):
    """
    Takes a single input parser, applies it, and returns its result normally.
    The only catch is that it will fail if its input parser did not consume
    all of the remaining tokens. The top level parser for "gwildor" will be a
    `Phrase` parser. This prevents us from partially matching a program which
    has garbage at the end.
    """
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        return None


class Exp(Parser):
    """
    Used to match an expression which consists of a list of elements
    separated by something, e.g. a list of statements separated by semi-colons
    a := 10;
    b := 20;
    c := 30

    `Exp` provides a way to work around left recursion by matching a list,
    similar to the way `Rep` does. `Exp` takes two parsers as input. The
    first parser matches the actual elements of the list. The second matches
    the separators. On success, the separator parser must return a function
    which combines elements parsed on the left and right into a single value.
    This value is accumulated for the whole list, left to right, and is
    ultimately returned.
    """

    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sepfn, right) = parsed
            return sepfn(result.value, right)

        next_parser = self.separator + self.parser ^ process_next
        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result
