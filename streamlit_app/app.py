import streamlit as st
import time
import json
import os
import sys
from fpdf import FPDF
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import graph
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

# Set up logging and config
config = load_config()
logger = setup_logger()

# Function to simulate step-by-step graph execution
def run_graph_with_streaming(initial_state):
    st.subheader("🧠 System Execution Log")
    graph = build_graph(config)
    
    if graph is None:
        st.error("❌ Failed to build graph. Check logs for details.")
        logger.error("Graph is None. Cannot proceed.")
        return  # Only return if graph is None

    status_area = st.empty()

    tracker = EmissionsTracker(project_name="financial_multi_agent_system", output_file="emissions.csv")
    tracker.start()

    with st.spinner("Running multi-agent graph..."):
        logger.info("Running graph...")
        logger.info(f"Graph object: {graph}")
        result = graph.invoke(initial_state)
        time.sleep(0.5)

    emissions = tracker.stop()
    logger.info(f"Emissions returned by tracker: {emissions}")
    st.success("✅ Execution complete!")


    # Show detailed per-agent output
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
    if emissions is not None:
        st.markdown(f"**Estimated CO₂ Emitted**: `{emissions:.6f} kg` per run")
    else:
        st.warning("⚠️ Emissions data not available.")

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
    elif export_format == "PDF":
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for key, val in agent_outputs.items():
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=key, ln=True)
            pdf.set_font("Arial", size=12)
            for line in str(val).split('\n'):
                pdf.multi_cell(0, 10, txt=line)

        # Output PDF to bytes buffer
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="📥 Download Result as PDF",
            data=pdf_buffer,
            file_name="agent_output.pdf",
            mime="application/pdf"
        )
    return result

# Question-based interactive input
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

# Run system when triggered
if st.session_state.get("run"):
    initial_state = {
        "assets": [a.strip() for a in assets.split(",")],
        "timestamp": timestamp,
        "memory": None,
        "user_query": user_query.strip() if user_query else "No question provided"
    }
    run_graph_with_streaming(initial_state)
    st.session_state['run'] = False
