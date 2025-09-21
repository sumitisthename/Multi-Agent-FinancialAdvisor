# agents/compliance_monitor.py
"""
Compliance monitoring agent for the LangGraph multi-agent financial analysis system.
"""
from tools.rule_parser import extract_compliance_rules
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv(override=True)
logger = get_logger()

# Load prompt
with open("prompts/compliance.txt") as f:
    COMPLIANCE_PROMPT = f.read()


def compliance_node(config):
    """
    Represents the compliance monitoring agent node in the LangGraph.
    """
    def run(state):
        """
        Executes the compliance monitoring agent.
        """
        from langchain_groq import ChatGroq
        logger.info("Running Compliance Monitoring Agent")
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")

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

            # Initialize LLM
            llm = ChatGroq(
                model="gemma2-9b-it",
                api_key=api_key,
                temperature=0.2
            )

            parser = StrOutputParser()
            review = parser.invoke(llm.invoke(llm_input))

            logger.info("Compliance Evaluation Completed")

            state["compliance_review"] = review
        except Exception as e:
            logger.error(f"Error in compliance monitoring agent: {e}")
            state["compliance_review"] = f"Error in compliance monitoring: {e}"
        return state

    return run
# This module defines the compliance monitoring agent for the LangGraph multi-agent financial system.
# It evaluates proposed actions against compliance rules and risk alerts, generating a compliance review using an LLM.