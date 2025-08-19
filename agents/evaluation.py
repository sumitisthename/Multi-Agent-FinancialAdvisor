# agents/evaluation.py

import os
import json
from dotenv import load_dotenv
from pathlib import Path
from utils.logger import get_logger
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

logger = get_logger()

# Validate API key early to avoid 401 later
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it before running.")

# Load evaluation prompt
with open("prompts/evaluation.txt", "r", encoding="utf-8") as f:
    EVALUATION_PROMPT = f.read()

def _parse_model_response(response_content: str) -> dict:
    """Parses JSON output from the model safely."""
    try:
        clean_response = (
            response_content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        return json.loads(clean_response)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON from model output: %s", response_content)
    except Exception as e:
        logger.error("Unexpected error while parsing model output: %s", e)
    return {"fcd": 0, "fgr": 0, "fdf": 0, "ecs": 0.0}

def get_raw_kpis(text: str) -> dict:
    """Gets raw KPI counts from the evaluation LLM."""
    if not text:
        return {"fcd": 0, "fgr": 0, "fdf": 0, "ecs": 0.0}

    llm = ChatGroq(
        model="gemma2-9b-it",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = PromptTemplate.from_template(EVALUATION_PROMPT)
    llm_input = prompt.format(text=text)

    parser = StrOutputParser()
    response = parser.invoke(llm.invoke(llm_input))

    return _parse_model_response(response)

def calculate_ths(kpis: dict, weights: dict = None) -> float:
    """Calculates the Total Hallucination Score (THS)."""
    if weights is None:
        weights = {"w1": 0.25, "w2": 0.25, "w3": 0.25, "w4": 0.25}

    fcd = kpis.get("fcd", 0)
    fgr = kpis.get("fgr", 0)
    fdf = kpis.get("fdf", 0)
    ecs = kpis.get("ecs", 0)

    # Using the weighted formula from the paper. Assuming NA=1 for individual text evaluation.
    # THSn = (w1 * FCDn - (w2 * FGRn + w3 * FDFn + w4 * ECSn)) / (NA * (w1 + w2 + w3 + w4))
    # Since sum of weights is 1, the denominator is NA. With NA=1, it simplifies.
    numerator = weights["w1"] * fcd - (weights["w2"] * fgr + weights["w3"] * fdf + weights["w4"] * ecs)
    denominator = sum(weights.values())

    if denominator == 0:
        return 0.0

    return numerator / denominator


def evaluation_node(config):
    """Returns the evaluation node runnable for LangGraph."""
    def run(state):
        logger.info("Evaluating agent outputs for hallucinations...")

        texts_to_evaluate = {
            "market_summary": state.get("market_summary", ""),
            "forecast": state.get("forecast", ""),
            "risk_report": state.get("risk_report", "")
        }

        evaluation_results = {}
        for name, text in texts_to_evaluate.items():
            if not text:
                evaluation_results[name] = {
                    "raw_kpis": {"fcd": 0, "fgr": 0, "fdf": 0, "ecs": 0.0},
                    "raw_ths": 0.0,
                    "normalized_kpis": {"fcd": 0, "fgr": 0, "fdf": 0, "ecs": 0.0},
                    "ths": 0.0,
                    "word_count": 0
                }
                continue

            word_count = len(text.split())
            raw_kpis = get_raw_kpis(text)
            raw_ths = calculate_ths(raw_kpis)

            if word_count > 0:
                normalized_kpis = {
                    "fcd": (raw_kpis.get("fcd", 0) / word_count) * 100,
                    "fgr": (raw_kpis.get("fgr", 0) / word_count) * 100,
                    "fdf": (raw_kpis.get("fdf", 0) / word_count) * 100,
                    "ecs": raw_kpis.get("ecs", 0) # ECS is already a 0-1 score
                }
            else:
                normalized_kpis = {"fcd": 0, "fgr": 0, "fdf": 0, "ecs": 0.0}

            ths = calculate_ths(normalized_kpis)

            evaluation_results[name] = {
                "raw_kpis": raw_kpis,
                "raw_ths": raw_ths,
                "normalized_kpis": normalized_kpis,
                "ths": ths,
                "word_count": word_count
            }

        logger.info("Evaluation results: %s", json.dumps(evaluation_results, indent=2))
        
        return {"evaluation_results": evaluation_results}

    return run
