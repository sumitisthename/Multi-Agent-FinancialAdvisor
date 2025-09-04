import streamlit as st
import time
import json
import os
import sys
from fpdf import FPDF
import io
import pandas as pd
import plotly.express as px

from codecarbon import EmissionsTracker

# Project imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import graph
from graph.graph_builder import build_graph
from graph.generate_graph import generate_forecast_plotly
from config.settings import load_config
from utils.logger import setup_logger

# --- Page Configuration ---
st.set_page_config(
    page_title="Multi-Agent Financial System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .reportview-container {
        background: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("📈 Multi-Agent Financial System")
st.markdown("""
Welcome to the future of financial analysis. This application leverages a sophisticated multi-agent system to deliver comprehensive market insights, forecasts, and strategic recommendations.
""")

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ Configuration")
    st.markdown("Provide the necessary inputs to start the financial analysis.")

    assets = st.text_input(
        "Assets (comma-separated)",
        "AAPL,TSLA,NVDA",
        help="Enter the stock tickers for the assets you want to analyze."
    )
    timestamp = st.text_input(
        "Date (YYYY-MM-DD)",
        "2025-06-10",
        help="The date for which you want to perform the analysis."
    )
    user_query = st.text_area(
        "Your Question",
        "Should I invest in TSLA next week?",
        help="Ask a specific question to the financial system."
    )

    st.header("⚙️ Execution")
    if st.button("🚀 Run Analysis"):
        st.session_state['run'] = True

    st.header("📄 Export")
    export_format = st.radio(
        "Export Format",
        ["None", "JSON", "TXT", "PDF"],
        index=0,
        help="Select the format to export the results."
    )

# --- Main Application ---
config = load_config()
logger = setup_logger()

def run_graph_with_streaming(initial_state):
    st.header("📊 Financial Analysis Results")

    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Agent Outputs", "Forecasts", "Analysis"])

    progress_bar = st.progress(0)
    status_text = st.empty()

    graph = build_graph(config)
    if graph is None:
        st.error("❌ Failed to build graph. Check logs for details.")
        return

    if os.path.exists("emissions.csv") and os.path.getsize("emissions.csv") == 0:
        os.remove("emissions.csv")
    tracker = EmissionsTracker(project_name="financial_multi_agent_system", output_file="emissions.csv")
    tracker.start()

    result = None
    total_steps = len(graph.nodes)
    for i, step in enumerate(graph.stream(initial_state)):
        node_name = list(step.keys())[0]
        status_text.text(f"Running {node_name}...")
        progress_bar.progress((i + 1) / total_steps)
        result = list(step.values())[0]

    emissions = tracker.stop()
    status_text.text("✅ Analysis Complete!")
    progress_bar.empty()

    with tab1:
        st.subheader("Executive Summary")
        st.markdown(f"**Final Recommendation:** {result.get('final_decision', 'N/A')}")

        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Level", result.get("risk_report", "N/A").split('\n')[0])
        col2.metric("Compliance Status", "Compliant" if "No issues" in result.get("compliance_review", "") else "Non-Compliant")
        col3.metric("Carbon Emissions (kg)", f"{emissions:.6f}" if emissions else "N/A")

        st.subheader("Key Insights")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
        <p><strong>Economic Outlook:</strong> {result.get('economic_indicators', 'N/A')}</p>
        <p><strong>Market Summary:</strong> {result.get('market_summary', 'N/A')}</p>
        <p><strong>Forecast:</strong> {result.get('forecast', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Detailed Agent Outputs")
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
            with st.expander(f"**{title}**"):
                st.markdown(f"```{content}```")

    with tab3:
        st.subheader("Forecast Graphs")
        figures = generate_forecast_plotly(timestamp)
        for asset, fig in figures:
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Model Evaluation")
        if "forecast_records" in result:
            for record in result["forecast_records"]:
                st.write(f"### Evaluation for {record['Asset']}")
                eval_df = pd.DataFrame(record['model_evaluations'])
                st.dataframe(eval_df)

    # --- Export Section ---
    if export_format != "None":
        st.sidebar.markdown("---")
        st.sidebar.header("📥 Download Results")
        if export_format == "JSON":
            st.sidebar.download_button(
                label="Download as JSON",
                data=json.dumps(result, indent=2),
                file_name="financial_analysis.json",
                mime="application/json"
            )
        elif export_format == "TXT":
            output_txt = "\n\n".join([f"{key}:\n{val}" for key, val in agent_outputs.items()])
            st.sidebar.download_button(
                label="Download as TXT",
                data=output_txt,
                file_name="financial_analysis.txt",
                mime="text/plain"
            )
        elif export_format == "PDF":
            # PDF Generation Logic (can be abstracted to a utility function)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(40, 10, "Financial Analysis Report")
            pdf.ln(20)
            for key, val in agent_outputs.items():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(40, 10, key)
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                # Ensure val is a string before attempting to encode
                val_str = str(val)
                pdf.multi_cell(0, 10, val_str.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(10)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.sidebar.download_button(
                label="Download as PDF",
                data=pdf_bytes,
                file_name="financial_analysis.pdf",
                mime="application/pdf"
            )


if st.session_state.get("run"):
    initial_state = {
        "assets": [a.strip() for a in assets.split(",")],
        "timestamp": timestamp,
        "memory": None,
        "user_query": user_query.strip() if user_query else "No question provided"
    }
    run_graph_with_streaming(initial_state)
    st.session_state['run'] = False
