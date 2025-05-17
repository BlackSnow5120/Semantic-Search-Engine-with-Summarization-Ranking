from flask import Flask, request, jsonify
from webcrawler import WebCrawler
from inverted_index import build_inverted_index
from semantic import build_semantic_index
from search_with_summary import search_with_summary
from semantic_serach import search
import os
import json
import pickle
from flask_cors import CORS
import numpy as np  # Import NumPy

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
DOCS_FILE = "documents.json"
INVERTED_INDEX_FILE = "inverted_index.json"
SEMANTIC_EMBEDDINGS_FILE = "semantic_embeddings.pkl"

@app.route("/build", methods=["POST"])
def build_data():
    base_url = request.json.get("base_url","https://en.wikipedia.org/wiki/Web_crawler")
    max_pages = request.json.get("max_pages", 50)

    if not os.path.exists(DOCS_FILE):
        crawler = WebCrawler(base_url, max_pages)
        docs = crawler.crawl()
        with open(DOCS_FILE, "w") as f:
            json.dump(docs, f)
    else:
        with open(DOCS_FILE, "r") as f:
            docs = json.load(f)

    if not os.path.exists(INVERTED_INDEX_FILE):
        inverted_index = build_inverted_index(docs)
        with open(INVERTED_INDEX_FILE, "w") as f:
            json.dump(inverted_index, f)

    if not os.path.exists(SEMANTIC_EMBEDDINGS_FILE):
        embeddings = build_semantic_index(docs)
        with open(SEMANTIC_EMBEDDINGS_FILE, "wb") as f:
            pickle.dump(embeddings, f)

    return jsonify({"status": "Build complete."})

def convert_numpy_floats(obj):
    if isinstance(obj, np.float32):
        return float(obj)
    elif isinstance(obj, list):
        return [convert_numpy_floats(elem) for elem in obj]
    elif isinstance(obj, dict):
        return {k: convert_numpy_floats(v) for k, v in obj.items()}
    return obj

@app.route("/search", methods=["POST"])
def search_endpoint():
    query = request.json.get("query")
    alpha = float(request.json.get("alpha"))
    top_k = int(request.json.get("top_k"))
    with open(DOCS_FILE, "r") as f:
        docs = json.load(f)
    with open(INVERTED_INDEX_FILE, "r") as f:
        inverted_index = json.load(f)
    with open(SEMANTIC_EMBEDDINGS_FILE, "rb") as f:
        semantic_embeddings = pickle.load(f)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = search(query, inverted_index, semantic_embeddings, model, docs, alpha=alpha, top_k=top_k)
    return jsonify(convert_numpy_floats(results)) 

@app.route("/search_with_summary", methods=["POST"])
def search_summary_endpoint():
    query = request.args.get("query","machine leaning")
    alpha = float(request.args.get("alpha", 0.5))
    top_k = int(request.args.get("top_k", 5))

    with open(DOCS_FILE, "r") as f:
        docs = json.load(f)
    with open(INVERTED_INDEX_FILE, "r") as f:
        inverted_index = json.load(f)
    with open(SEMANTIC_EMBEDDINGS_FILE, "rb") as f:
        semantic_embeddings = pickle.load(f)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = search_with_summary(query, inverted_index, semantic_embeddings, model, docs, alpha=alpha, top_k=top_k)
    return jsonify(convert_numpy_floats(results))  

if __name__ == "__main__":
    app.run(debug=True,port=5000)