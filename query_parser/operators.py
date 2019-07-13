import csv
import logging
import os
from enum import Enum

from query_parser.aggregators import parse_select_statement
from query_parser.expression_parser import build_expression_from_tokens

OPERATOR_KEYWORDS = (
    'SELECT',
    'FROM',
    'WHERE',
    'LIMIT',
    ';'
)


configuration = {}


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

    def apply(self, data=None):
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
    def __init__(self):
        super().__init__()
        self.output_fields = None

    def state(self):
        return ParserState.POST_SELECT

    def validate(self):
        # TODO validate key format

        # Empty select implies select *
        if not self.expression_buffer:
            raise ValueError('At least one column name or "*" is required')
        self.output_fields = parse_select_statement(self.expression_buffer)

    def apply(self, data=None):
        output_list = []
        for field in self.output_fields:
            output_list.append(field.apply(data))
        return zip(*output_list)

    def __repr__(self) -> str:
        return f'<SELECT {" ".join(self.expression_buffer)}>'


class FromOperator(Operator):
    def validate(self):
        if len(self.expression_buffer) != 1:
            raise ValueError(f'We do not support multiple data sources right now {self.expression_buffer}')

    def state(self):
        return ParserState.POST_FROM

    def apply(self, data=None):
        # TODO this should really come from command line args and not hardcoded like this!
        filename = f'{configuration["data_path"]}/{self.expression_buffer[0]}.csv'
        if not os.path.exists(filename):
            raise ValueError(f'Data source {self.expression_buffer[0]} is invalid')

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)

    def __repr__(self) -> str:
        return f'<FROM {" ".join(self.expression_buffer)}>'


class WhereOperator(Operator):

    def apply(self, data=None):
        rows = []
        for row in data:
            logging.debug(row)
            if self.filter_criteria.apply(row):
                rows.append(row)
        return rows

    def __init__(self) -> None:
        super().__init__()
        self.filter_criteria = None

    def validate(self):
        self.filter_criteria = build_expression_from_tokens(self.expression_buffer)
        if not self.filter_criteria:
            raise ValueError('No filter criteria given for where clause')

    def state(self):
        return ParserState.POST_WHERE

    def __repr__(self) -> str:
        return f'<WHERE {" ".join(self.expression_buffer)}>'


class LimitOperator(Operator):

    def __init__(self) -> None:
        super().__init__()
        self.limit = None

    def apply(self, data=None):
        return data[:self.limit]

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
    def apply(self, data=None):
        pass

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
        self.message = message
        self.current_state = current_state
        self.operator = operator

    def __str__(self) -> str:
        return f'Invalid syntax: {self.message} in state, {self.current_state} attempted to add {self.operator}'


def is_operator_state_valid(current_state: ParserState, operator: Operator):
    return any(isinstance(operator, operator_type) for operator_type in VALID_NEXT_OPERATOR_STATES[current_state])
