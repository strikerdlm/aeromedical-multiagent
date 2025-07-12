"""
Main entry point for the application.

This script allows the application to be run directly from the project root,
ensuring that all package imports are resolved correctly.

To run the application:
    python run.py

To pass arguments:
    python run.py --mode=prompt --query="your query"
"""
import sys
import os

# Add the project root to the Python path to allow running from any directory
# and to ensure consistent module resolution.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now that the path is set up, we can import from the `src` package
from src.main import main

if __name__ == "__main__":
    main() 