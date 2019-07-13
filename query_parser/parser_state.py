from enum import Enum
from typing import Union

from query_parser.operators import SelectOperator, FromOperator, WhereOperator, LimitOperator, EndOperator


class ParserState(Enum):
    INIT = 1
    POST_SELECT = 2
    POST_FROM = 3
    POST_WHERE = 4
    POST_LIMIT = 5
    END = 6


VALID_NEXT_OPERATOR_STATES = {
    ParserState.INIT: (SelectOperator,),
    ParserState.POST_SELECT: (FromOperator, LimitOperator,),
    ParserState.POST_FROM: (WhereOperator, LimitOperator, EndOperator,),
    ParserState.POST_WHERE: (LimitOperator, EndOperator,),
    ParserState.POST_LIMIT: (EndOperator,),
    ParserState.END: (),
}


class InvalidStateException(ValueError):

    def __init__(self, message, current_state, operator) -> None:
        super().__init__(message)
        self.current_state = current_state
        self.operator = operator


def is_operator_valid(
        current_state: ParserState,
        operator: Union[SelectOperator, FromOperator, WhereOperator, LimitOperator, EndOperator]
):
    valid_operators = VALID_NEXT_OPERATOR_STATES[current_state]
    if operator not in valid_operators:
        raise InvalidStateException('Invalid operator for state', current_state, operator)
