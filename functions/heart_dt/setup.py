#!/usr/bin/env python3
"""
Setup module for the Heart Digital Twin application
Handles dependency installation and other setup tasks
"""
import sys
import subprocess

def install_dependencies():
    """
    Install the required dependencies for the application
    """
    print("Installing required dependencies...")
    # Use the current Python executable to install packages
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.20.3"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas>=1.3.0", "matplotlib>=3.4.0", "wfdb>=4.1.0", "flask>=2.0.0"])
    print("Dependencies installed successfully.") 