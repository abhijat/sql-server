import re
from typing import List


class Aggregator(object):
    def __init__(self, column: str) -> None:
        super().__init__()
        self.column = column

    def apply(self, dataset):
        raise NotImplementedError

    def _apply_function_on_data(self, dataset, func):
        if not dataset:
            return None

        value = float(dataset[0][self.column])
        for obj in dataset[1:]:
            try:
                value = func(value, float(obj[self.column]))
            except ValueError:
                continue
        return value

    @staticmethod
    def from_string(entity: str) -> 'Aggregator':
        match = re.match('AVG\((?P<x>.*)\)', entity)
        if match:
            return Average(match.group('x'))

        match = re.match('MIN\((?P<x>.*)\)', entity)
        if match:
            return Min(match.group('x'))

        match = re.match('MAX\((?P<x>.*)\)', entity)
        if match:
            return Max(match.group('x'))

        match = re.match('COUNT\((?P<x>.*)\)', entity)
        if match:
            return Count(match.group('x'))

        match = re.match('SUM\((?P<x>.*)\)', entity)
        if match:
            return Sum(match.group('x'))


class Average(Aggregator):
    def apply(self, dataset: List[dict]):
        summation = Sum(self.column)
        _sum = summation.apply(dataset)
        return _sum // len(dataset)


class Count(Aggregator):
    def apply(self, dataset):
        return len(dataset)


class Sum(Aggregator):
    def apply(self, dataset):
        return self._apply_function_on_data(dataset, lambda x, y: x + y)


class Min(Aggregator):
    def apply(self, dataset):
        return self._apply_function_on_data(dataset, min)


class Max(Aggregator):
    def apply(self, dataset):
        return self._apply_function_on_data(dataset, max)


class Distinct(object):
    def __init__(self, column: str) -> None:
        super().__init__()
        self.column = column

    def apply(self, dataset):
        return set([obj[self.column] for obj in dataset])


class Extractor(object):
    def __init__(self, column: str) -> None:
        super().__init__()
        self.column = column

    def apply(self, dataset):
        return [obj[self.column] for obj in dataset]


class MultiExtractor(object):
    def apply(self, dataset):
        return [', '.join(obj.values()) for obj in dataset]


def is_aggregate(entity: str):
    return any(entity.startswith(f'{k}(') for k in ('AVG', 'MIN', 'MAX', 'SUM', 'COUNT')) and entity.endswith(')')


def parse_select_statement(tokens):
    entities = []
    for token in tokens:
        entities.extend(token.split(','))

    output_fields = []
    entities_iter = iter(entities)

    for entity in entities_iter:
        if entity:
            if entity == '*':
                output_fields.append(MultiExtractor())
            elif is_aggregate(entity):
                output_fields.append(Aggregator.from_string(entity))
            elif entity == 'DISTINCT':
                output_fields.append(Distinct(next(entities_iter)))
            else:
                output_fields.append(Extractor(entity))

    return output_fields
