from equality import Equality


class Aexp(Equality):
    pass


class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return 'IntAexp({})'.format(self.i)


class VarAexp(Aexp):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'VarAexp({})'.format(self.name)


class BinopAexp(Aexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'BinopAexp({}, {}, {})'.format(self.op, self.left, self.right)


class Bexp(Equality):
    pass


class RelopBexp(Bexp):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class AndBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class OrBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NotBexp(Bexp):
    def __init__(self, exp):
        self.exp = exp


class Statement(Equality):
    pass


class AssignmentStatement(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp


class CompoundStatement(Statement):
    def __init__(self, first, second):
        self.first = first
        self.second = second


class IfStatement(Statement):
    def __init__(self, condition, true_stmt, false_stmt):
        self.condition = condition
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt


class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body