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


llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)


# Load prompt
with open("prompts/coordinator.txt") as f:
    COORDINATOR_PROMPT = f.read()


def coordinator_node(config):
    def run(state):
        logger.info("Running Coordinator Agent")

        market = state.get("market_summary", "")
        forecast = state.get("forecast", "")
        risk = state.get("risk_report", "")
        compliance = state.get("compliance_review", "")
        date = state["timestamp"]

        context = {
            "date": date,
            "market": market,
            "forecast": forecast,
            "risk": risk,
            "compliance": compliance
        }

        prompt = PromptTemplate.from_template(COORDINATOR_PROMPT)
        llm_input = prompt.format(**context)

        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        print("\n=== Coordinator Prompt Input ===\n", llm_input, "\n============================\n")
        final_decision = parser.invoke(llm.invoke(llm_input))

        logger.info("Final Decision Synthesized")

        state["final_decision"] = final_decision
        return state

    return run
# This module defines the coordinator agent for the LangGraph multi-agent financial system.
# It synthesizes inputs from other agents to generate a final decision using an LLM.    
# The coordinator agent acts as the central decision-maker, integrating insights from market analysis,
# forecasting, risk assessment, and compliance evaluation to provide a comprehensive overview and final recommendation.
# The coordinator's role is crucial for ensuring that all aspects of the financial analysis are considered
# and that the final decision aligns with the overall strategy and compliance requirements.
# The coordinator agent is designed to be flexible and adaptable, allowing it to incorporate new data sources or agents as needed.