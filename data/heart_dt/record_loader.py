#!/usr/bin/env python3
"""
Record Loader Module for Heart Digital Twin
Handles loading and downloading heart record data
"""
import os
import wfdb
import sys

def download_record(record_name):
    """
    Download the record if it's not already present and store it in data folder
    
    Args:
        record_name (str): The name of the record to download (e.g., '100')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get path to data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = current_dir
        
        # Check if the record already exists in the data directory
        record_path = os.path.join(data_dir, record_name)
        if not os.path.exists(f"{record_path}.dat") or not os.path.exists(f"{record_path}.hea"):
            print(f"Downloading record {record_name} to {data_dir}...")
            wfdb.dl_database('mitdb', record_name, dl_dir=data_dir)
            print(f"Record {record_name} downloaded successfully.")
        
        return True
    except Exception as e:
        print(f"Error downloading record {record_name}: {e}")
        return False

def get_record_path(record_name):
    """
    Get the full path to a record in the data directory
    
    Args:
        record_name (str): The name of the record (e.g., '100')
    
    Returns:
        str: The full path to the record
    """
    data_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(data_dir, record_name) 