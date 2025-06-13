import os

# Root directory of your project
project_root = os.path.abspath(".")

# Directories where __init__.py should exist
target_dirs = [
    "agents",
    "tools",
    "memory",
    "graph",
    "config",
    "utils",
    "streamlit_app",
]

# Optionally add root-level __init__.py
open(os.path.join(project_root, "__init__.py"), "a").close()

# Create __init__.py in all target subdirectories
for dir_name in target_dirs:
    full_path = os.path.join(project_root, dir_name)
    if os.path.isdir(full_path):
        init_file = os.path.join(full_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Marks this directory as a Python package\n")
            print(f"✅ Created: {init_file}")
        else:
            print(f"✔️ Already exists: {init_file}")
    else:
        print(f"⚠️ Directory not found: {full_path}")
# Ensure the script is run from the project root
if __name__ == "__main__":
    print("Initialization complete. All necessary __init__.py files created.")