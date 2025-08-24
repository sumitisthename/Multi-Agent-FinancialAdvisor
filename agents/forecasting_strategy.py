# agents/forecasting_strategy.py
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.quant_models import run_forecast_model
from config.settings import load_config
from utils.logger import get_logger
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from memory.memory_store import log_decision, retrieve_recent_memory
from dotenv import load_dotenv

load_dotenv()
logger = get_logger()

# Initialize LLM once
llm = ChatGroq(
    model="gemma2-9b-it",
    api_key=os.getenv("GROQ_API_KEY")
)

# Load forecast prompt
with open("prompts/forecast.txt") as f:
    FORECAST_PROMPT = f.read()


def forecasting_node(config):
    def run(state):
        logger.info("Running Forecasting Agent")

        market_summary = state.get("market_summary", "")
        assets = list(set(state["assets"]))
        date = state["timestamp"]

        # Retrieve recent lessons from memory
        lessons = retrieve_recent_memory(config)

        logger.info("ARIMA model invoked for assets: %s", assets)

        forecast_data, mape = run_forecast_model(assets, date, config)

        context = {
            "date": date,
            "assets": ", ".join(assets),
            "market_summary": market_summary,
            "forecast_table": forecast_data,
            "lessons": lessons,
            "user_question": state.get("user_query", "")
        }

        # Format prompt
        prompt = PromptTemplate.from_template(FORECAST_PROMPT)

        # Run through pipeline
        chain = prompt | llm | StrOutputParser()
        output = chain.invoke(context)

        logger.info("Forecast Generated")

        # Update state
        state["forecast"] = output
        state["mape"] = mape
        log_decision(state, output, config)
        return state

    return run
