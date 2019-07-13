from typing import List

from query_parser.operators import OPERATOR_KEYWORDS, ParserState, is_operator_valid, \
    InvalidStateException, Operator
from query_parser.query import Query


def cleanup_final_token(token, tokens):
    if token != ';' and token.endswith(';'):
        token = token[:-1]
        tokens.append(';')
    return token


def parse_query(query: str) -> List[Query]:
    queries = []
    tokens = query.split()

    state = ParserState.INIT
    operator = None

    operators = []
    expression_buffer = []

    for token in tokens:
        # Dirty hack to make sure the semicolon is treated as a distinct token!
        token = cleanup_final_token(token, tokens)

        if token in OPERATOR_KEYWORDS:
            # Push the existing operator to stack, if any
            if operator:
                # Push the collected expression buffer to operator
                operator.expression_buffer = expression_buffer
                expression_buffer = []

                # Make sure the expression is valid
                operator.validate()
                operators.append(operator)

            # Initialize the new operator
            operator = Operator.from_keyword(token)
            if not is_operator_valid(state, operator):
                raise InvalidStateException('Invalid operator for state', state, operator)
            state = operator.state()

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


if __name__ == '__main__':
    s = 'SELECT * FROM foo WHERE bar = 1 AND X = 7 LIMIT 10;'
    q = parse_query(s)
    print(q)
