# index_policies.py
import os
import json
import re
from memory.embeddings import embed_text, store_embedding
from utils.logger import get_logger

logger = get_logger()

POLICY_DOCUMENT_PATH = "policy.txt"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./memory/vector_store.faiss")
POLICY_CHUNKS_PATH = "./memory/policy_chunks.json"

def chunk_text(text):
    """
    Splits the policy document into chunks based on sections.
    """
    logger.info("Chunking policy document")
    # Split by section headers (e.g., "### Section 1: ...")
    raw_chunks = re.split(r'(?m)^###\s', text)
    chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]
    return chunks

def run_indexing():
    """
    Reads the policy document, chunks it, and stores the embeddings.
    """
    logger.info("Starting policy document indexing process")

    # Clean up old index and chunks if they exist
    if os.path.exists(VECTOR_DB_PATH):
        os.remove(VECTOR_DB_PATH)
        logger.info(f"Removed existing vector store at {VECTOR_DB_PATH}")
    if os.path.exists(POLICY_CHUNKS_PATH):
        os.remove(POLICY_CHUNKS_PATH)
        logger.info(f"Removed existing policy chunks at {POLICY_CHUNKS_PATH}")

    try:
        with open(POLICY_DOCUMENT_PATH, "r") as f:
            policy_text = f.read()
    except FileNotFoundError:
        logger.error(f"Policy document not found at {POLICY_DOCUMENT_PATH}")
        return

    chunks = chunk_text(policy_text)
    chunk_map = {}

    for i, chunk in enumerate(chunks):
        # Generate embedding
        vector = embed_text(chunk)

        # Store the embedding with a unique ID
        metadata_id = i + 1  # Use a 1-based index for IDs
        store_embedding(vector, metadata_id)

        # Store the chunk text in the map
        chunk_map[metadata_id] = chunk
        logger.info(f"Indexed chunk {metadata_id}/{len(chunks)}")

    # Save the chunk map to a file
    with open(POLICY_CHUNKS_PATH, "w") as f:
        json.dump(chunk_map, f, indent=2)

    logger.info(f"Indexing complete. {len(chunks)} chunks indexed and stored.")
    logger.info(f"Policy chunk map saved to {POLICY_CHUNKS_PATH}")

if __name__ == "__main__":
    run_indexing()
