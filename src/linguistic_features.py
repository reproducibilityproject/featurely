# This Source Code Form is subject to the terms of the MIT
# License. If a copy of the same was not distributed with this
# file, You can obtain one at
# https://github.com/reproducibilityproject/featurely/blob/main/LICENSE

import re
import sys
import nltk
import spacy
import string
import textacy
import numpy as np
import pandas as pd
from math import sqrt, log
from itertools import groupby
from nltk.collocations import *
from collections import Counter
from nltk.corpus import stopwords
from collections import defaultdict
from itertools import chain, product
from nltk.corpus import wordnet as wn
from nltk.tokenize import RegexpTokenizer
from nltk import word_tokenize as tokenize
from nltk.stem.porter import PorterStemmer as stemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from textstat.textstat import textstatistics, easy_word_set, legacy_round

"""
m1 - The number of all word forms a text consists
m2 - The sum of the products of each observed frequency to the power of two
     and the number of word types observed with that frequency
"""

# function for computing word count
def compute_word_count(sentence):
    tokenizer = RegexpTokenizer(r'\w+')
    return len(tokenizer.tokenize(sentence))

# function for computing average word length
def compute_average_word_length(sentence):
    return np.mean([len(words) for words in sentence.split()])

# function for computing average sentence length
def compute_average_sentence_length(sentence):
    sentence = re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", sentence)
    return np.mean([len(words) for words in sentence])

# function for calculating frequency of words > avg word length
def freq_of_words_great_sent_len(sentence):
    result = []
    avg_word_len = compute_average_word_length(sentence)
    # sentence = re.split("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", sentence)
    sentence = Counter(sentence.split())
    for key, value in sentence.items():
        if len(key) > avg_word_len:
            result.append(value)
#             print (key, value)
    return sum(result)

# function for tokenizing words
def tokenize(sentence):
    return re.split(r"[^0-9A-Za-z\-'_]+", sentence)

# function for breaking the document into sentences
def break_sentences(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    return doc.sents

# count the syllables
def syllables_count(word):
    return textstatistics().syllable_count(word)

# function for computing lexical diversity as a measure of yules-k
def compute_yules_k_for_text(sentence):
    tokens = tokenize(sentence)
    counter = Counter(token.upper() for token in tokens)

    #compute number of word forms in a given sentence/text
    m1 = sum(counter.values())
    m2 = sum([frequency ** 2 for frequency in counter.values()])

    #compute yules k measure and return the value
    yules_k = 10000/((m1 * m1) / (m2 - m1))
    return yules_k

# function for eliminating anything other than alphabets in a text
def words_in_sentence(sentence):
    w = [words.strip("0123456789!:,.?()[]{}") for words in sentence.split()]
    return filter(lambda x: len(x) > 0, w)

# function for computing lexical diversity as a measure of yules-I
def compute_yules_i_for_text(sentence):
    dictionary = {}
    stm = stemmer()

    for word in words_in_sentence(sentence):
        word = stm.stem(word).lower()
        try:
            dictionary[word] += 1
        except:
            dictionary[word] = 1

    m1 = float(len(dictionary))
    m2 = sum([len(list(grouped_values)) * (frequency ** 2) for frequency, grouped_values in groupby(sorted(dictionary.values()))])

    # compute yules i and return the value
    try:
        yules_i = (m1 * m1) / (m2 - m1)
        return yules_i
    except ZeroDivisionError:
        return 0

# polysemy for the content words
def polysemy(group):
    stop = stopwords.words('english')
    str1 = [i for i in group.split() if i not in stop]
    a = list()
    for w in str1:
        if(len(wn.synsets(w)) > 1):
            a.append(w)
    return len(a)

# Return total Difficult Words in a text
def complex_words(text):
    words = []
    sentences = break_sentences(text)
    for sentence in sentences:
        words += [token for token in sentence]

    diff_words_set = set()

    for word in words:
        if word not in easy_word_set and textstatistics().syllable_count(str(word)) >= 2:
            diff_words_set.add(word)

    return len(diff_words_set)

