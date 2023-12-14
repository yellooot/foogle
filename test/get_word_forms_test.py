import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import unittest
from get_word_forms import get_word_forms


class TestGetWordForms(unittest.TestCase):
    def test_russian_word(self):
        self.assertEqual({'кошечке', 'кошечку', 'кошечки', 'кошечкой',
                          'кошечек', 'кошечка', 'кошечкам', 'кошечках',
                          'кошечкою', 'кошечками'}, get_word_forms('кошечка'))

    def test_english_word(self):
        self.assertEqual({'catties', 'catty', 'cat', 'cats', 'catting',
                          'cattinesses', 'cattiness', 'catted'},
                         get_word_forms('cat'))

    def test_other_words(self):
        self.assertEqual({'catодфвыа'}, get_word_forms('catодфвыа'))
        self.assertEqual({'sdk123оо'}, get_word_forms('sdk123оо'))
