# memory/embeddings.py

import os
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from utils.logger import get_logger

logger = get_logger()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./memory/vector_store.faiss")

model = SentenceTransformer(EMBEDDING_MODEL)

def embed_text(text):
    logger.info("Generating embeddings")
    return model.encode([text])[0]

def store_embedding(vector, metadata_id):
    logger.info(f"Storing embedding for ID {metadata_id}")

    index = load_index()
    index.add_with_ids(np.array([vector]).astype("float32"), np.array([metadata_id]))
    faiss.write_index(index, VECTOR_DB_PATH)

def search_embedding(query, top_k=3):
    logger.info("Searching similar embeddings")
    vector = embed_text(query)
    index = load_index()
    D, I = index.search(np.array([vector]).astype("float32"), top_k)
    return I[0]

def load_index():
    if os.path.exists(VECTOR_DB_PATH):
        return faiss.read_index(VECTOR_DB_PATH)
    else:
        return faiss.IndexFlatL2(model.get_sentence_embedding_dimension())
