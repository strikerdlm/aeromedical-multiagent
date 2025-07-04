#!/usr/bin/env python3
"""
Entry point for the Multi-Agent Prompt Enhancement Application.

Run this script to start the text-based prompt enhancement system.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.main import main
    main() 