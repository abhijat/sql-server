from unittest import TestCase

from query_parser.aggregators import parse_select_statement, Average, Extractor, Distinct


class TestParseSelect(TestCase):

    def test_parse_aggregate(self):
        tokens = 'AVG(foo), bar'
        output_fields = parse_select_statement(tokens.split())

        self.assertEqual(2, len(output_fields))
        self.assertIsInstance(output_fields[0], Average)
        self.assertIsInstance(output_fields[1], Extractor)

    def test_parse_distinct(self):
        tokens = 'DISTINCT foo, bar'
        output_fields = parse_select_statement(tokens.split())

        self.assertEqual(2, len(output_fields))
        self.assertIsInstance(output_fields[0], Distinct)
        self.assertEqual(output_fields[0].column, 'foo')
        self.assertIsInstance(output_fields[1], Extractor)
