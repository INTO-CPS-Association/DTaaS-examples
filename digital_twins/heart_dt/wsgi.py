import os
import sys

# Add project root directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Initialize the data directory
print("Initializing data directory...")
from data.heart_dt.initialize import ensure_data_directory
data_dir = ensure_data_directory()
print(f"Data directory initialized: {data_dir}")

# Import the Flask app
from digital_twins.heart_dt.app import app, main

# Initialize the application
if not hasattr(app, '_initialized'):
    main()
    app._initialized = True
