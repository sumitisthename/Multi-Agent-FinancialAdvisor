import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [assets, setAssets] = useState('AAPL,TSLA,NVDA');
  const [userQuery, setUserQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post('/api/run_graph', {
        assets: assets.split(',').map(a => a.trim()),
        user_query: user_query,
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error running graph:', error);
      setResult({ error: 'Failed to run graph. See console for details.' });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Multi-Agent Financial Planner</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="assets">Assets (comma-separated)</label>
            <input
              type="text"
              id="assets"
              value={assets}
              onChange={(e) => setAssets(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="userQuery">Question</label>
            <textarea
              id="userQuery"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              placeholder="e.g., Should I invest in TSLA next week?"
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Running...' : 'Run Analysis'}
          </button>
        </form>
        {result && (
          <div className="result">
            <h2>Analysis Result</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
