from typing import Union

from query_parser.parser_state import ParserState

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
    STATE = ParserState.POST_SELECT
    pass


class FromOperator(object):
    STATE = ParserState.POST_FROM
    pass


class WhereOperator(object):
    STATE = ParserState.POST_WHERE
    pass


class LimitOperator(object):
    STATE = ParserState.POST_LIMIT
    pass


class EndOperator(object):
    STATE = ParserState.END
    pass


Operator = Union[SelectOperator, FromOperator, WhereOperator, LimitOperator, EndOperator]
