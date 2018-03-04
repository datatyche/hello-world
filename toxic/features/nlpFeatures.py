
"""
Features applying text blob functions.
"""
from textblob import TextBlob

def get_sentiment(text):
    return TextBlob(text).sentiment


