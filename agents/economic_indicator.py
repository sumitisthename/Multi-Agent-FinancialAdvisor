# agents/economic_indicator_agent.py

from tools.economic_data_tool import fetch_gdp_data, fetch_pce_data, fetch_employment_data
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
    model="gemma2-9b-it",
    api_key=api_key,
    temperature=0.2
)

# Load prompt template from file
with open("prompts/economic.txt") as f:
    ECONOMIC_PROMPT = f.read()

def economic_indicator_node():
    def run(state):
        logger.info("Running Economic Indicator Agent")

        # Fetch economic data
        try:
            gdp_data = fetch_gdp_data()
            logger.info(f"Fetched GDP data: {gdp_data}")
        except Exception as e:
            logger.error(f"Error fetching GDP data: {e}")
            gdp_data = {"error": str(e)}

        try:
            pce_data = fetch_pce_data()
            logger.info(f"Fetched PCE data: {pce_data}")
        except Exception as e:
            logger.error(f"Error fetching PCE data: {e}")
            pce_data = {"error": str(e)}

        try:
            employment_data = fetch_employment_data()
            logger.info(f"Fetched employment data: {employment_data}")
        except Exception as e:
            logger.error(f"Error fetching employment data: {e}")
            employment_data = {"error": str(e)}

        # Prepare context for LLM
        context = {
            "gdp_data": gdp_data,
            "pce_data": pce_data,
            "employment_data": employment_data,
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
