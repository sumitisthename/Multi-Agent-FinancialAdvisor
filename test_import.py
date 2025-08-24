# Test script to diagnose import issues
# Run this in your project root directory

import sys
import os

print("Python path:")
for path in sys.path:
    print(f"  {path}")

print(f"\nCurrent working directory: {os.getcwd()}")

print("\nTesting imports...")

try:
    import tools
    print("✅ Successfully imported 'tools' package")
    print(f"   tools.__file__ = {tools.__file__}")
except Exception as e:
    print(f"❌ Failed to import 'tools': {e}")

try:
    import tools.quant_models
    print("✅ Successfully imported 'tools.quant_models'")
    print(f"   Available functions: {[name for name in dir(tools.quant_models) if not name.startswith('_')]}")
except Exception as e:
    print(f"❌ Failed to import 'tools.quant_models': {e}")
    import traceback
    traceback.print_exc()

try:
    from tools.quant_models import run_forecast_model
    print("✅ Successfully imported 'run_forecast_model'")
    print(f"   Function type: {type(run_forecast_model)}")
except Exception as e:
    print(f"❌ Failed to import 'run_forecast_model': {e}")
    import traceback
    traceback.print_exc()

# Check if __init__.py exists
init_file = "tools/__init__.py"
if os.path.exists(init_file):
    print(f"✅ {init_file} exists")
    with open(init_file, 'r') as f:
        content = f.read()
        if content.strip():
            print(f"   Content: {content[:100]}...")
        else:
            print("   File is empty (which is fine)")
else:
    print(f"❌ {init_file} does not exist - creating it...")
    try:
        with open(init_file, 'w') as f:
            f.write("# This file makes tools a Python package\n")
        print(f"✅ Created {init_file}")
    except Exception as e:
        print(f"❌ Failed to create {init_file}: {e}")

# Check the quant_models.py file
quant_file = "tools/quant_models.py"
if os.path.exists(quant_file):
    print(f"✅ {quant_file} exists")
    try:
        with open(quant_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for syntax errors by trying to compile
            compile(content, quant_file, 'exec')
            print("✅ File compiles without syntax errors")
            
            # Check if run_forecast_model is defined
            if 'def run_forecast_model' in content:
                print("✅ 'run_forecast_model' function definition found")
            else:
                print("❌ 'run_forecast_model' function definition not found")
                
    except SyntaxError as e:
        print(f"❌ Syntax error in {quant_file}: {e}")
    except Exception as e:
        print(f"❌ Error reading {quant_file}: {e}")
else:
    print(f"❌ {quant_file} does not exist")