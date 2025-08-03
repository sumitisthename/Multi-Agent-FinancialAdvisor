# tools/rule_parser.py
"""
Rule parsing tools for the LangGraph multi-agent financial analysis system.
"""
import os
from utils.logger import get_logger

logger = get_logger()


def extract_compliance_rules():
    """
    Extracts compliance rules from a set of documents.
    """
    # In practice, parse legal docs or vector DB results
    logger.info("Extracting compliance rules (stub)")

    return (
        "- No trade should exceed $10M or 5% of daily volume.\n"
        "- Insiders must not trade during blackout periods.\n"
        "- Maintain minimum liquidity of 15% for each position."
    )
