#!/usr/bin/env python3
"""
Entry point for the Multi-Agent Prompt Enhancement Application.

Run this script to start the text-based prompt enhancement system.
"""

import sys
import os

# Add the current directory to the Python path so we can import the src package
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    from src.main import main
    main() 