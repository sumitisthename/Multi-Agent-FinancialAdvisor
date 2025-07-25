from flask import Flask, request, jsonify
from graph.graph_builder import build_graph
from config.settings import load_config
from utils.logger import setup_logger
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Set up logging and config
config = load_config()
logger = setup_logger()

# Build LangGraph workflow
graph = build_graph(config)

@app.route('/run_graph', methods=['POST'])
def run_graph():
    data = request.json
    assets = data.get('assets')
    user_query = data.get('user_query')

    if not assets:
        return jsonify({"error": "Assets are required"}), 400

    initial_state = {
        "assets": assets,
        "timestamp": datetime.utcnow().isoformat(),
        "memory": None,
        "user_query": user_query or "No question provided"
    }

    result = graph.invoke(initial_state)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
