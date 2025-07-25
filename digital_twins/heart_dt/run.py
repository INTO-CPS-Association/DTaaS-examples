#!/usr/bin/env python3
"""
This file provides backward compatibility with the original structure.
It simply imports and runs the main function from app.py.
"""
import os
import sys

# Add project root directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # digital_twins
project_root = os.path.dirname(parent_dir)  # pranjay directory
if project_root not in sys.path:
    sys.path.append(project_root)

# Initialize the data directory
print("Initializing data directory...")
from data.heart_dt.initialize import ensure_data_directory
data_dir = ensure_data_directory()
print(f"Data directory initialized: {data_dir}")

from digital_twins.heart_dt.app import main

if __name__ == "__main__":
    main()
