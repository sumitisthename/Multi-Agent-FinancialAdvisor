# agents/market_analysis.py
"""
Market analysis agent for the LangGraph multi-agent financial analysis system.
"""
from tools.data_fetcher import fetch_market_data, fetch_news_data
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logger
logger = get_logger()

# Validate API key
api_key = os.getenv("GROQ_API_KEY")
print("[DEBUG] Using GROQ Key:", api_key)
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")


# Load prompt template from file
with open("prompts/market.txt") as f:
    MARKET_PROMPT = f.read()

def market_analysis_node():
    """
    Represents the market analysis agent node in the LangGraph.
    """
    def run(state):
        """
        Executes the market analysis agent.
        """
        from langchain_groq import ChatGroq
        logger.info("Running Market Analysis Agent")
        try:
            # Fetch data
            prices = fetch_market_data(state["assets"], state["timestamp"])
            headlines = fetch_news_data(state["assets"])

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

            # Initialize LLM
            llm = ChatGroq(
                model="llama3-8b-8192",
                api_key=os.getenv("GROQ_API_KEY")
            )

            # Generate response
            parser = StrOutputParser()
            summary = parser.invoke(llm.invoke(llm_input))

            logger.info("Market Summary Generated")

            state["market_summary"] = summary
        except Exception as e:
            logger.error(f"Error in market analysis agent: {e}")
            state["market_summary"] = f"Error in market analysis: {e}"
        return state

    return run
