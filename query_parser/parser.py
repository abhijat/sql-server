from query_parser.operators import OPERATOR_KEYWORDS
from query_parser.query import Query


def parse_query(query: str) -> Query:
    tokens = query.split('\\s+')

    for token in tokens:
        if token in OPERATOR_KEYWORDS:
