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

## Backtesting and Performance

To evaluate the performance and environmental impact of the forecasting models, a backtesting script is included. This script runs multiple models over a historical period and compares their forecasts, performance metrics, and carbon emissions.

### Running the Backtest

To run the backtest, execute the following command from the root directory:

```bash
python backtest.py
```

The script will test the defined forecast models (default: ARIMA and a simple Moving Average) for the assets defined in the script (default: SPY, AAPL) over the last 30 days.

### Backtest Output

The script will generate a `results/` directory containing the following files:

-   `backtest_raw_data_{model_name}.csv`: A CSV file for each model tested, containing the detailed day-by-day results of the backtest. It includes the forecasted price and the actual price for each day.
-   `performance_summary.json`: A single JSON file containing a comparative summary of all tested models. For each model, it provides:
    -   **performance_metrics**: A breakdown of KPIs for each asset, including:
        -   **RMSE (Root Mean Squared Error):** Measures the absolute error of the forecast.
        -   **MAPE (Mean Absolute Percentage Error):** Measures the percentage error of the forecast.
        -   **Directional_Accuracy:** The percentage of time the model correctly predicted whether the price would go up or down.
        -   **Total_Return_pct:** The total return of a simple trading strategy based on the forecasts.
        -   **Sharpe_Ratio:** The risk-adjusted return of the simulated strategy.
    -   **aggregated_emissions_kg**: The total aggregated carbon emissions (in kg of CO₂eq) for the entire backtesting run of that model. This allows for a direct comparison of the performance-vs-emissions trade-off.

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
