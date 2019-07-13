from typing import List

from query_parser.operators import OPERATOR_KEYWORDS, operator_for_keyword
from query_parser.parser_state import ParserState, is_operator_valid, InvalidStateException
from query_parser.query import Query


def parse_query(query: str) -> List[Query]:
    queries = []
    tokens = query.split('\\s+')

    state = ParserState.INIT
    operator = None

    operators = []
    expression_buffer = []

    for token in tokens:
        if token in OPERATOR_KEYWORDS:

            # Push the existing operator to stack, if any
            if operator:
                # Push the collected expression buffer to operator
                # Note that we are changing the list back to string but we lose whitespace info here
                operator.expression_buffer = ' '.join(expression_buffer)

                # Make sure the expression is valid
                operator.validate()
                operators.append(operator)

            # Initialize the new operator
            operator = operator_for_keyword(token)
            if not is_operator_valid(state, operator):
                raise InvalidStateException('Invalid operator for state', state, operator)
            state = operator.STATE

            if state == ParserState.END:
                queries.append(Query(operators))

        # A non-operator token! Add it to the expression buffer
        else:
            if not operator:
                raise InvalidStateException('Invalid start of query', state, None)
            expression_buffer.append(token)

    # All tokens have ended. The state must be correct
    if state != ParserState.END:
        raise InvalidStateException('Malformed end of query', state, None)

    return queries
