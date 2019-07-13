EXPRESSION_KEYWORDS = (
    'AND',
    'OR',
    'NOT'
)


class Expression(object):
    """
    An expression takes a dict and does _something_ with it. The actual action depends on the type of expression
    """

    def apply(self, obj: dict) -> bool:
        raise NotImplementedError


class BinaryExpression(Expression):
    """
    A binary expression is created from three pieces of data, the LHS, the RHS and the comparator
    """

    def apply(self, obj: dict) -> bool:
        raise NotImplementedError

    @staticmethod
    def from_buffer(fieldname, key, value) -> 'BinaryExpression':
        # TODO we should probably check here if the value supports > or <
        if key == '=':
            return EqualsExpression(fieldname, value)
        elif key == '>':
            return GreaterThanExpression(fieldname, value)
        elif key == '<':
            return LessThanExpression(fieldname, value)

    def __init__(self, fieldname: str, value: str) -> None:
        super().__init__()
        self.fieldname = fieldname

        if value.isnumeric():
            value = float(value)
        elif value in ('True', 'true'):
            value = True
        elif value in ('False', 'false'):
            value = False
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
            value = value[1:-1]
        self.value = value


class EqualsExpression(BinaryExpression):
    def apply(self, obj: dict) -> bool:
        return obj[self.fieldname] == self.value


class LessThanExpression(BinaryExpression):
    def apply(self, obj: dict) -> bool:
        return obj[self.fieldname] < self.value


class GreaterThanExpression(BinaryExpression):
    def apply(self, obj: dict) -> bool:
        return obj[self.fieldname] > self.value


class AndExpression(Expression):
    """
    Checks if two expressions are both True
    """

    def __init__(self, left: Expression, right: Expression) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def apply(self, obj: dict) -> bool:
        return self.left.apply(obj) and self.right.apply(obj)


class OrExpression(Expression):
    """
    Either one of two expressions is True
    """

    def __init__(self, left: Expression, right: Expression) -> None:
        super().__init__()
        self.left = left
        self.right = right

    def apply(self, obj: dict) -> bool:
        return self.left.apply(obj) or self.right.apply(obj)


class NotExpression(Expression):
    """
    The single expression is False
    """

    def __init__(self, expression: Expression) -> None:
        super().__init__()
        self.expression = expression

    def apply(self, obj: dict) -> bool:
        return not self.expression.apply(obj)


def build_expression_from_tokens(tokens):
    # For the lack of time we will use a multi-pass strategy here
    initial_pass = []

    token_iter = iter(tokens)
    # First build all simple binary expressions
    for token in token_iter:
        if token in ('AND', 'OR', 'NOT'):
            initial_pass.append(token)
        else:
            lhs, op, rhs = token, next(token_iter), next(token_iter)
            expression = BinaryExpression.from_buffer(lhs, op, rhs)
            initial_pass.append(expression)

    joint_clause = None

    iterator = iter(initial_pass)
    # Now process the AND | OR | NOT style expressions
    for item in iterator:
        if item in ('AND', 'OR') and not joint_clause:
            raise ValueError(initial_pass)

        if not joint_clause and isinstance(item, Expression):
            joint_clause = item
        elif item == 'AND':
            joint_clause = AndExpression(left=joint_clause, right=next(iterator))
        elif item == 'OR':
            joint_clause = OrExpression(left=joint_clause, right=next(iterator))
        elif item == 'NOT':
            joint_clause = NotExpression(expression=next(iterator))

    return joint_clause
