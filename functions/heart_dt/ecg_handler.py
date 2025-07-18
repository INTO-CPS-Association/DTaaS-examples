#!/usr/bin/env python3
"""
ECG Handler module for Heart Digital Twin
Manages the ECG data processing functions
"""
import os
import io
import base64
from threading import Lock
import numpy as np
import wfdb
import matplotlib.pyplot as plt
import time

# Set the backend before importing matplotlib
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive saving

# Import data handling functions
from data.heart_twin_data.record_loader import download_record, get_record_path

# Global variables to store ECG data
record_data = {}
current_position = 0
data_lock = Lock()  # Lock for thread safety

def init_ecg_data(record_name='100', window_seconds=5):
    """Initialize the ECG data from the specified record"""
    global record_data, current_position
    
    # Download the record if needed, stores in data folder
    if not download_record(record_name):
        print(f"Failed to download record {record_name}")
        return False
    
    # Get the record path in the data folder
    record_path = get_record_path(record_name)
    
    # Read the record
    print(f"Reading record {record_name} from {record_path}...")
    try:
        record = wfdb.rdrecord(record_path)
        # Read the annotations (this contains the anomaly information)
        ann = wfdb.rdann(record_path, 'atr')
        
        # Process and print anomalies
        print_anomalies(record, ann, record_name)

    except Exception as e:
        print(f"Error reading record: {e}")
        return False
    
    fs = record.fs  # Sampling frequency
    signal = record.p_signal  # The signal data
    
    # Get lead/channel names from the record
    channel_names = []
    print(f"Record signal names: {record.sig_name}")
    
    lead_descriptions = {
        'MLII': 'Modified Limb Lead II (MLII)',
        'V1': 'Precordial Lead V1',
        'V2': 'Precordial Lead V2',
        'V3': 'Precordial Lead V3',
        'V4': 'Precordial Lead V4',
        'V5': 'Precordial Lead V5',
        'V6': 'Precordial Lead V6',
        'aVR': 'Augmented Vector Right (aVR)',
        'aVL': 'Augmented Vector Left (aVL)',
        'aVF': 'Augmented Vector Foot (aVF)',
        'I': 'Lead I',
        'II': 'Lead II',
        'III': 'Lead III'
    }
    
    for i, sig_name in enumerate(record.sig_name):
        if sig_name in lead_descriptions:
            lead_description = f"Channel {i}: {lead_descriptions[sig_name]}"
        else:
            lead_description = f"Channel {i}: {sig_name}"
        
        channel_names.append(lead_description)
        print(f"Added channel: {lead_description}")
    
    with data_lock:
        record_data = {
            'signal': signal,
            'fs': fs,
            'n_samples': signal.shape[0],
            'window_size': int(fs * window_seconds),
            'channel': 0,  # Use first channel by default
            'channel_names': channel_names,  # Store channel names
            'record_name': record_name,  # Store the record name
            'annotations': {
                'sample': ann.sample,
                'symbol': ann.symbol,
                'aux_note': ann.aux_note
            }  # Store the annotations
        }
        current_position = 0
    
    print(f"Record loaded: {record_data['n_samples']} samples, {signal.shape[1]} channels, {fs} Hz sampling rate")
    print(f"Available channels: {', '.join(channel_names)}")
    return True

def generate_plot():
    """Generate a plot for the current window of ECG data with anomaly markers"""
    global current_position, record_data
    
    try:
        with data_lock:
            if not record_data or 'signal' not in record_data:
                print("No ECG data available for plotting")
                return None
                
            # Get the current window
            start = current_position
            window_size = record_data['window_size']
            end = start + window_size
            
            # Ensure we don't exceed the data length
            if end > record_data['n_samples']:
                end = record_data['n_samples']
                start = max(0, end - window_size)
                # Reset to beginning if we've reached the end
                if end == record_data['n_samples']:
                    current_position = 0
                else:
                    current_position = start
            else:
                # Move the window for next time
                current_position += int(window_size * 0.1)  # Overlap windows by 90%
            
            # Extract data for the current window
            channel = record_data['channel']
            data = record_data['signal'][start:end, channel]
            fs = record_data['fs']
            xdata = np.arange(start, end) / fs  # Time axis in seconds
            
            # Get current channel name for the title
            current_channel_name = "ECG Lead"
            if 'channel_names' in record_data and len(record_data['channel_names']) > channel:
                channel_name = record_data['channel_names'][channel]
                # Extract the part after the colon (if present)
                if ': ' in channel_name:
                    current_channel_name = channel_name.split(': ', 1)[1]
                else:
                    current_channel_name = channel_name
            
            # Get record name
            record_name = record_data.get('record_name', 'Unknown')
            
            # Get annotations within this window
            annotations = {}
            if 'annotations' in record_data:
                ann_samples = record_data['annotations']['sample']
                ann_symbols = record_data['annotations']['symbol']
                
                # Find annotations within the current window
                for i, sample in enumerate(ann_samples):
                    if start <= sample < end:
                        sample_x = sample / fs  # Convert to time
                        if ann_symbols[i] not in annotations:
                            annotations[ann_symbols[i]] = []
                        annotations[ann_symbols[i]].append((sample_x, data[int(sample - start)]))
        
        # Generate the plot with enhanced styling
        plt.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
        
        # Plot the ECG with a better style
        ax.plot(xdata, data, color='#1a75ff', lw=1.5)
        
        # Define colors and markers for different anomalies
        anomaly_styles = {
            'N': ('o', '#3CB371', 'Normal beat'),  # Green circle
            'L': ('s', '#FFA500', 'Left bundle branch block'),  # Orange square
            'R': ('D', '#9370DB', 'Right bundle branch block'),  # Purple diamond
            'A': ('^', '#FF6347', 'Atrial premature beat'),  # Red triangle
            'V': ('*', '#DC143C', 'Premature ventricular contraction'),  # Crimson star
            'E': ('P', '#8B008B', 'Ventricular escape beat'),  # Dark magenta pentagon
            'j': ('h', '#2E8B57', 'Nodal escape beat'),  # Sea green hexagon
            '/': ('X', '#4682B4', 'Paced beat'),  # Steel blue X
            'F': ('+', '#B8860B', 'Fusion of paced and normal beat'),  # Dark goldenrod plus
            '!': ('d', '#FF0000', 'Ventricular flutter wave'),  # Red thin diamond
            'a': ('<', '#FF69B4', 'Aberrated atrial premature beat'),  # Hot pink left triangle
            'S': ('>', '#1E90FF', 'Supraventricular premature beat')  # Dodger blue right triangle
        }
        
        # Add markers for anomalies
        legend_elements = []
        from matplotlib.lines import Line2D
        
        # Sort anomalies so more severe ones are on top
        priority_order = ['!', 'V', 'A', 'E', 'L', 'R', 'j', 'a', 'S', 'F', '/', 'N']
        sorted_anomalies = sorted(annotations.keys(), 
                                  key=lambda x: priority_order.index(x) if x in priority_order else 99)
        
        # Plot annotations with markers
        for symbol in sorted_anomalies:
            if symbol == 'N':  # Skip plotting all normal beats to avoid clutter
                continue
                
            points = annotations[symbol]
            style = anomaly_styles.get(symbol, ('o', '#808080', f'Unknown ({symbol})'))
            
            # Plot points
            x_points = [p[0] for p in points]
            y_points = [p[1] for p in points]
            
            # Add markers
            ax.scatter(x_points, y_points, marker=style[0], color=style[1], s=80, 
                       zorder=3, alpha=0.8, edgecolors='white', linewidth=1)
            
            # Add to legend (only once per type)
            legend_elements.append(Line2D([0], [0], marker=style[0], color='w', 
                                         markerfacecolor=style[1], markersize=10, 
                                         label=style[2]))
        
        # Add a grid that resembles ECG paper
        ax.grid(which='major', linestyle='-', linewidth='0.5', color='#ff9999', alpha=0.3)
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='#ffcccc', alpha=0.2)
        ax.minorticks_on()
        
        # Customize appearance
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('#f8f9fa')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#dddddd')
        ax.spines['bottom'].set_color('#dddddd')
        
        # Add labels and title
        ax.set_xlabel("Time (s)", fontsize=10, color='#444444')
        ax.set_ylabel("Amplitude (mV)", fontsize=10, color='#444444')
        ax.set_title(f"DTaaS Heart Digital Twin - Record {record_name}, {current_channel_name}", 
                    fontsize=12, color='#333333', fontweight='bold')
        
        # Add time range information
        time_info = f"Time window: {xdata[0]:.1f}s - {xdata[-1]:.1f}s"
        ax.annotate(time_info, xy=(0.02, 0.97), xycoords='axes fraction', 
                   fontsize=8, color='#666666', verticalalignment='top')
        
        # Add legend if we have anomalies
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', title="Anomalies", 
                     fontsize=8, title_fontsize=9)
        
        # Convert plot to PNG image with higher quality
        img = io.BytesIO()
        plt.tight_layout()
        fig.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        img.seek(0)
        
        return base64.b64encode(img.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"Error in generate_plot: {e}")
        return None
    

def print_anomalies(record, ann, record_name):
    """Print anomaly information to the console"""
    print("\n========== ECG ANOMALIES DETECTED ==========")
    print(f"Record: {record_name}")
    print("\nBeat classification symbols:")
    print("N: Normal beat")
    print("L: Left bundle branch block beat")
    print("R: Right bundle branch block beat")
    print("A: Atrial premature beat")
    print("V: Premature ventricular contraction")
    print("!: Ventricular flutter wave")
    print("/: Paced beat")
    print("F: Fusion of paced and normal beat")
    print("E: Ventricular escape beat")
    print("j: Nodal (junctional) escape beat")
    print("a: Aberrated atrial premature beat")
    print("S: Supraventricular premature beat")
    
    # Count anomalies by type
    anomaly_counts = {}
    normal_count = 0
    
    for i, symbol in enumerate(ann.symbol):
        if symbol == 'N':  # Normal beat
            normal_count += 1
            continue
            
        # All other symbols are considered anomalies
        if symbol not in anomaly_counts:
            anomaly_counts[symbol] = 0
        anomaly_counts[symbol] += 1
        
        # Print sample anomalies (limit output for clarity)
        if anomaly_counts[symbol] <= 5:  # Print only first 5 instances of each type
            sample_num = ann.sample[i]
            time_sec = sample_num / record.fs
            print(f"Anomaly '{symbol}' detected at sample {sample_num} (time: {time_sec:.2f}s)")
    
    # Print summary
    print("\n========== ANOMALY SUMMARY ==========")
    print(f"Total normal beats: {normal_count}")
    
    if anomaly_counts:
        print("\nAnomalies detected:")
        for symbol, count in anomaly_counts.items():
            print(f"  {symbol}: {count} instances")
    else:
        print("\nNo anomalies detected in this record.")
    
    print("=====================================\n")


def update_parameters(params):
    """Update the ECG display parameters"""
    global record_data, current_position
    
    start_time = time.time()
    try:
        with data_lock:
            if not record_data:
                return False, "No ECG data loaded"
                
            if 'channel' in params:
                channel = int(params['channel'])
                if 0 <= channel < record_data['signal'].shape[1]:
                    record_data['channel'] = channel
                else:
                    return False, f"Invalid channel. Must be 0-{record_data['signal'].shape[1]-1}"
            
            if 'window_seconds' in params:
                window_seconds = float(params['window_seconds'])
                if 1 <= window_seconds <= 60:
                    record_data['window_size'] = int(record_data['fs'] * window_seconds)
                else:
                    return False, "Window size must be between 1-60 seconds"
            
            if 'reset' in params and params['reset']:
                current_position = 0
                
            # Return current information
            return True, {
                "current_channel": record_data.get('channel', 0),
                "channel_names": record_data.get('channel_names', [])
            }
            
    except Exception as e:
        print(f"Error updating parameters: {e}")
        return False, str(e)
    end_time = time.time()
    print(f"Parameter update took: {end_time - start_time:.2f} seconds")

def get_current_info():
    """Get current record and channel information"""
    with data_lock:
        if not record_data:
            return False, "No ECG data loaded", {}
        
        return True, "Success", {
            "current_record": record_data.get('record_name', '100'),
            "current_channel": record_data.get('channel', 0),
            "channel_names": record_data.get('channel_names', [])
        }