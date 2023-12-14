import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import unittest
from query import Query
from exceptions import FoogleBadQueryError


class QueryTests(unittest.TestCase):

    def test_valid_logical_query(self):
        query_string = "apple and (orange or not banana)"
        query = list(Query(query_string).data)
        self.assertEqual(query, ['apple', 'orange', 'banana', '!', '|', '&'])

    def test_valid_non_logical_query(self):
        query_string = "apple orange banana"
        query = list(Query(query_string, is_logical=False).data)
        self.assertEqual(query, ['apple', 'orange', 'banana', '&', '&'])

    def test_invalid_query(self):
        for query_string in ["not", "apple and", "apple and (orange or banana) or", "or not and"]:
            self._test_raising_bad_query_error(query_string)

    def test_mismatched_parentheses(self):
        for query_string in ["apple and (orange or banana", "(apple))", "((apple)"]:
            self._test_raising_bad_query_error(query_string)

    def test_empty_query(self):
        self._test_raising_bad_query_error("")

    def test_inexact_forms(self):
        self._test_inexact_form('кошечка', {'кошечке', 'кошечку', 'кошечки', 'кошечкой',
                                            'кошечек', 'кошечка', 'кошечкам', 'кошечках',
                                            'кошечкою', 'кошечками'})
        self._test_inexact_form('cat', {'catties', 'catty', 'cat', 'cats', 'catting',
                                        'cattinesses', 'cattiness', 'catted'})
        self._test_inexact_form('chk35j', {'chk35j'})

    def test_is_logical(self):
        query = Query("cat", is_logical=True)
        self.assertTrue(query.is_logical)

    def test_is_not_logical(self):
        query = Query("cat", is_logical=False)
        self.assertFalse(query.is_logical)

    def _test_raising_bad_query_error(self, query_string):
        with self.assertRaises(FoogleBadQueryError):
            Query(query_string)

    def _test_inexact_form(self, word, expected_word_forms):
        inexact_query_string = f"~{word}"
        query = list(Query(inexact_query_string).data)
        expected_word_forms_amount = len(expected_word_forms)
        expected_operators = ['|'] * (expected_word_forms_amount - 1)
        self.assertEqual(len(query), 2 * expected_word_forms_amount - 1)
        self.assertEqual(set(query[:expected_word_forms_amount]), expected_word_forms)
        self.assertEqual(query[expected_word_forms_amount:], expected_operators)
