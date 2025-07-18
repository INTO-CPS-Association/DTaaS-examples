#!/usr/bin/env python3
"""
Data Initialization Script
Sets up the necessary data folder structure
"""
import os
import sys

def ensure_data_directory():
    """Ensure data directory exists and is properly structured"""
    # Get the current directory (should be the data directory)
    data_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Data directory: {data_dir}")
    
    # Create data folder if it doesn't exist
    if not os.path.exists(data_dir):
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir)
    
    # Create a .gitkeep file to ensure the directory is tracked by git
    gitkeep_path = os.path.join(data_dir, '.gitkeep')
    if not os.path.exists(gitkeep_path):
        with open(gitkeep_path, 'w') as f:
            f.write("# This file ensures the data directory is tracked by git\n")
            f.write("# ECG records will be stored in this directory\n")
    
    # Create a README.md file with information about the data
    readme_path = os.path.join(data_dir, 'README.md')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("# Heart Digital Twin Data\n\n")
            f.write("This directory contains ECG records from the MIT-BIH Arrhythmia Database.\n\n")
            f.write("Records are downloaded automatically when the application is run.\n")
            f.write("Each record consists of a .dat file (binary signal data) and a .hea file (header information).\n\n")
            f.write("For more information about the MIT-BIH Arrhythmia Database, see:\n")
            f.write("https://physionet.org/content/mitdb/\n")
    
    return data_dir

if __name__ == "__main__":
    print("Initializing data directory...")
    data_dir = ensure_data_directory()
    print(f"Data directory initialized: {data_dir}")
    print("Ready to store ECG records.") 