# agents/evaluation_strategy.py

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

# Initialize model
llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0,
    api_key=api_key
)

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
    return {"fcd": 0.0, "fgr": 0.0, "fdf": 0.0, "ecs": 0.0}

def evaluate_text(text: str) -> dict:
    """Evaluates text for hallucinations using the evaluation LLM."""
    if not text:
        return {"fcd": 0.0, "fgr": 0.0, "fdf": 0.0, "ecs": 0.0}

    prompt = PromptTemplate.from_template(EVALUATION_PROMPT)
    llm_input = prompt.format(text=text)

    parser = StrOutputParser()
    response = parser.invoke(llm.invoke(llm_input))

    return _parse_model_response(response)

def normalize_kpis(raw_scores: dict) -> dict:
    """Normalize raw KPI counts to 0-1 range."""
    return {
        "fcd": max(0.0, min(1.0, 1 - raw_scores.get("fcd", 0)/10)),  # fewer errors → closer to 1
        "fgr": max(0.0, min(1.0, raw_scores.get("fgr", 0)/10)),       # higher grounded ratio → closer to 1
        "fdf": max(0.0, min(1.0, raw_scores.get("fdf", 0))),          # already fraction
        "ecs": max(0.0, min(1.0, raw_scores.get("ecs", 0)))           # already fraction
    }

def evaluation_node(config):
    """Returns the evaluation node runnable for LangGraph."""
    def run(state):
        logger.info("Evaluating agent outputs for hallucinations...")

        market_summary = state.get("market_summary", "")
        forecast = state.get("forecast", "")
        risk_report = state.get("risk_report", "")

        evaluation_results = {
            "market_summary": evaluate_text(market_summary),
            "forecast": evaluate_text(forecast),
            "risk_report": evaluate_text(risk_report),
        }

        evaluation_results = {k: normalize_kpis(v) for k, v in evaluation_results.items()}


        logger.info("Evaluation results: %s", evaluation_results)
        
        # ✅ Return only the updated part of the state
        return {"evaluation_results": evaluation_results}

    return run
