# agents/risk_anomaly.py

from tools.quant_models import detect_anomalies
from tools.data_fetcher import fetch_transaction_data
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
logger = get_logger()

print(os.getenv("GROQ_API_KEY"))


llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)


# Load prompt
with open("prompts/risk.txt") as f:
    RISK_PROMPT = f.read()


def risk_node(config):
    def run(state):
        logger.info("Running Risk & Anomaly Detection Agent")

        assets = state["assets"]
        date = state["timestamp"]
        market_summary = state.get("market_summary", "")
        forecast = state.get("forecast", "")

        # Simulated transaction/account data (optional extension)
        transactions = fetch_transaction_data(assets, date, config)
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

        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        report = parser.invoke(llm.invoke(llm_input))

        logger.info("Anomaly Report Generated")

        state["risk_report"] = report
        state["anomalies"] = anomalies
        return state

    return run
