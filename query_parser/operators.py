OPERATOR_KEYWORDS = (
    'SELECT',
    'FROM',
    'WHERE',
    'LIMIT',
)


def operator_for_keyword(keyword: str):
    if keyword == 'SELECT':
        return SelectOperator()
    elif keyword == 'FROM':
        return FromOperator()
    elif keyword == 'WHERE':
        return WhereOperator()
    elif keyword == 'LIMIT':
        return LimitOperator()


class SelectOperator(object):
    pass


class FromOperator(object):
    pass


class WhereOperator(object):
    pass


class LimitOperator(object):
    pass


class EndOperator(object):
    pass
