# agents/risk_anomaly.py
"""
Risk and anomaly detection agent for the LangGraph multi-agent financial analysis system.
"""
from tools.quant_models import detect_anomalies
from tools.data_fetcher import fetch_transaction_data
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv(override=True)
logger = get_logger()




# Load prompt
with open("prompts/risk.txt") as f:
    RISK_PROMPT = f.read()


def risk_node(config):
    """
    Represents the risk and anomaly detection agent node in the LangGraph.
    """
    def run(state):
        """
        Executes the risk and anomaly detection agent.
        """
        from langchain_groq import ChatGroq
        logger.info("Running Risk & Anomaly Detection Agent")
        try:
            assets = state["assets"]
            date = state["timestamp"]
            market_summary = state.get("market_summary", "")
            forecast = state.get("forecast", "")

            # Simulated transaction/account data (optional extension)
            transactions = fetch_transaction_data(assets, date)
            config = load_config()  # Load configuration before using it
            anomalies = detect_anomalies(transactions, forecast, config)

            context = {
                "date": date,
                "assets": ", ".join(assets),
                "forecast": forecast,
                "market_summary": market_summary,
                "anomaly_report": anomalies,
                "user_question": state.get("user_query", "")
            }

            prompt = PromptTemplate.from_template(RISK_PROMPT)
            llm_input = prompt.format(**context)

            # Initialize LLM
            llm = ChatGroq(
                model="gemma2-9b-it",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0
            )

            parser = StrOutputParser()
            report = parser.invoke(llm.invoke(llm_input))

            logger.info("Anomaly Report Generated")

            state["risk_report"] = report
            state["anomalies"] = anomalies
        except Exception as e:
            logger.error(f"Error in risk and anomaly detection agent: {e}")
            state["risk_report"] = f"Error in risk and anomaly detection: {e}"
        return state

    return run
