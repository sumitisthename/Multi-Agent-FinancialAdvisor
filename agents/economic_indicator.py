# agents/economic_indicator_agent.py

from tools.economic_data_tool import fetch_economic_indicator
from config.settings import load_config
from utils.logger import get_logger
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Setup logger
logger = get_logger()

# Load config
config = load_config()

# Validate API key
api_key = os.getenv("GROQ_API_KEY")
print("[DEBUG] Using GROQ Key:", api_key)
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")

# Initialize LLM globally with API key
llm = ChatGroq(
    model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.2
)

# Load prompt template from file
with open("prompts/economic.txt") as f:
    ECONOMIC_PROMPT = f.read()

def economic_indicator_node():
    def run(state):
        logger.info("Running Economic Indicator Agent")

        # Define indicators to fetch
        indicators = [
            "NY.GDP.MKTP.CD",       # GDP (current US$)
            "FP.CPI.TOTL.ZG",       # Inflation, consumer prices (annual %)
            "SL.UEM.TOTL.ZS"        # Unemployment rate (% of labor force)
        ]

        results = []
        for ind in indicators:
            try:
                result = fetch_economic_indicator(ind, country_code="US")
                logger.info(f"Fetched economic indicator {ind}: {result}")
                results.append(result)
            except Exception as e:
                logger.error(f"Error fetching {ind}: {e}")
                results.append({"indicator": ind, "error": str(e)})

        # Prepare context for LLM
        context = {
            "indicators": results,
            "user_question": state.get("user_query", "")
        }

        # Format and run prompt
        prompt = PromptTemplate.from_template(ECONOMIC_PROMPT)
        llm_input = prompt.format(**context)

        # Generate response
        parser = StrOutputParser()
        summary = parser.invoke(llm.invoke(llm_input))

        logger.info("Economic Summary Generated")

        state["economic_indicators"] = summary
        return state

    return run
