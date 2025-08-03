# agents/compliance_monitor.py

from tools.rule_parser import extract_compliance_rules
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
with open("prompts/compliance.txt") as f:
    COMPLIANCE_PROMPT = f.read()


def compliance_node(config):
    def run(state):
        logger.info("Running Compliance Monitoring Agent")

        proposed_action = state.get("forecast", "")
        risk_alerts = state.get("risk_report", "")
        date = state["timestamp"]

        rules = extract_compliance_rules(config)

        context = {
            "date": date,
            "rules": rules,
            "action_summary": proposed_action,
            "risk_summary": risk_alerts,
            "user_question": state.get("user_query", "")
        }

        prompt = PromptTemplate.from_template(COMPLIANCE_PROMPT)
        llm_input = prompt.format(**context)

        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        review = parser.invoke(llm.invoke(llm_input))

        logger.info("Compliance Evaluation Completed")

        state["compliance_review"] = review
        return state

    return run
# This module defines the compliance monitoring agent for the LangGraph multi-agent financial system.
# It evaluates proposed actions against compliance rules and risk alerts, generating a compliance review using an LLM.