import streamlit as st
import time
import json
import os
import sys
from fpdf import FPDF
import io

from codecarbon import EmissionsTracker

# Project imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import graph
from graph.graph_builder import build_graph
from config.settings import load_config
from utils.logger import setup_logger

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
    export_format = st.radio("Export Result As", ["None", "JSON", "TXT", "PDF"], index=0)
    if st.button("Run Multi-Agent Graph"):
        st.session_state['run'] = True

# Set up logging and config
config = load_config()
logger = setup_logger()

# Function to simulate step-by-step graph execution
def run_graph_with_streaming(initial_state):
    st.subheader("🧠 Agentic System Execution Log")

    goal = initial_state.get("user_query", "No specific question provided")
    assets_list = initial_state.get("assets", [])

    # Step 1: Define the Goal
    st.markdown("### 🎯 Goal Definition")
    st.markdown(f"- **User Query:** `{goal}`")
    st.markdown(f"- **Assets to Analyze:** `{', '.join(assets_list)}`")
    st.markdown("- **Date of Analysis:** `{}`".format(initial_state.get("timestamp")))

    # Step 2: Planning
    st.markdown("---")
    st.markdown("### 🧭 Planning Phase")
    planning_steps = [
        "Identify relevant agents for financial analysis.",
        "Determine dependencies between agents (e.g., forecast needs market summary).",
        "Set execution order: Economic ➝ Market ➝ Forecast ➝ Risk ➝ Compliance ➝ Final Decision ➝ Reflection."
    ]
    for step in planning_steps:
        st.markdown(f"- {step}")
    st.markdown("✅ Planning complete.\n")

    # Step 3: Execute Graph
    st.markdown("---")
    st.markdown("### ⚙️ Execution Phase")
    graph = build_graph(config)

    if graph is None:
        st.error("❌ Failed to build graph. Check logs for details.")
        return
    
    if os.path.exists("emissions.csv") and os.path.getsize("emissions.csv") == 0:
        os.remove("emissions.csv")
    tracker = EmissionsTracker(project_name="financial_multi_agent_system", output_file="emissions.csv")
    tracker.start()

    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    execution_steps = [
        "Running Economic Indicators Agent...",
        "Running Market Summary Agent...",
        "Running Forecast Agent...",
        "Running Risk Report Agent...",
        "Running Compliance Review Agent...",
        "Running Final Decision Agent...",
        "Running Reflection Agent..."
    ]

    result = None
    for i, step in enumerate(execution_steps):
        status_placeholder.info(f"🔄 {step}")
        time.sleep(1.2)  # simulate time delay
        progress_bar.progress((i + 1) / len(execution_steps))

    result = graph.invoke(initial_state)
    emissions = tracker.stop()
    progress_bar.empty()
    status_placeholder.success("✅ All agents executed successfully.")

    # Step 4: Display Agent Outputs
    st.markdown("---")
    st.markdown("### 🗂️ Agent Outputs")
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
    st.markdown("---")

    # Emissions
    st.markdown("---")
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
        class FinancialReportPDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Executive Financial Report", ln=True, align="C")
                self.set_font("Arial", "", 10)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, f"Generated on: {timestamp}", ln=True, align="C")
                self.ln(5)
                self.set_text_color(0, 0, 0)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f"LangGraph Financial System | Page {self.page_no()}", align="C")

        pdf = FinancialReportPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Executive Summary Section
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, "Executive Summary", ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, f"""
    This executive report provides a comprehensive multi-agent analysis of selected financial assets. 
    The insights include economic indicators, market summaries, forecasts, risk assessments, compliance evaluations, and final investment decisions.

    **Assets Analyzed:** {assets}
    **Date of Analysis:** {timestamp}
        """)
        pdf.ln(5)

        # Detailed Agent Outputs
        for key, val in agent_outputs.items():
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(210, 210, 210)
            pdf.cell(0, 10, f"{key}", ln=True, fill=True)
            pdf.ln(1)
            pdf.set_font("Arial", "", 11)
            for line in str(val).split('\n'):
                pdf.multi_cell(0, 8, f"  {line}")
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

        # Output as downloadable PDF
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="📥 Download Executive Report (PDF)",
            data=pdf_bytes,
            file_name="executive_financial_report.pdf",
            mime="application/pdf"
        )
        return result

# Question-based interactive input
st.markdown("---")
st.subheader("💬 Ask a Question to the Financial System")
user_query = st.text_area("Enter your question (e.g., Should I invest in TSLA next week?)")

if st.button("Analyze My Query"):
    st.subheader("🧠 Multi-Agent Analysis In Progress")

    steps = [
        ("📥 Understanding your question...", "Parsing context and identifying financial assets."),
        ("📊 Fetching stock data...", "Retrieving historical and real-time market prices."),
        ("📈 Forecasting trends...", "Applying ML models to project market behavior."),
        ("⚠️ Running risk analysis...", "Identifying volatility and uncertainty."),
        ("🧾 Evaluating compliance...", "Verifying adherence to financial regulations."),
        ("🧠 Synthesizing final decision...", "Generating investment recommendation."),
    ]

    status_container = st.empty()
    progress_bar = st.progress(0)
    total_steps = len(steps)

    for i, (title, description) in enumerate(steps):
        with status_container.container():
            st.markdown(f"**Step {i+1}/{total_steps}: {title}**")
            st.markdown(f"`{description}`")
        progress_bar.progress((i + 1) / total_steps)
        time.sleep(1.5)
        status_container.empty()

    progress_bar.empty()
    st.success("✅ Query processing complete.")
    st.markdown("👉 Now click **Run Multi-Agent Graph** in the sidebar to view detailed outputs.")

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
