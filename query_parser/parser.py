import logging
from typing import List

from query_parser.operators import OPERATOR_KEYWORDS, ParserState, is_operator_state_valid, \
    InvalidStateException, Operator
from query_parser.query import Query


class QueryParser(object):

    def __init__(self) -> None:
        super().__init__()
        self.tokens = []
        self._initialize_state()

    def _initialize_state(self):
        self.state = ParserState.INIT
        self.operators = []
        self.operator = None
        self.expression_buffer = []

    def _cleanup_final_token(self, token, index):
        if token != ';' and token.endswith(';'):
            token = token[:-1]
            self.tokens.insert(index + 1, ';')
        return token

    def _finalize_operator(self):
        # Push the collected expression buffer to operator
        self.operator.expression_buffer = self.expression_buffer
        self.expression_buffer = []

        # Make sure the expression is valid
        self.operator.validate()
        self.operators.append(self.operator)

    def _parse_operator_keyword(self, index, queries, token):
        # Push the existing operator to stack, if any
        if self.operator:
            self._finalize_operator()

        # Initialize the new operator
        self.operator = Operator.from_keyword(token)
        if not is_operator_state_valid(self.state, self.operator):
            raise InvalidStateException('Invalid operator for state', self.state, self.operator)

        self.state = self.operator.state()

        # Handle end of query
        if self.state == ParserState.END:
            queries.append(Query(self.operators))

            # If we see an end of query before tokens run out, prepare to process the next query in string
            if index < len(self.tokens) - 1:
                self._initialize_state()

    def parse(self, query_string: str) -> List[Query]:
        queries = []

        self.tokens = query_string.split()
        for index, token in enumerate(self.tokens):
            token = self._cleanup_final_token(token, index)

            if token in OPERATOR_KEYWORDS:
                self._parse_operator_keyword(index, queries, token)

            # A non-operator token! Add it to the expression buffer
            else:
                # There can be no expressions without an operator
                if not self.operator:
                    raise InvalidStateException('Invalid start of query', self.state, None)

                # Store the expression to pass it off to the operator later on
                self.expression_buffer.append(token)

        # All tokens have been consumed. The state must be END
        if self.state != ParserState.END:
            raise InvalidStateException('Malformed end of query', self.state, None)

        return queries

