import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

def evaluate_arima_model(asset, start_date, end_date):
    """
    Evaluates the performance of an ARIMA model for a given asset.
    """
    # Gather historical data
    df = yf.download(asset, start=start_date, end=end_date, progress=False)

    # Split the data
    train_data, test_data = train_test_split(df['Close'], test_size=0.2, shuffle=False)

    # Train the model
    model = ARIMA(train_data, order=(5, 1, 0))
    fitted_model = model.fit()

    # Make predictions
    predictions = fitted_model.forecast(steps=len(test_data))

    # Evaluate performance
    mae = mean_absolute_error(test_data, predictions)
    mse = mean_squared_error(test_data, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(test_data, predictions)

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": r2
    }

def evaluate_isolation_forest_model():
    """
    Evaluates the performance of an Isolation Forest model.
    """
    # Generate simulated data
    np.random.seed(42)
    X = 0.3 * np.random.randn(100, 2)
    X = np.r_[X + 2, X - 2]
    X = pd.DataFrame(X, columns=['feature1', 'feature2'])

    # Add some anomalies
    X = pd.concat([X, pd.DataFrame(np.random.uniform(low=-6, high=6, size=(10, 2)), columns=['feature1', 'feature2'])])

    # Create labels
    y = np.ones(len(X))
    y[-10:] = -1

    # Train the model
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)

    # Make predictions
    y_pred = model.predict(X)

    # Evaluate performance
    precision = precision_score(y, y_pred, pos_label=-1)
    recall = recall_score(y, y_pred, pos_label=-1)
    f1 = f1_score(y, y_pred, pos_label=-1)
    cm = confusion_matrix(y, y_pred)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm
    }

if __name__ == '__main__':
    # Evaluate ARIMA model
    asset = "AAPL"
    start_date = "2020-01-01"
    end_date = "2023-01-01"
    arima_metrics = evaluate_arima_model(asset, start_date, end_date)
    print(f"ARIMA Metrics for {asset}:")
    for metric, value in arima_metrics.items():
        print(f"  {metric}: {value}")

    # Evaluate Isolation Forest model
    isolation_forest_metrics = evaluate_isolation_forest_model()
    print("\nIsolation Forest Metrics:")
    for metric, value in isolation_forest_metrics.items():
        if metric == "confusion_matrix":
            print(f"  {metric}:\n{value}")
        else:
            print(f"  {metric}: {value}")
