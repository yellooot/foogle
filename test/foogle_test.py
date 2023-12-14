import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

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
        pass

    def test_relevant_txt_extension(self):
        pass

    def test_search_all_extensions(self):
        query1 = ['cat', 'dog', '|']
        query2 = ['cat']
        query3 = ['dog']
        query4 = ['cat', 'dog', '&']
        foogle = Foogle("test_data/different_extensions_test_data")
        self.assertEqual({'cat.pdf', 'cat.rtf', 'dog.txt', 'cat dog.docx'},
                         {path.name for path in foogle.search(deque(query1),
                                                              Foogle.SUPPORTED_EXTENSIONS)})
        self.assertEqual({'cat.pdf', 'cat.rtf', 'cat dog.docx'},
                         {path.name for path in foogle.search(deque(query2),
                                                              Foogle.SUPPORTED_EXTENSIONS)})
        self.assertEqual({'dog.txt', 'cat dog.docx'},
                         {path.name for path in foogle.search(deque(query3),
                                                              Foogle.SUPPORTED_EXTENSIONS)})
        self.assertEqual({'cat dog.docx'},
                         {path.name for path in foogle.search(deque(query4),
                                                              Foogle.SUPPORTED_EXTENSIONS)})


    # def test_relevant_all_extensions(self):
    #     query = ["test", "&", "document", "|", "!"]
    #     result = self.foogle.search(deque(query), Foogle.SUPPORTED_EXTENSIONS)
    #     expected_result = [self.docx_path, self.pdf_path, self.txt_path, self.rtf_path]
    #     self.assertCountEqual(result, expected_result)
    #
    # def test_different_encodings(self):
    #     foogle = Foogle("test_data/different_encodings_test_data")

    def test_different_forms(self):
        pass
