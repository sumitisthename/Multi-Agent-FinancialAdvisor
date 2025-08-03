# tools/rule_parser.py

import os
from utils.logger import get_logger

logger = get_logger()


def extract_compliance_rules(config):
    # In practice, parse legal docs or vector DB results
    logger.info("Extracting compliance rules (stub)")

    return (
        "- No trade should exceed $10M or 5% of daily volume.\n"
        "- Insiders must not trade during blackout periods.\n"
        "- Maintain minimum liquidity of 15% for each position."
    )
