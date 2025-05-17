import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import defaultdict
import json

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = word_tokenize(text.lower())
    filtered = [t for t in tokens if t.isalpha() and t not in stop_words]
    return filtered

def build_inverted_index(docs):
    inverted_index = defaultdict(set)
    for doc_id, doc in docs.items():
        tokens = preprocess(doc['text'])
        for token in set(tokens): 
            inverted_index[token].add(doc_id)
    inverted_index = {k: list(v) for k,v in inverted_index.items()}
    return inverted_index

