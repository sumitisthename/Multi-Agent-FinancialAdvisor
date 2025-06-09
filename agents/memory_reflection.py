# agents/memory_reflection.py

from memory.memory_store import log_decision, retrieve_recent_memory
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


# Load reflection prompt
with open("prompts/coordinator.txt") as f:
    REFLECTION_PROMPT = f.read().replace("Decision", "Reflection")  # reuse structure


def memory_reflection_node(config):
    def run(state):
        logger.info("Running Memory Reflection Agent")

        date = state["timestamp"]
        decision = state.get("final_decision", "")
        market = state.get("market_summary", "")
        forecast = state.get("forecast", "")
        risk = state.get("risk_report", "")
        compliance = state.get("compliance_review", "")

        memory_snippets = retrieve_recent_memory(config)

        context = {
            "date": date,
            "memory_log": memory_snippets,
            "market": market,
            "forecast": forecast,
            "risk": risk,
            "compliance": compliance,
            "decision": decision
        }

        prompt = PromptTemplate.from_template(REFLECTION_PROMPT)
        llm_input = prompt.format(**context)

        llm = ChatGroq(model="llama3-8b-8192")
        parser = StrOutputParser()
        lesson = parser.invoke(llm.invoke(llm_input))

        logger.info("Reflection Completed - Lesson Logged")

        log_decision(state, lesson, config)
        state["reflection_lesson"] = lesson
        return state

    return run
# This module defines the memory reflection agent for the LangGraph multi-agent financial system.
# It reviews past decisions and lessons learned, generating a reflection lesson using an LLM.           
# The memory reflection agent is designed to enhance the system's learning capabilities by analyzing past decisions,
# identifying patterns, and extracting valuable lessons that can inform future actions.
# The agent retrieves recent memory snippets, formats them with current context, and uses an LLM to generate insights.
# This reflection process helps the system adapt and improve over time, ensuring that it learns from both successes and failures.
# The memory reflection agent plays a crucial role in the LangGraph system by providing a feedback loop
# that allows the agents to evolve and refine their strategies based on historical performance.
# The agent's output is logged for future reference, contributing to the system's overall knowledge base.
# The memory reflection agent is essential for continuous improvement and strategic alignment in the financial analysis process.
# It ensures that the system not only reacts to current data but also learns from its past actions,
# creating a more robust and informed decision-making framework.
# The agent's design allows it to be flexible and adaptable, incorporating new data sources or agents as needed.
# This adaptability ensures that the LangGraph system remains relevant and effective in a dynamic financial environment.
# The memory reflection agent is a key component of the LangGraph multi-agent financial system,
# providing a mechanism for ongoing learning and strategic refinement.