import logging
from typing import List

from query_parser.operators import Operator, FromOperator, SelectOperator, LimitOperator, WhereOperator


class Query(object):

    def __init__(self, operators: List[Operator]) -> None:
        super().__init__()
        self.operators = operators

        # These isinstance checks should probably be avoided!
        # We should probably also check there isnt more than one of these per query
        self._select = None
        self._from = None
        self._where = None
        self._limit = None

        for op in self.operators:
            if isinstance(op, FromOperator):
                self._from = op
            if isinstance(op, SelectOperator):
                self._select = op
            if isinstance(op, LimitOperator):
                self._limit = op
            if isinstance(op, WhereOperator):
                self._where = op

    def __repr__(self) -> str:
        return f'operators: {" | ".join(repr(op) for op in self.operators)}'

    def execute(self):
        data = self._from.apply()
        if self._where:
            data = self._where.apply(data)

        if self._limit:
            data = self._limit.apply(data)

        data = self._select.apply(data)

        for row in data:
            yield ', '.join([str(item) for item in row])
