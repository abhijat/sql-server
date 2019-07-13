from typing import List

from query_parser.operators import Operator


class Query(object):

    def __init__(self, operators: List[Operator]) -> None:
        super().__init__()
        self.operators = operators

    def __repr__(self) -> str:
        return f'operators: {" | ".join(repr(op) for op in self.operators)}'


