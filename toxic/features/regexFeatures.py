"""
regexFeatures module hosts various lambda functions.
"""
import re


def block_word_count(text):
    return len(re.compile("[A-Z0-9]+[ \W]+").findall(text))


def word_count(text):
    return len(re.compile("[\w]+[ \W]*").findall(text))


def line_count(text):
    return len(re.compile("[\?\.\!\n]+").findall(text))


def question_count(text):
    return len(re.compile("[\?]+").findall(text))


def exclamation_count(text):
    return len(re.compile("[!]+").findall(text))


