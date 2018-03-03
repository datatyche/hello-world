"""
Features targeting identity class.
"""
import re

with open('resources/identitywords.csv', 'r') as myfile:
    idendity_words_re=myfile.read().replace('\n', '|')


def identity_words_count(text):
    return len(re.compile(idendity_words_re).findall(text))
