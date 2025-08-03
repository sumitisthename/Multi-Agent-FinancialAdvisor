from setuptools import setup, find_packages

setup(
    name="financial_advisor",
    version="0.1.0",
    author="Sumit De",
    description="A multi-agent financial advisor using LangChain, forecasting, and anomaly detection.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Core LangChain & LangGraph components
        "langchain",
        "langgraph",
        "langchain-core",
        "langchain-groq",
        "langchain-community",

        # Frontend
        "streamlit",

        # LLM APIs & Embedding
        "openai",
        "sentence-transformers",
        "faiss-cpu",

        # Data processing
        "pandas",
        "numpy",
        "scikit-learn",

        # Networking & environment
        "requests",
        "python-dotenv",

        # Logging and debugging
        "loguru",

        # Code Carbon for energy usage tracking
        "codecarbon",

        # Time-series forecasting
        "statsmodels",

        # Yahoo Finance
        "yfinance",

        # Visualization
        "matplotlib",
        "ipython",

        # Testing
        "pytest"
    ],
    python_requires=">=3.8",
)
