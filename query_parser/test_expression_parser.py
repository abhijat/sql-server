from unittest import TestCase

from query_parser.expression_parser import build_expression_from_tokens, EqualsExpression, LessThanExpression, \
    GreaterThanExpression, AndExpression


class TestExpressionParser(TestCase):

    def test_equals_expression(self):
        s = 'a = 1'
        clause = build_expression_from_tokens(s.split())
        self.assertIsInstance(clause, EqualsExpression)
        self.assertEqual(clause.fieldname, 'a')
        self.assertEqual(clause.value, 1)

    def test_boolean_expression(self):
        s = 'foo = False'
        clause = build_expression_from_tokens(s.split())
        self.assertIsInstance(clause, EqualsExpression)
        self.assertEqual(clause.fieldname, 'foo')
        self.assertEqual(clause.value, False)

    def test_less_than(self):
        s = 'a < 1'
        clause = build_expression_from_tokens(s.split())
        self.assertIsInstance(clause, LessThanExpression)
        self.assertEqual(clause.fieldname, 'a')
        self.assertEqual(clause.value, 1)

    def test_greater_than(self):
        s = 'a > 1'
        clause = build_expression_from_tokens(s.split())
        self.assertIsInstance(clause, GreaterThanExpression)
        self.assertEqual(clause.fieldname, 'a')
        self.assertEqual(clause.value, 1)

    def test_and_expression(self):
        s = 'a > 1 AND b = 0'
        clause = build_expression_from_tokens(s.split())
        self.assertIsInstance(clause, AndExpression)

        lhs, rhs = clause.left, clause.right
        self.assertIsInstance(lhs, GreaterThanExpression)
        self.assertIsInstance(rhs, EqualsExpression)

        self.assertEqual(lhs.fieldname, 'a')
        self.assertEqual(rhs.value, 0)