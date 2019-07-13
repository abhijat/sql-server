from enum import Enum

from query_parser.expression_parser import build_expression_from_tokens

OPERATOR_KEYWORDS = (
    'SELECT',
    'FROM',
    'WHERE',
    'LIMIT',
    ';'
)


class ParserState(Enum):
    INIT = 1
    POST_SELECT = 2
    POST_FROM = 3
    POST_WHERE = 4
    POST_LIMIT = 5
    END = 6


class Operator(object):

    def __init__(self) -> None:
        super().__init__()
        self.expression_buffer = None

    def state(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    @staticmethod
    def from_keyword(keyword: str):
        if keyword == 'SELECT':
            return SelectOperator()
        elif keyword == 'FROM':
            return FromOperator()
        elif keyword == 'WHERE':
            return WhereOperator()
        elif keyword == 'LIMIT':
            return LimitOperator()
        elif keyword == ';':
            return EndOperator()


class SelectOperator(Operator):
    def state(self):
        return ParserState.POST_SELECT

    def validate(self):
        # TODO validate key format

        # Empty select implies select *
        if not self.expression_buffer:
            raise ValueError('At least one column name or "*" is required')

    def __repr__(self) -> str:
        return f'<SELECT {" ".join(self.expression_buffer)}>'


class FromOperator(Operator):
    def validate(self):
        if len(self.expression_buffer) != 1:
            raise ValueError(f'We do not support multiple data sources right now {self.expression_buffer}')

    def state(self):
        return ParserState.POST_FROM

    def __repr__(self) -> str:
        return f'<FROM {" ".join(self.expression_buffer)}>'


class WhereOperator(Operator):

    def __init__(self) -> None:
        super().__init__()
        self.filter_criteria = None

    def validate(self):
        self.filter_criteria = build_expression_from_tokens(self.expression_buffer)
        if not self.filter_criteria:
            raise ValueError('could not build filter criteria from expression {}'.format(self.expression_buffer))

    def state(self):
        return ParserState.POST_WHERE

    def __repr__(self) -> str:
        return f'<WHERE {" ".join(self.expression_buffer)}>'


class LimitOperator(Operator):

    def __init__(self) -> None:
        super().__init__()
        self.limit = None

    def validate(self):
        if len(self.expression_buffer) != 1:
            raise ValueError(f'invalid limit {self.expression_buffer}')

        # TODO this might throw: raise a better error here
        try:
            self.limit = int(self.expression_buffer[0])
        except ValueError:
            raise ValueError(f'non numeric limit {self.expression_buffer[0]}')

    def state(self):
        return ParserState.POST_LIMIT

    def __repr__(self) -> str:
        return f'<LIMIT {" ".join(self.expression_buffer)}>'


class EndOperator(Operator):
    def validate(self):
        if self.expression_buffer:
            raise ValueError(f'End of statement should have no expressions {self.expression_buffer}')

    def state(self):
        return ParserState.END

    def __repr__(self) -> str:
        return f'<END>'


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


def is_operator_state_valid(current_state: ParserState, operator: Operator):
    return any(isinstance(operator, operator_type) for operator_type in VALID_NEXT_OPERATOR_STATES[current_state])
