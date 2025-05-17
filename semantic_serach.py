import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalpha() and t not in stop_words]

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1)*np.linalg.norm(vec2) + 1e-10)

model = SentenceTransformer('all-MiniLM-L6-v2')
def keyword_search(query_tokens, inverted_index):
    """
    Returns dict doc_id -> keyword score (e.g. term frequency in query)
    """
    doc_scores = Counter()
    for token in query_tokens:
        if token in inverted_index:
            for doc_id in inverted_index[token]:
                doc_scores[doc_id] += 1
    return doc_scores
def semantic_search(query, semantic_embeddings, model, top_k=10):
    query_emb = model.encode(query, convert_to_numpy=True)
    scores = {}
    for doc_id, emb in semantic_embeddings.items():
        scores[doc_id] = cosine_similarity(query_emb, emb)
    top_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return dict(top_docs)
def combine_scores(kw_scores, sem_scores, alpha=0.5):
    """
    alpha: weight for keyword score (0-1), (1-alpha) for semantic score
    Normalize scores before combining
    """
    all_doc_ids = set(kw_scores.keys()).union(sem_scores.keys())

    max_kw = max(kw_scores.values()) if kw_scores else 1
    max_sem = max(sem_scores.values()) if sem_scores else 1

    combined_scores = {}
    for doc_id in all_doc_ids:
        kw_score = kw_scores.get(doc_id, 0) / max_kw
        sem_score = sem_scores.get(doc_id, 0) / max_sem
        combined_scores[doc_id] = alpha * kw_score + (1 - alpha) * sem_score

    ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked
def search(query, inverted_index, semantic_embeddings, model, docs, alpha=0.5, top_k=5):
    query_tokens = preprocess(query)
    kw_scores = keyword_search(query_tokens, inverted_index)
    sem_scores = semantic_search(query, semantic_embeddings, model, top_k=top_k*3)

    combined = combine_scores(kw_scores, sem_scores, alpha=alpha)
    top_results = combined[:top_k]

    results = []
    for doc_id, score in top_results:
        doc = docs[str(doc_id)]
        snippet = doc['text'][:200].replace('\n',' ') + '...' 
        if(score != 0.000 ):
            results.append({'doc_id': doc_id, 'url': doc['url'], 'score': score, 'snippet': snippet})

    return results


