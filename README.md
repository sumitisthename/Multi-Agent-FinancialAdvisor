# LangGraph Multi-Agent Financial System

This project is a multi-agent financial system that uses LangGraph to analyze market data, forecast asset prices, identify risks, ensure compliance, and make investment decisions. The system is designed to be a proof-of-concept for applying autonomous agents to complex financial tasks.

## Features

- **Multi-Agent Architecture:** The system uses a team of specialized AI agents to handle different aspects of the financial analysis process, including:
    - **Econimic Indicator Agent:** Capture inidcators like GDP, Inflation and Unemployment rate
    - **Market Analysis Agent:** Provides summaries of market conditions for specified assets.
    - **Forecasting Agent:** Predicts future asset prices using time-series models.
    - **Risk Analysis Agent:** Identifies potential risks associated with investments.
    - **Compliance Agent:** Ensures that investment strategies adhere to predefined rules.
    - **Coordinator Agent:** Oversees the entire process and makes a final decision.
- **Interactive UI:** A Streamlit application provides an interactive interface for running the system, viewing results, and asking questions.
- **Extensible:** The graph-based architecture, powered by LangGraph, makes it easy to add new agents or modify the existing workflow.
- **Carbon Tracking:** The system tracks and reports its own carbon emissions using the `codecarbon` library.
- **Data-Driven:** The system uses real-world financial data from Yahoo Finance.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API keys:**
   - Create a `.env` file in the root directory of the project.
   - Add your API keys to the `.env` file. At a minimum, you will need a `GROQ_API_KEY`.
   ```
   GROQ_API_KEY="your-groq-api-key"
   # Add other API Keys:
   NEW_API_KEY = "your-new-api-key"
   ALPHA = "your-apha-vantage-api-key"
   ```

## Usage

### Command-Line Interface

To run a single test cycle of the system, you can use the `main.py` script:

```bash
python main.py
```

This will run the system with a default set of assets and print the final decision and reflection to the console.

### Streamlit Application

For a more interactive experience, you can run the Streamlit application:

```bash
streamlit run streamlit_app/app.py
```

This will launch a web application in your browser where you can:

-   Enter the assets you want to analyze.
-   Specify the date for the analysis.
-   Run the multi-agent system.
-   View the detailed outputs from each agent.
-   Ask questions in natural language.
-   Download the results as a JSON or TXT file.

## Project Structure

```
.
├── agents/             # Contains the code for each agent
├── config/             # Configuration files
├── forecasts/          # Stores the generated forecasts
├── graph/              # Defines the LangGraph workflow
├── logs/               # Log files
├── memory/             # Stores the system's memory
├── prompts/            # Prompts for the LLMs
├── streamlit_app/      # The Streamlit UI
├── tests/              # Unit and integration tests
├── tools/              # Tools used by the agents
├── utils/              # Utility functions
├── main.py             # Main script for the CLI
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Dependencies

The main dependencies for this project are:

-   `langchain` and `langgraph` for the agentic workflow.
-   `streamlit` for the user interface.
-   `pandas`, `numpy`, and `scikit-learn` for data processing.
-   `yfinance` for fetching financial data.
-   `groq` for the language model API.
-   `codecarbon` for tracking CO2 emissions.

For a full list of dependencies, please see the `requirements.txt` file.
