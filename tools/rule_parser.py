# tools/rule_parser.py

import os
import json
from utils.logger import get_logger
from memory.embeddings import search_embedding

logger = get_logger()
POLICY_CHUNKS_PATH = "./memory/policy_chunks.json"

def extract_compliance_rules(query: str, top_k: int = 3) -> str:
    """
    Retrieves the most relevant compliance rules for a given query using a RAG pipeline.
    """
    logger.info(f"Retrieving compliance rules for query: '{query}'")

    # 1. Search for relevant chunk IDs in the vector store
    try:
        retrieved_ids = search_embedding(query, top_k=top_k)
        logger.info(f"Retrieved chunk IDs: {retrieved_ids}")
    except Exception as e:
        logger.error(f"Error searching for embeddings: {e}")
        return "Error: Could not retrieve compliance rules from the vector store."

    # 2. Load the policy chunks map
    try:
        with open(POLICY_CHUNKS_PATH, "r") as f:
            policy_chunks = json.load(f)
    except FileNotFoundError:
        logger.error(f"Policy chunks file not found at {POLICY_CHUNKS_PATH}")
        return "Error: Policy chunks file not found."
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {POLICY_CHUNKS_PATH}")
        return "Error: Could not parse policy chunks file."

    # 3. Retrieve the rule text for the given IDs
    retrieved_rules = []
    for chunk_id in retrieved_ids:
        # The IDs from FAISS are 1-based, but our JSON map keys are strings
        rule_text = policy_chunks.get(str(chunk_id))
        if rule_text:
            retrieved_rules.append(rule_text)
        else:
            logger.warning(f"Chunk ID {chunk_id} not found in policy_chunks.json")

    if not retrieved_rules:
        return "No relevant compliance rules found for the given query."

    logger.info(f"Successfully retrieved {len(retrieved_rules)} compliance rule(s).")
    return "\n---\n".join(retrieved_rules)
