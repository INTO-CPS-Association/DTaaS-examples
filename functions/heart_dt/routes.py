#!/usr/bin/env python3
"""
Routes Module for Heart Digital Twin
Defines all the Flask routes for the application
"""
# Import necessary modules
from flask import Response, jsonify, request
import os

# Import ECG handling functions
from functions.heart_dt.ecg_handler import generate_plot, init_ecg_data, update_parameters, get_current_info

# Import UI components
from tools.heart_dt.ui_components import render_main_page, generate_bits_logo, generate_into_cps_logo

def register_routes(app):
    """Register all Flask routes with the application"""
    
    # Set up static file handling for multiple directories
    setup_static_paths(app)
    
    @app.route('/set-parameters', methods=['POST'])
    def set_parameters():
        """Update ECG display parameters"""
        try:
            data = request.json
            
            # Handle record change
            if 'record' in data:
                record_name = data['record']
                # Validate record name
                try:
                    record_num = int(record_name)
                    if 100 <= record_num <= 109:
                        # Initialize new record data
                        if init_ecg_data(record_name=record_name, window_seconds=5):
                            # Get updated channel information directly from ecg_handler
                            success, message, info = get_current_info()
                            if success:
                                return jsonify({
                                    "success": True,
                                    "message": f"Loaded record {record_name}",
                                    "current_channel": info.get("current_channel", 0),
                                    "channel_names": info.get("channel_names", [])
                                })
                            else:
                                return jsonify({"success": False, "message": f"Failed to get channel info for record {record_name}"})
                        else:
                            return jsonify({"success": False, "message": f"Failed to load record {record_name}"})
                    else:
                        return jsonify({"success": False, "message": "Invalid record number. Must be between 100-109"})
                except ValueError:
                    return jsonify({"success": False, "message": "Invalid record format"})
            
            # Update other parameters
            success, result = update_parameters(data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Parameters updated",
                    "current_channel": result.get("current_channel", 0),
                    "channel_names": result.get("channel_names", [])
                })
            else:
                return jsonify({"success": False, "message": result})
                
        except Exception as e:
            print(f"Error setting parameters: {e}")
            return jsonify({"success": False, "message": str(e)})

    @app.route('/get-info')
    def get_info():
        """Get current record and channel information"""
        success, message, info = get_current_info()
        
        if success:
            return jsonify({
                "success": True,
                "current_record": info.get("current_record", "100"),
                "current_channel": info.get("current_channel", 0),
                "channel_names": info.get("channel_names", [])
            })
        else:
            return jsonify({"success": False, "message": message})

    @app.route('/')
    def index():
        """Render the main page template"""
        return render_main_page()

    @app.route('/ecg-data')
    def ecg_data():
        """Generate and return the current ECG plot as an image"""
        try:
            img_data = generate_plot()
            if img_data is None:
                return Response('Error: No ECG data available', status=500, mimetype='text/plain')
            return Response(f'data:image/png;base64,{img_data}', mimetype='text/plain')
        except Exception as e:
            print(f"Error generating ECG plot: {e}")
            return Response('Error generating ECG plot', status=500, mimetype='text/plain')

    @app.route('/debug-info')
    def debug_info():
        """Get detailed debug information"""
        try:
            success, message, info = get_current_info()
            
            if success:
                # Add more debug information
                records_available = list(range(100, 110))  # Records 100-109
                
                debug_data = {
                    "success": True,
                    "current_record": info.get("current_record", "100"),
                    "current_channel": info.get("current_channel", 0),
                    "channel_names": info.get("channel_names", []),
                    "records_available": records_available,
                    "channel_count": len(info.get("channel_names", [])),
                    "app_version": "1.0.1",  # Add a version number for tracking
                    "timestamp": import_datetime().now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                }
                
                return jsonify(debug_data)
            else:
                return jsonify({
                    "success": False,
                    "message": message,
                    "timestamp": import_datetime().now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                })
                
        except Exception as e:
            print(f"Error getting debug info: {e}")
            return jsonify({
                "success": False,
                "message": str(e),
                "timestamp": import_datetime().now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            })
            
    # Helper function to import datetime only when needed
    def import_datetime():
        import datetime
        return datetime

    @app.route('/static/bits.png')
    def bits_logo():
        """Serve the BITS logo from static folder"""
        # The app's static_folder should now be set to digital_twins/static
        try:
            return app.send_static_file('bits.png')
        except Exception as e:
            print(f"Error serving bits.png: {e}")
            # Generate a placeholder logo as fallback
            img_data = generate_bits_logo()
            return Response(img_data.getvalue(), mimetype='image/png')

    @app.route('/static/into-cps.png')
    def into_cps_logo():
        """Serve the INTO-CPS logo from static folder"""
        # The app's static_folder should now be set to digital_twins/static
        try:
            return app.send_static_file('into-cps.png')
        except Exception as e:
            print(f"Error serving into-cps.png: {e}")
            # Generate a placeholder logo as fallback
            img_data = generate_into_cps_logo()
            return Response(img_data.getvalue(), mimetype='image/png')

    @app.route('/static/heart-model')
    def serve_heart_model():
        """Serve the heart model GLB file"""
        from tools.heart_dt.model_loader import get_heart_model
        
        # Get the heart model binary data
        model_data, success = get_heart_model()
        
        if not success:
            return Response("Heart model not found", status=404, mimetype='text/plain')
        
        # Serve the file with the correct content type for GLB
        return Response(model_data, mimetype='model/gltf-binary')

def setup_static_paths(app):
    """Configure static file handling for multiple directories"""
    # Get the absolute path to the digital_twins/static directory
    current_file = os.path.abspath(__file__)
    functions_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(os.path.dirname(functions_dir))  # Go up to the project root
    digital_twins_static = os.path.join(project_root, 'digital_twins', 'heart_dt', 'static')
    
    # Print static folder information for debugging
    print(f"App static folder: {app.static_folder}")
    print(f"Digital twins static folder: {digital_twins_static}")
    
    # Check if the digital_twins/static directory exists
    if os.path.exists(digital_twins_static):
        print(f"Found digital_twins/static directory at: {digital_twins_static}")
        # List files in the directory
        files = os.listdir(digital_twins_static)
        print(f"Files in digital_twins/static: {files}")
        
        # Check for logo files specifically
        bits_path = os.path.join(digital_twins_static, 'bits.png')
        into_cps_path = os.path.join(digital_twins_static, 'into-cps.png')
        
        if os.path.exists(bits_path):
            print(f"Found bits.png at: {bits_path}")
        else:
            print(f"bits.png not found at: {bits_path}")
            
        if os.path.exists(into_cps_path):
            print(f"Found into-cps.png at: {into_cps_path}")
        else:
            print(f"into-cps.png not found at: {into_cps_path}")
    else:
        print(f"Digital twins static directory not found at: {digital_twins_static}") 