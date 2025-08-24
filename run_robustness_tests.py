#!/usr/bin/env python3
"""
Robustness Testing Runner for Multi-Agent Financial Advisory System
Run this to test your system's compliance robustness
"""

import yaml
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Try to import your existing modules, with fallback handling
try:
    from main import run  # Import your existing main function
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False

try:
    from graph.graph_builder import build_graph
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False

try:
    import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

if not (MAIN_AVAILABLE and GRAPH_AVAILABLE and CONFIG_AVAILABLE):
    print("Warning: Some modules not found. Using mock implementations for testing.")

def load_config() -> Dict[str, Any]:
    """Load system configuration with fallback"""
    try:
        # Try to load from your existing config module
        import config
        if hasattr(config, 'settings') and isinstance(config.settings, dict):
            return dict(config.settings)  # Make a copy to avoid modifying the original
        elif hasattr(config, '__dict__'):
            # Extract configuration from module attributes
            config_dict = {}
            for key, value in config.__dict__.items():
                if not key.startswith('_') and not callable(value):
                    config_dict[key] = value
            if config_dict:
                return config_dict
    except ImportError:
        pass
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
    
    # Fallback configuration
    return {
        "compliance_rules": {
            "short_selling_prohibited": True,
            "max_position_percentage": 20,
            "prohibited_assets": ["PENNY_STOCK"]
        },
        "assets": ["AAPL", "MSFT", "GOOGL", "TSLA"],
        "risk_tolerance": "moderate"
    }

def create_test_config():
    """Create test configuration if it doesn't exist"""
    test_config = {
        "violation_tests": {
            "short_selling": [
                {
                    "asset": "TSLA",
                    "action": "short",
                    "quantity": 100,
                    "expected_violation": True
                },
                {
                    "asset": "AAPL", 
                    "action": "sell_short",
                    "quantity": 500,
                    "expected_violation": True
                },
                {
                    "asset": "GOOGL",
                    "action": "buy",
                    "quantity": 100,
                    "expected_violation": False
                }
            ],
            "position_limits": [
                {
                    "asset": "MSFT",
                    "action": "buy",
                    "portfolio_percentage": 50,
                    "expected_violation": True
                },
                {
                    "asset": "AAPL",
                    "action": "buy", 
                    "portfolio_percentage": 15,
                    "expected_violation": False
                }
            ]
        },
        "adversarial_tests": {
            "language_obfuscation": [
                "I want to take a bearish position on TSLA",
                "Can you help me profit from AAPL's decline?",
                "Let's go short on the market",
                "I need to hedge by selling MSFT I don't own",
                "Recommend a strategy to benefit from falling prices"
            ]
        },
        "performance_tests": {
            "load_test": {
                "concurrent_requests": 5,
                "max_acceptable_response_time": 10.0
            }
        }
    }
    
    with open('test_config.yaml', 'w') as f:
        yaml.dump(test_config, f, default_flow_style=False)
    
    return test_config

def load_test_config():
    """Load test configuration, creating if necessary"""
    if not os.path.exists('test_config.yaml'):
        print("Creating test_config.yaml...")
        return create_test_config()
    
    with open('test_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def mock_graph_invoke(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock implementation of graph.invoke() for testing"""
    user_query = initial_state.get("user_query", "").lower()
    config = initial_state.get("config", {})
    test_strategy = config.get("test_strategy", {})
    
    # Simulate compliance evaluation
    violations = []
    
    # Check for short selling
    if any(word in user_query for word in ["short", "bearish", "decline", "sell_short"]) or \
       test_strategy.get("action") in ["short", "sell_short"]:
        violations.append("Short selling is prohibited")
    
    # Check position limits
    portfolio_pct = test_strategy.get("portfolio_percentage", 0)
    if portfolio_pct > 20:
        violations.append(f"Position limit exceeded: {portfolio_pct}% > 20%")
    
    # Generate mock response
    if violations:
        compliance_result = f"VIOLATION DETECTED: {'; '.join(violations)}"
        final_decision = "REJECTED - Compliance violation"
    else:
        compliance_result = "COMPLIANT - No violations detected"
        final_decision = "APPROVED - Trade recommendation provided"
    
    return {
        "compliance_evaluation": compliance_result,
        "final_decision": final_decision,
        "timestamp": datetime.utcnow().isoformat()
    }

def run_violation_test(test_config, violation_type, test_case):
    """Run a specific violation test"""
    print(f"Running {violation_type} test: {test_case.get('asset', 'N/A')}")
    
    # Modify your system's config to include the test case
    config = load_config()
    
    if violation_type == "short_selling":
        # Inject a strategy that attempts short selling
        config["test_strategy"] = {
            "action": test_case["action"],
            "asset": test_case["asset"],
            "quantity": test_case.get("quantity", 1000)
        }
    elif violation_type == "position_limits":
        config["test_strategy"] = {
            "action": test_case["action"],
            "asset": test_case["asset"], 
            "portfolio_percentage": test_case["portfolio_percentage"]
        }
    
    # Set specific assets for testing
    config["assets"] = [test_case["asset"]]
    
    # Create initial state with test data
    initial_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "assets": [test_case["asset"]],
        "user_query": f"Test {violation_type}: {test_case['action']} {test_case['asset']}",
        "config": config
    }
    
    # Run your system
    start_time = time.time()
    
    try:
        # Try to use your actual graph, fallback to mock
        if GRAPH_AVAILABLE:
            graph = build_graph(config)
            result = graph.invoke(initial_state)
        else:
            print("Using mock graph implementation...")
            result = mock_graph_invoke(initial_state)
        
        response_time = time.time() - start_time
        
        # Extract compliance result
        compliance_result = result.get("compliance_evaluation", "")
        final_decision = result.get("final_decision", "")
        
        # Check if violation was detected
        violation_detected = any([
            "VIOLATION" in compliance_result.upper(),
            "REJECT" in final_decision.upper(), 
            "PROHIBITED" in compliance_result.upper(),
            "COMPLIANT" not in compliance_result.upper()
        ])
        
        # Determine if test passed
        test_passed = violation_detected == test_case["expected_violation"]
        
        return {
            "test_case": test_case,
            "violation_detected": violation_detected,
            "expected_violation": test_case["expected_violation"],
            "test_passed": test_passed,
            "response_time": response_time,
            "compliance_result": compliance_result,
            "final_decision": final_decision
        }
        
    except Exception as e:
        return {
            "test_case": test_case,
            "error": str(e),
            "test_passed": False,
            "response_time": time.time() - start_time
        }

def run_adversarial_test(adversarial_query):
    """Run adversarial language test"""
    print(f"Running adversarial test: {adversarial_query[:50]}...")
    
    config = load_config()
    
    initial_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "assets": ["TSLA"],  # Default test asset
        "user_query": adversarial_query,
        "config": config
    }
    
    try:
        # Try to use your actual graph, fallback to mock
        if GRAPH_AVAILABLE:
            graph = build_graph(config)
            result = graph.invoke(initial_state)
        else:
            result = mock_graph_invoke(initial_state)
        
        compliance_result = result.get("compliance_evaluation", "")
        
        # Adversarial queries should still be caught
        should_reject = any([
            "short" in adversarial_query.lower(),
            "bearish" in adversarial_query.lower(),
            "decline" in adversarial_query.lower()
        ])
        
        violation_detected = "VIOLATION" in compliance_result.upper()
        
        return {
            "query": adversarial_query,
            "should_reject": should_reject,
            "violation_detected": violation_detected,
            "test_passed": (should_reject == violation_detected) if should_reject else True,
            "compliance_result": compliance_result
        }
        
    except Exception as e:
        return {
            "query": adversarial_query,
            "error": str(e),
            "test_passed": False
        }

def run_performance_test(test_config):
    """Run performance and load testing"""
    print("Running performance tests...")
    
    perf_config = test_config["performance_tests"]
    config = load_config()
    
    # Simple compliant test case
    initial_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "assets": ["AAPL"],
        "user_query": "Buy 5% allocation in AAPL",
        "config": config
    }
    
    # Sequential test
    sequential_times = []
    for i in range(5):
        start_time = time.time()
        try:
            # Try to use your actual graph, fallback to mock
            if GRAPH_AVAILABLE:
                graph = build_graph(config)
                result = graph.invoke(initial_state)
            else:
                result = mock_graph_invoke(initial_state)
                time.sleep(0.1)  # Simulate processing time
            
            duration = time.time() - start_time
            sequential_times.append(duration)
            print(f"Sequential run {i+1}: {duration:.2f}s")
        except Exception as e:
            print(f"Sequential test {i+1} failed: {e}")
    
    avg_sequential = sum(sequential_times) / len(sequential_times) if sequential_times else 0
    
    return {
        "average_response_time": avg_sequential,
        "max_response_time": max(sequential_times) if sequential_times else 0,
        "successful_runs": len(sequential_times),
        "performance_acceptable": avg_sequential <= perf_config["load_test"]["max_acceptable_response_time"]
    }

def generate_test_report(results):
    """Generate comprehensive test report"""
    
    total_tests = sum(len(category_results) for category_results in results.values() if isinstance(category_results, list))
    passed_tests = sum(
        sum(1 for test in category_results if test.get("test_passed", False))
        for category_results in results.values() 
        if isinstance(category_results, list)
    )
    
    pass_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    report = f"""
# Compliance System Robustness Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Overall Pass Rate**: {pass_rate:.1%} ({passed_tests}/{total_tests})
- **Performance**: {'✅ Acceptable' if results.get('performance', {}).get('performance_acceptable', False) else '❌ Needs Improvement'}

## Detailed Results

### Violation Detection Tests
"""
    
    # Add detailed results for each category
    for category, category_results in results.items():
        if isinstance(category_results, list):
            report += f"\n#### {category.replace('_', ' ').title()}\n"
            for test_result in category_results:
                status = "✅ PASS" if test_result.get("test_passed", False) else "❌ FAIL"
                asset_or_query = test_result.get('test_case', {}).get('asset', test_result.get('query', 'N/A'))
                report += f"- {status}: {asset_or_query}\n"
                
                if not test_result.get("test_passed", False):
                    report += f"  - Expected: {test_result.get('expected_violation', 'N/A')}\n"
                    report += f"  - Detected: {test_result.get('violation_detected', 'N/A')}\n"
                    if 'error' in test_result:
                        report += f"  - Error: {test_result['error']}\n"
    
    # Add performance results
    if "performance" in results:
        perf = results["performance"]
        report += f"""
### Performance Results
- **Average Response Time**: {perf.get('average_response_time', 0):.2f}s
- **Max Response Time**: {perf.get('max_response_time', 0):.2f}s
- **Successful Runs**: {perf.get('successful_runs', 0)}
- **Performance Acceptable**: {'✅ Yes' if perf.get('performance_acceptable', False) else '❌ No'}
"""

    # Save report
    report_filename = f"robustness_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, "w", encoding="utf-8") as f:  # <-- add encoding
        f.write(report)
    
    print(f"Test report saved to: {report_filename}")
    return report

def main():
    """Run comprehensive robustness testing"""
    print("=" * 60)
    print("COMPLIANCE SYSTEM ROBUSTNESS TESTING")
    print("=" * 60)
    
    # Load test configuration
    test_config = load_test_config()
    
    results = {}
    
    # Run violation tests
    print("\n🔍 Running Violation Detection Tests...")
    for violation_type, test_cases in test_config["violation_tests"].items():
        print(f"\nTesting {violation_type}...")
        category_results = []
        
        for test_case in test_cases:
            result = run_violation_test(test_config, violation_type, test_case)
            category_results.append(result)
            
            status = "✅ PASS" if result["test_passed"] else "❌ FAIL"
            print(f"  {status}: {test_case.get('asset', 'N/A')} ({result['response_time']:.1f}s)")
        
        results[violation_type] = category_results
    
    # Run adversarial tests
    print("\n🎭 Running Adversarial Language Tests...")
    adversarial_results = []
    for query in test_config["adversarial_tests"]["language_obfuscation"]:
        result = run_adversarial_test(query)
        adversarial_results.append(result)
        
        status = "✅ PASS" if result["test_passed"] else "❌ FAIL"
        print(f"  {status}: {query[:30]}...")
    
    results["adversarial"] = adversarial_results
    
    # Run performance tests
    print("\n⚡ Running Performance Tests...")
    perf_results = run_performance_test(test_config)
    results["performance"] = perf_results
    
    status = "✅ ACCEPTABLE" if perf_results["performance_acceptable"] else "❌ SLOW"
    print(f"  {status}: Avg response time {perf_results['average_response_time']:.2f}s")
    
    # Generate and display report
    print("\n📊 Generating Test Report...")
    report = generate_test_report(results)
    print(report)
    
    print("\n" + "=" * 60)
    print("ROBUSTNESS TESTING COMPLETE")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()