from ast import BinopAexp, IntAexp, VarAexp
from combinators import Lazy, Reserved, Tag
from lexer import ID, INT, language_lexer, lexer, RESERVED

id = Tag(ID)
num = Tag(INT) ^ (lambda i: int(i))
aexp_precedence_list = [
    ['*', '/'],
    ['+', '-']
]


def keyword(kw):
    return Reserved(kw, RESERVED)


def aexp_value():
    """
    This is a zero-arugment fn because we don't want the code for each
    parser to be evaluated right away. If we defined every parser as a global,
    each parser would not be able to reference parsers that come after it
    in the same source file since they wouldn't be defined, yet
    """
    return (num ^ (lambda i: IntAexp(i))) | (id ^ (lambda v: VarAexp(v)))


def process_group(parsed):
    """Discards the parenthesis tokens and returns the expression in between"""
    ((_, p), _) = parsed
    return p


def aexp_group():
    """
    Parses '(', followed by an arithmetic expression, followed by ')'.
    We need to avoid calling aexp directly since aexp will call aexp_group,
    which would result in infinite recursion. The Lazy combinator is used
    to defer the call to aexp until the parser is actually applied to some input.
    """
    return keyword('(') + Lazy(aexp) + keyword(')') ^ process_group


def aexp_term():
    """
    Any basic, self-contained expression where we don't have to worry about
    operator precedence with respect to other expressions.
    """
    return aexp_value() | aexp_group()


def process_binop(op):
    """
    Takes any arithmetic operator and returns a function that combines a pair of
    expressions using that operator.
    """
    return lambda l, r: BinopAexp(op, l, r)


def any_op_in_list(ops):
    """
    Takes a list of keyword strings and returns a parser that will match any
    of them.
    """
    op_parsers = [keyword(op) for op in ops]
    return reduce(lambda l, r: l | r, op_parsers)


def precedence(value_parser, precedence_levels, combine):
    """
    We first define op_parser which, for a given precedence level, reads any
    operator in that level and returns a function which combines two expressions.
    `op_parser` can be used as the right-hand argument of Exp.
    We start by calling Exp with `op_parser` for the highest precedence level,
    since these operations need to be grouped together first. We then use the
    resulting parser as the element parser (Exp's left argument) at the next level.
    After the loop finishes, the resulting parser will be able to correctly
    parse any arithmetic expression.

    :value_parser           parser that can read basic parts of an expression: nums,
                                vars, and groups (aexp_term)
    :precedence_levels      list of operators, 1 list for each level (aexp_precedence_list)
    :combine                return a fn to build a larger expression out of 2
                                smaller expressions (process_binop)
    """
    def op_parser(precedence_level):
        return any_op_in_list(precedence_level) ^ combine
    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precedence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser