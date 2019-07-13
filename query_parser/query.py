from typing import List

from query_parser.operators import Operator


class Query(object):

    def __init__(self, operators: List[Operator]) -> None:
        super().__init__()
        self.operators = operators

