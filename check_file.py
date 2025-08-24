# Script to check the actual contents of quant_models.py

import os

file_path = "tools/quant_models.py"

if os.path.exists(file_path):
    print(f"Reading {file_path}...")
    print("=" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(content)
    print("=" * 50)
    
    # Check for function definitions
    lines = content.split('\n')
    functions = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('def '):
            functions.append(f"Line {i}: {line.strip()}")
    
    print(f"\nFound {len(functions)} function definitions:")
    for func in functions:
        print(f"  {func}")
        
    # Specifically check for run_forecast_model
    if 'def run_forecast_model' in content:
        print("\n✅ 'run_forecast_model' is defined in the file")
    else:
        print("\n❌ 'run_forecast_model' is NOT defined in the file")
        
    # Check file size
    file_size = len(content)
    print(f"\nFile size: {file_size} characters")
    
else:
    print(f"❌ File {file_path} does not exist")