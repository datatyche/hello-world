"""

"""
import unittest
from toxic.features.regexFeatures import *


class RegexFeaturesTest(unittest.TestCase):
    def test_block_word_count(self):
        """
        Test the number of words in upper case.
        :None:
        """
        self.assertEqual(4, block_word_count("THIS IS BLOCK SENTENCE."), "LINE TEST")
        self.assertEqual(9, block_word_count("""THIS IS BLOCK PARA.
        CONTAINS MORE THAN ONE LINE."""), "PARA TEST")
        self.assertEqual(8, block_word_count("A LINE WITH CONJUNCTION. I'M A CONJUNCTION."), "CONJUNCTION TEST")
        self.assertEqual(7, block_word_count("This is a regression test. IT SHOULD SKIP WORDS IN LOWER CASE."),
                         "REGRESSION TEST")

    def test_word_count(self):
        """
        Tests the number of words in a given text.
        :None:
        """
        self.assertEqual(4, word_count("THIS IS BLOCK SENTENCE."), "LINE TEST")
        self.assertEqual(9, word_count("""THIS IS BLOCK PARA.
                CONTAINS MORE THAN ONE LINE."""), "PARA TEST")
        self.assertEqual(8, word_count("A LINE WITH CONJUNCTION. I'M A CONJUNCTION."), "CONJUNCTION TEST")

    def test_line_count(self):
        """
                Tests the number of words in a given text.
                :None:
                """
        self.assertEqual(1, line_count("THIS IS BLOCK SENTENCE."), "LINE TEST")
        self.assertEqual(2, line_count("""THIS IS BLOCK PARA.
                        CONTAINS MORE THAN ONE LINE."""), "PARA TEST")
        self.assertEqual(line_count("A LINE WITH CONJUNCTION. I'M A CONJUNCTION."), 2, "Line with full stop")

    def test_question_count(self):
        """
        Tests the number of questions in a given text.
        :None:
        """
        self.assertEqual(question_count("A LINE WITH CONJUNCTION???? I'M A CONJUNCTION."), 1,
                         "Line with multiple question mark")

    def test_exclamation_count(self):
        """
        Tests the number of questions in a given text.
        :None:
        """
        self.assertEqual(exclamation_count("A LINE WITH CONJUNCTION!!! I'M A CONJUNCTION."), 1,
                         "Line with multiple exclamation mark")

