class Equality:
    def __eq__(self, other):
        logic = [
            isinstance(other, self.__class__),
            self.__dict__ == other.__dict__
        ]
        return all(logic)

    def __ne__(self, other):
        return not self.__eq__(other)
