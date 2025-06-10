# agents/market_analysis.py

from tools.data_fetcher import fetch_market_data, fetch_news_data
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

logger = get_logger()


llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)


# Load prompt
with open("prompts/market.txt") as f:
    MARKET_PROMPT = f.read()


def market_analysis_node(config):
    def run(state):
        logger.info("Running Market Analysis Agent")

        # Fetch data
        prices = fetch_market_data(state["assets"], state["timestamp"], config)
        headlines = fetch_news_data(state["assets"], config)

        context = {
            "date": state["timestamp"],
            "assets": ", ".join(state["assets"]),
            "price_data": prices,
            "news": headlines,
            "user_question": state.get("user_query", "")
        }

        # Format prompt
        prompt = PromptTemplate.from_template(MARKET_PROMPT)
        llm_input = prompt.format(**context)

        # Call LLM
        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        summary = parser.invoke(llm.invoke(llm_input))

        logger.info("Market Summary Generated")

        state["market_summary"] = summary
        return state

    return run
# This module defines the market analysis agent for the LangGraph multi-agent financial system.
# It fetches market data and news, formats it, and generates a market summary using an LLM.