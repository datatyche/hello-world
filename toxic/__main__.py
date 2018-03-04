"""
Toxic application can be started by running this file.
"""
from toxic.features import regexFeatures
from toxic.features import obsceneFeatures
from toxic.features import idendityFeatures
from toxic.features import nlpFeatures
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import AdaBoostClassifier

import pandas as pd
import logging


def apply_features(df, input_data):
    df['block_word_ratio'] = input_data.apply(lambda x: regexFeatures.block_word_count(x.comment_text) / regexFeatures.word_count(x.comment_text), axis=1)
    df['line_count'] = input_data.apply(lambda x: regexFeatures.line_count(x.comment_text), axis=1)
    df['obscene_count'] = input_data.apply(lambda x: obsceneFeatures.bad_words_count(x.comment_text, badWordsRe), axis=1)
    df['identity_count'] = input_data.apply(lambda x: idendityFeatures.identity_words_count(x.comment_text, idendity_words_re), axis=1)
    sentiment = input_data.apply(lambda x: nlpFeatures.get_sentiment(x.comment_text), axis=1)
    df['polarity'] = pd.DataFrame([x.polarity for x in sentiment])
    df['subjectivity'] = pd.DataFrame([x.subjectivity for x in sentiment])
        
    


# logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

# Load Input
logging.info("Reading input.")
train = pd.read_csv('toxic/resources/train.csv')#.head(n=10000)

# custom data set
with open('toxic/resources/badwords.csv', 'r') as myfile:
    badWordsRe=myfile.read().replace('\n', '|')

with open('toxic/resources/identitywords.csv', 'r') as myfile:
    idendity_words_re=myfile.read().replace('\n', '|')

# Apply features and split x_train and y_train
logging.info("Applying features to training set.")
x_train = pd.DataFrame()
apply_features(x_train, train)
y_train = train.drop(['id', 'comment_text'], axis=1)

# model
estimator = AdaBoostClassifier()

# train score
score = []
for target_class in list(y_train):
    score.append(cross_val_score(estimator, x_train, y_train[target_class], cv=5, scoring='roc_auc').mean())
mean_score = sum(score) / len(score)
logging.info("Scores are " + str(score))
logging.info("Mean score = %.2f" % mean_score)

if mean_score > 0.95:
    test = pd.read_csv('toxic/resources/test.csv')
    result = pd.DataFrame(test.id)
    x_test = pd.DataFrame()
    logging.info("Applying features to test set.")
    apply_features(x_test, train)
    # predict test values
    for target_class in list(y_train):
        estimator.fit(x_train, y_train[target_class])
        result[target_class] = estimator.predict_proba(x_test)[:, 1].reshape(-1, 1)
        result.to_csv('toxic/resources/submission.csv')
