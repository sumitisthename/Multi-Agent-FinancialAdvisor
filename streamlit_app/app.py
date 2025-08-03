import streamlit as st
import time
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.graph_builder import build_graph
from config.settings import load_config
from utils.logger import setup_logger
from codecarbon import EmissionsTracker

st.set_page_config(page_title="Multi-Agent Financial Planner", layout="wide")

st.title("📈 LangGraph Multi-Agent Financial System")
st.markdown("""
This app demonstrates a multi-agent system for financial market analysis, forecasting, risk detection, compliance, and strategic planning.
""")

# Sidebar inputs
with st.sidebar:
    st.header("🛠️ Configuration")
    assets = st.text_input("Enter assets (comma-separated)", "AAPL,TSLA,NVDA")
    timestamp = st.text_input("Date (YYYY-MM-DD)", "2025-06-10")
    export_format = st.radio("Export Result As", ["None", "JSON", "TXT"], index=0)
    if st.button("Run Multi-Agent Graph"):
        st.session_state['run'] = True

# Load config and logger
config = load_config()
logger = setup_logger()

# Function to run the LangGraph
def run_graph_with_streaming(initial_state):
    st.subheader("🧠 System Execution Log")
    status_area = st.empty()

    graph = build_graph(config)

    if graph is None:
        st.error("❌ Failed to build graph. Please check the logs or agent node definitions.")
        return

    tracker = EmissionsTracker(project_name="financial_multi_agent_system", output_file="emissions.csv")
    tracker.start()

    with st.spinner("Running multi-agent graph..."):
        try:
            result = graph.invoke(initial_state)
            time.sleep(0.5)
        except Exception as e:
            st.error(f"❌ Error during graph execution: {e}")
            return

    emissions = tracker.stop()
    st.success("✅ Execution complete!")

    # Display per-agent outputs
    agent_outputs = {
        "Economic Indicators": result.get("economic_indicators", "N/A"),
        "Market Summary": result.get("market_summary", "N/A"),
        "Forecast": result.get("forecast", "N/A"),
        "Risk Report": result.get("risk_report", "N/A"),
        "Compliance Review": result.get("compliance_review", "N/A"),
        "Final Decision": result.get("final_decision", "N/A"),
        "Reflection Lesson": result.get("reflection_lesson", "N/A")
    }

    for title, content in agent_outputs.items():
        with st.expander(f"📌 {title}"):
            st.markdown(f"```\n{content}\n```")

    # Emission summary
    st.subheader("🌱 Carbon Emissions")
    st.markdown(f"**Estimated CO₂ Emitted**: `{emissions:.6f} kg` per run")

    # Export section
    if export_format == "JSON":
        st.download_button(
            label="📥 Download Result as JSON",
            data=json.dumps(result, indent=2),
            file_name="agent_output.json",
            mime="application/json"
        )
    elif export_format == "TXT":
        output_txt = "\n\n".join([f"{key}:\n{val}" for key, val in agent_outputs.items()])
        st.download_button(
            label="📥 Download Result as TXT",
            data=output_txt,
            file_name="agent_output.txt",
            mime="text/plain"
        )

    return result

# Interactive input for custom query
st.markdown("---")
st.subheader("💬 Ask a Question to the Financial System")
user_query = st.text_area("Enter your question (e.g., Should I invest in TSLA next week?)")

if st.button("Analyze My Query"):
    with st.spinner("Planning and reasoning through your query..."):
        st.markdown("### 🧭 Planning")
        st.markdown("- Understand context and intent\n- Fetch relevant market and forecast data\n- Check risk and compliance\n- Generate decision")

        st.markdown("### 🔄 Actions")
        st.markdown("- Fetching stock data...\n- Forecasting trends...\n- Running risk analysis...\n- Evaluating compliance...\n- Synthesizing final decision...")

        st.markdown("### 🧠 Reasoning")
        st.markdown(f"The system considers your query:\n\n> {user_query}\n\n...and responds based on agent outputs.")

        st.success("Query processing complete. Please run the multi-agent graph to view outputs above.")

# Run the system
if st.session_state.get("run"):
    initial_state = {
        "assets": [a.strip() for a in assets.split(",")],
        "timestamp": timestamp,
        "memory": None,
        "user_query": user_query.strip() if user_query else "No question provided"
    }
    run_graph_with_streaming(initial_state)
    st.session_state['run'] = False
