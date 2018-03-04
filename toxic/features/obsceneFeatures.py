"""
Features targeting obscene class.
"""
import re

def bad_words_count(text, badWordsRe):
    return len(re.compile(badWordsRe).findall(text))
