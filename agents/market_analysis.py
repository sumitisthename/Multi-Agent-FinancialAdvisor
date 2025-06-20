# agents/market_analysis.py

from tools.data_fetcher import fetch_market_data, fetch_news_data
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logger
logger = get_logger()

# Load config
config = load_config()

# Validate API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")

# Initialize LLM globally with API key
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)

# Load prompt template from file
with open("prompts/market.txt") as f:
    MARKET_PROMPT = f.read()

def market_analysis_node(config):
    def run(state):
        logger.info("Running Market Analysis Agent")

        # Fetch data
        prices = fetch_market_data(state["assets"], state["timestamp"], config)
        headlines = fetch_news_data(state["assets"], config)

        # Prepare prompt context
        context = {
            "date": state["timestamp"],
            "assets": ", ".join(state["assets"]),
            "price_data": prices,
            "news": headlines,
            "user_question": state.get("user_query", "")
        }

        # Format and run prompt
        prompt = PromptTemplate.from_template(MARKET_PROMPT)
        llm_input = prompt.format(**context)

        # Generate response
        parser = StrOutputParser()
        summary = parser.invoke(llm.invoke(llm_input))

        logger.info("Market Summary Generated")

        state["market_summary"] = summary
        return state

    return run
