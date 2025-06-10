# agents/forecasting_strategy.py

from tools.quant_models import run_forecast_model
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
with open("prompts/forecast.txt") as f:
    FORECAST_PROMPT = f.read()


def forecasting_node(config):
    def run(state):
        logger.info("Running Forecasting Agent")

        market_summary = state.get("market_summary", "")
        assets = state["assets"]
        date = state["timestamp"]

        forecast_data = run_forecast_model(assets, date, config)

        context = {
            "date": date,
            "assets": ", ".join(assets),
            "market_summary": market_summary,
            "forecast_table": forecast_data,
            "user_question": state.get("user_query", "")
        }

        prompt = PromptTemplate.from_template(FORECAST_PROMPT)
        llm_input = prompt.format(**context)

        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        output = parser.invoke(llm.invoke(llm_input))

        logger.info("Forecast Generated")

        state["forecast"] = output
        return state

    return run
