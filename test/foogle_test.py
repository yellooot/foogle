from query import Query
import math
import unittest
from collections import deque
from foogle import Foogle


class FoogleTests(unittest.TestCase):
    def test_tf_idf(self):
        foogle = Foogle("test_data/simple_test_data")
        self.assertAlmostEqual((1 / 3) * math.log10(8 / 4),
                               foogle.get_tf_idf(6, "c",
                                                 Foogle.SUPPORTED_EXTENSIONS), delta=1e-5)

    def test_search_txt_extension(self):
        query_and_results = [(['a', 'b', '|'],
                              {'a b.txt', 'a.txt', 'a b c.txt', 'a c.txt', 'b c.txt', 'b.txt'}),
                             (['a', 'b', '&'],
                              {'a b.txt', 'a b c.txt'}),
                             (['b', 'a', '!', '&'],
                              {'b c.txt', 'b.txt'})]
        foogle = Foogle("test_data/simple_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             {path.name for path in foogle.search(deque(query_and_result[0]),
                                                                  Foogle.SUPPORTED_EXTENSIONS)})

    def test_relevant_txt_extension(self):
        query_and_results = [(['a'], ['a.txt', 'a b.txt', 'a c.txt'])]
        foogle = Foogle("test_data/simple_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             [path.name for path in foogle.relevant(deque(query_and_result[0]),
                                                                    Foogle.SUPPORTED_EXTENSIONS)])

    def test_search_all_extensions(self):
        query_and_results = [(['cat', 'dog', '|'],
                              {'cat.pdf', 'cat cat uuu.rtf', 'dog.txt', 'cat dog.docx'}),
                             (['cat'], {'cat.pdf', 'cat cat uuu.rtf', 'cat dog.docx'}),
                             (['dog'], {'dog.txt', 'cat dog.docx'}),
                             (['cat', 'dog', '&'], {'cat dog.docx'})]
        foogle = Foogle("test_data/different_extensions_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             {path.name for path in foogle.search(deque(query_and_result[0]),
                                                                  Foogle.SUPPORTED_EXTENSIONS)})

    def test_relevant_all_extensions(self):
        # first test-case
        # 'cat dog.docx' tf-idf is (1 / 2) * log10(4 / 2) ~ 0.15
        # 'dog.txt' tf-idf is (1 / 1) * log10(4 / 2) ~ 0.3
        # second test-case
        # 'cat dog.docx' tf-idf is (1 / 2) * log10(4 / 3) ~ 0.062
        # 'cat cat uuu.rtf' tf-idf is (2 / 3) * log10(4 / 3) ~ 0.083
        # 'cat.pdf' tf-idf is (1 / 1) * log10(4 / 3) ~ 0.125
        query_and_results = [(['dog'], ['dog.txt', 'cat dog.docx']),
                             (['cat'], ['cat.pdf', 'cat cat uuu.rtf', 'cat dog.docx'])]
        foogle = Foogle("test_data/different_extensions_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             [path.name for path in foogle.relevant(deque(query_and_result[0]),
                                                                    Foogle.SUPPORTED_EXTENSIONS)])

    def test_different_encodings(self):
        query_and_results = [(['first'], {'ascii.txt', 'cp865.txt', 'koi8_r.txt', 'latin1.txt',
                                          'utf16.txt'}),
                             (['am'], {'ascii.txt', 'cp865.txt', 'koi8_r.txt', 'latin1.txt',
                                       'utf16.txt'})]
        foogle = Foogle("test_data/different_encoding_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             {path.name for path in foogle.search(deque(query_and_result[0]),
                                                                  Foogle.SUPPORTED_EXTENSIONS)})

    def test_inexact_queries(self):
        query_and_results = [(list(Query('~cat').data), ['cats.txt']),
                             (list(Query('~кошка').data), ['кошками.txt'])]
        foogle = Foogle("test_data/different_forms_test_data")
        for query_and_result in query_and_results:
            self.assertEqual(query_and_result[1],
                             [path.name for path in foogle.search(deque(query_and_result[0]),
                                                                  Foogle.SUPPORTED_EXTENSIONS)])
