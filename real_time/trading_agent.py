from real_time.live_state import LiveState
from tools.quant_models import run_forecast_model, detect_anomalies
from tools.rule_parser import extract_compliance_rules
from config.settings import load_config
from datetime import datetime

class TradingAgent:
    """
    A real-time agent that makes trading decisions based on live data.
    """
    def __init__(self, live_state: LiveState):
        self.live_state = live_state
        self.config = load_config()
        self.compliance_rules = extract_compliance_rules(self.config)

    def make_decision(self, asset: str):
        """
        Makes a trading decision for a given asset.

        This method will:
        1. Generate a forecast.
        2. Perform a risk analysis.
        3. Check for compliance.
        4. Return a trading decision (e.g., "BUY", "SELL", "HOLD").
        """
        # 1. Generate a forecast
        # In a real system, we'd use the live market data.
        # For now, we'll call the existing forecast model.
        # Note: This might be too slow for real-time. We'll optimize this later.
        forecast = run_forecast_model([asset], datetime.now().isoformat(), self.config)

        # 2. Perform a risk analysis
        # The `detect_anomalies` function needs transactions and a forecast.
        # We'll need to adapt this for a live environment.
        # For now, we'll pass an empty list of transactions.
        anomalies = detect_anomalies([], str(forecast), self.config)

        # 3. Check for compliance
        # The compliance check is rule-based and should be fast.
        # We'll need to define how the proposed action is generated.
        # For now, let's assume a simple logic based on the forecast.

        # A simple decision logic (to be improved)
        if "Positive" in str(forecast):
            action = "BUY"
        elif "Negative" in str(forecast):
            action = "SELL"
        else:
            action = "HOLD"

        is_compliant = self.check_compliance(action, anomalies)

        if is_compliant:
            return action
        else:
            return "HOLD"

    def check_compliance(self, action: str, anomalies: list) -> bool:
        """
        Checks if a proposed action is compliant with the rules.
        """
        # This is a simplified compliance check.
        # A real system would have a more sophisticated rule engine.
        if "Volatility" in str(anomalies) and action != "HOLD":
            return False

        # Example rule: No selling of "AAPL"
        if action == "SELL" and "AAPL" in self.compliance_rules:
            return False

        return True

if __name__ == '__main__':
    # Example usage
    live_state = LiveState()
    # You would typically have a running loop that updates the live_state

    trading_agent = TradingAgent(live_state)
    decision = trading_agent.make_decision("AAPL")
    print(f"Trading decision for AAPL: {decision}")
