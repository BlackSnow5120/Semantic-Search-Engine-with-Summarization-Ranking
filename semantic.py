from sentence_transformers import SentenceTransformer
import numpy as np
import pickle

def build_semantic_index(docs, model_name='all-MiniLM-L6-v2'):
    """
    docs: dict of doc_id -> { 'url':..., 'text':... }
    returns: dict doc_id -> embedding vector (numpy array)
    """
    model = SentenceTransformer(model_name)
    embeddings = {}
    for doc_id, doc in docs.items():
        emb = model.encode(doc['text'], convert_to_numpy=True)
        embeddings[doc_id] = emb
    return embeddings
