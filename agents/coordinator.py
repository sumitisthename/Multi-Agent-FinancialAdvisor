# agents/coordinator.py

from config.settings import load_config
from utils.logger import get_logger
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
logger = get_logger()

print(os.getenv("GROQ_API_KEY"))

logger = get_logger()

# Load prompt
with open("prompts/coordinator.txt") as f:
    COORDINATOR_PROMPT = f.read()


def coordinator_node(config):
    def run(state):
        logger.info("Running Coordinator Agent")
        try:
            economic_indicators = state.get("economic_indicators", [])
            if not economic_indicators:
                raise ValueError("No economic indicators found in state.")
            market = state.get("market_summary", "")
            if not market:
                raise ValueError("Market summary is missing in state.")
            forecast = state.get("forecast", "")
            if not forecast:
                raise ValueError("Forecast is missing in state.")
            risk = state.get("risk_report", "")
            if not risk:
                raise ValueError("Risk report is missing in state.")
            compliance = state.get("compliance_review", "")
            if not compliance:
                raise ValueError("Compliance review is missing in state.")
            date = state["timestamp"]

            context = {
                "date": date,
                "economic_indicators": economic_indicators,
                "market": market,
                "forecast": forecast,
                "risk": risk,
                "compliance": compliance,
                "user_question": state.get("user_query", "")
            }

            prompt = PromptTemplate.from_template(COORDINATOR_PROMPT)
            llm_input = prompt.format(**context)

            llm = ChatGroq(
                model="gemma2-9b-it",
                api_key=os.getenv("GROQ_API_KEY")
            )
            parser = StrOutputParser()
            print("\n=== Coordinator Prompt Input ===\n", llm_input, "\n============================\n")
            final_decision = parser.invoke(llm.invoke(llm_input))

            logger.info("Final Decision Synthesized")

            state["final_decision"] = final_decision
            return state
        except Exception as e:
            logger.error(f"Error in coordinator_node: {e}")
            state["final_decision"] = f"Error: {e}"
        return state

    return run
# This module defines the coordinator agent for the LangGraph multi-agent financial system.
# It synthesizes inputs from other agents to generate a final decision using an LLM.    
# The coordinator agent acts as the central decision-maker, integrating insights from market analysis,
# forecasting, risk assessment, and compliance evaluation to provide a comprehensive overview and final recommendation.
# The coordinator's role is crucial for ensuring that all aspects of the financial analysis are considered
# and that the final decision aligns with the overall strategy and compliance requirements.
# The coordinator agent is designed to be flexible and adaptable, allowing it to incorporate new data sources or agents as needed.