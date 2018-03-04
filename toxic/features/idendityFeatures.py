"""
Features targeting identity class.
"""
import re


def identity_words_count(text, idendity_words_re):
    return len(re.compile(idendity_words_re).findall(text))
