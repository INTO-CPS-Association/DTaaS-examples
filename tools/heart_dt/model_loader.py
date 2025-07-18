#!/usr/bin/env python3
"""
Model Loader Module for Heart Digital Twin
Handles loading of 3D heart models
"""
import os

def get_heart_model():
    """
    Get the binary data for the heart model
    
    Returns:
        tuple: (binary_data, success_flag)
    """
    # Get the absolute path to the models directory
    current_file = os.path.abspath(__file__)
    tools_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(os.path.dirname(tools_dir))  # Go up to project root
    models_dir = os.path.join(project_root, 'models', 'heart_dt', 'source')
    
    # Try both model files
    model_paths = [
        os.path.join(models_dir, 'Beating heart.glb'),
        os.path.join(models_dir, 'bh2.glb')
    ]
    
    # Try each model path
    for model_path in model_paths:
        print(f"Checking for heart model at: {model_path}")
        if os.path.exists(model_path):
            try:
                # Read and return the binary data
                with open(model_path, 'rb') as file:
                    model_data = file.read()
                print(f"Loaded heart model from: {model_path}")
                return model_data, True
            except Exception as e:
                print(f"Error loading heart model from {model_path}: {e}")
    
    print("No heart model found")
    return None, False 