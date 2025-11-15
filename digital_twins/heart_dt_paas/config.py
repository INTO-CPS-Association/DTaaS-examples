#!/usr/bin/env python3
"""
Configuration Module for Heart Digital Twin
Contains global configuration settings
"""

# Server configuration
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 5001

# ECG display configuration
DEFAULT_RECORD = '100'
DEFAULT_WINDOW_SECONDS = 5
RECORDS_RANGE = range(100, 110)  # Records 100-109

# Model configuration
HEART_MODEL_PATHS = [
    "../models/heart-dt/source/Beating heart.glb",
    "../models/heart-dt/source/bh2.glb"
] 