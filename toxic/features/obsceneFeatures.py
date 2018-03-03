"""
Features targeting obscene class.
"""
import re

with open('resources/badwords.csv', 'r') as myfile:
    badWordsRe=myfile.read().replace('\n', '|')


def bad_words_count(text):
    return len(re.compile(badWordsRe).findall(text))
