#!/usr/bin/env python3
"""
UI Components Module for Heart Digital Twin
Contains functions to generate UI components
"""
import io
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def render_main_page():
    """Render the main page HTML template"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heart Digital Twin - DTaaS</title>
        <!-- Import model-viewer component -->
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
                margin: 0;
                padding: 20px 0;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                position: relative;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .logo {
                height: 60px;
                width: auto;
                max-width: 120px;
                object-fit: contain;
            }
            .title-container {
                flex: 1;
                text-align: center;
            }
            #ecg-container {
                text-align: center;
                margin-top: 20px;
            }
            #ecg-image {
                max-width: 100%;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .status-bar {
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
                padding: 8px 15px;
                background-color: #f0f0f0;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            .status-item {
                display: flex;
                align-items: center;
            }
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-running {
                background-color: #28a745;
            }
            .status-paused {
                background-color: #ffc107;
            }
            .status-heart-normal {
                background-color: #28a745;
            }
            .controls {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 15px;
                margin: 20px 0;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
                border: 1px solid #eee;
            }
            .control-group {
                display: flex;
                flex-direction: column;
                min-width: 150px;
            }
            label {
                margin-bottom: 5px;
                font-weight: bold;
                font-size: 14px;
                color: #555;
            }
            select, input, button {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            button {
                background-color: #4a7aff;
                color: white;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #3a64d8;
            }
            #pauseButton {
                background-color: #6c757d;
            }
            #pauseButton:hover {
                background-color: #5a6268;
            }
            #pauseButton.paused {
                background-color: #28a745;
            }
            #pauseButton.paused:hover {
                background-color: #218838;
            }
            .notification {
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            #channel, #record {
                min-width: 280px;
            }
            .heart-model-container {
                margin: 20px 0;
                text-align: center;
                border-radius: 5px;
                overflow: hidden;
                position: relative;
            }
            model-viewer {
                width: 100%;
                height: 350px;
                background-color: #f8f9fa;
                --poster-color: transparent;
                --progress-bar-color: #4a7aff;
                --progress-mask: transparent;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            .model-controls {
                position: absolute;
                bottom: 10px;
                right: 10px;
                display: flex;
                gap: 5px;
                z-index: 100;
            }
            .model-btn {
                background-color: rgba(255, 255, 255, 0.7);
                color: #333;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .model-btn:hover {
                background-color: rgba(255, 255, 255, 0.9);
            }
            .debug-link {
                position: absolute;
                bottom: 5px;
                right: 5px;
                font-size: 10px;
                color: #ccc;
                text-decoration: none;
            }
            .debug-link:hover {
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="/static/bits.png" alt="BITS Logo" class="logo" style="margin-right: 10px;">
                <div class="title-container">
                    <h1>Heart Digital Twin - DTaaS</h1>
                </div>
                <img src="/static/into-cps.png" alt="INTO-CPS Logo" class="logo" style="margin-left: 10px;">
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label for="record">Patient Record:</label>
                    <select id="record">
                        <option value="100">Record 100</option>
                        <option value="101">Record 101</option>
                        <option value="102">Record 102</option>
                        <option value="103">Record 103</option>
                        <option value="104">Record 104</option>
                        <option value="105">Record 105</option>
                        <option value="106">Record 106</option>
                        <option value="107">Record 107</option>
                        <option value="108">Record 108</option>
                        <option value="109">Record 109</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="channel">ECG Lead Selection:</label>
                    <select id="channel">
                        <option value="0">Loading channel information...</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="windowSize">Window Size (sec):</label>
                    <input type="number" id="windowSize" min="1" max="60" value="5" step="1">
                </div>
                
                <div class="control-group">
                    <label for="updateRate">Refresh Rate:</label>
                    <select id="updateRate">
                        <option value="10">Very Fast (0.01s)</option>
                        <option value="1000" selected>Fast (1s)</option>
                        <option value="2000">Medium (2s)</option>
                        <option value="5000">Slow (5s)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>&nbsp;</label>
                    <button id="applyButton">Apply Settings</button>
                </div>
                
                <div class="control-group">
                    <label>&nbsp;</label>
                    <button id="resetButton">Reset Position</button>
                </div>
                
                <div class="control-group">
                    <label>&nbsp;</label>
                    <button id="pauseButton">Pause Simulation</button>
                </div>
            </div>
            
            <div id="notification" class="notification"></div>
            
            <!-- 3D Heart Model -->
            <div class="heart-model-container">
                <model-viewer 
                    id="heart-model"
                    src="/static/heart-model" 
                    alt="3D Heart Model"
                    camera-controls
                    camera-orbit="0deg 75deg 2.5m"
                    field-of-view="30deg"
                    shadow-intensity="0.6"
                    environment-image="neutral"
                    autoplay
                    animation-name="HeartBeat001">
                    <div class="progress-bar hide" slot="progress-bar">
                        <div class="update-bar"></div>
                    </div>
                </model-viewer>
                
                <div class="model-controls">
                    <button class="model-btn" id="reset-camera">Reset View</button>
                    <button class="model-btn" id="toggle-rotate">Auto-Rotate</button>
                </div>
            </div>
            
            <div id="ecg-container">
                <img id="ecg-image" src="/ecg-data" alt="ECG Graph">
                <div class="status-bar">
                    <div class="status-item">
                        <div class="status-indicator status-running" id="simulation-indicator"></div>
                        <span id="simulation-status">Simulation: Ongoing</span>
                    </div>
                    <div class="status-item">
                        <div class="status-indicator status-heart-normal"></div>
                        <span>Heart Health: Normal</span>
                    </div>
                </div>
            </div>
            
            <a href="/debug-info" target="_blank" class="debug-link">Debug Info</a>
        </div>
        
        <script>
            let isUpdating = false;
            let updateInterval = 1000;
            let updateTimer = null;
            let isPaused = false;
            let currentRecord = null;
            
            // Load channel information on page load
            window.addEventListener('load', async function() {
                await loadChannelInfo();
                updateECG(); // Initial ECG update
                // Set the default record in the dropdown
                const recordSelect = document.getElementById('record');
                // Get the current record from the server
                const response = await fetch('/get-info');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.current_record) {
                        recordSelect.value = data.current_record;
                        currentRecord = data.current_record;
                    }
                }
                
                // Sync heart model animation with pause/resume
                const heartModel = document.getElementById('heart-model');
                if (heartModel) {
                    // Wait for model to load
                    heartModel.addEventListener('load', () => {
                        // If simulation is paused, pause the heart animation too
                        if (isPaused) {
                            heartModel.pause();
                        }
                    });
                    
                    // Set up model control buttons
                    document.getElementById('reset-camera').addEventListener('click', () => {
                        heartModel.cameraOrbit = "0deg 75deg 2.5m";
                        heartModel.fieldOfView = "30deg";
                    });
                    
                    document.getElementById('toggle-rotate').addEventListener('click', () => {
                        heartModel.autoRotate = !heartModel.autoRotate;
                    });
                }
            });
            
            // Function to load channel information
            async function loadChannelInfo() {
                try {
                    const response = await fetch('/get-info');
                    const data = await response.json();
                    
                    if (data.success && data.channel_names && data.channel_names.length > 0) {
                        const channelSelect = document.getElementById('channel');
                        channelSelect.innerHTML = ''; // Clear existing options
                        
                        // Add options for each channel
                        data.channel_names.forEach((channelName, index) => {
                            const option = document.createElement('option');
                            option.value = index;
                            option.textContent = channelName;
                            channelSelect.appendChild(option);
                        });
                        
                        // Set the current selected channel
                        channelSelect.value = data.current_channel || 0;
                    } else {
                        showNotification('Failed to load channel information', true);
                    }
                } catch (error) {
                    console.error('Error loading channel information:', error);
                    showNotification('Failed to load channel information', true);
                }
            }
            
            // Function to show notification
            function showNotification(message, isError = false) {
                const notification = document.getElementById('notification');
                notification.textContent = message;
                notification.className = 'notification ' + (isError ? 'error' : 'success');
                notification.style.display = 'block';
                
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
            }
            
            // Function to update ECG display
            async function updateECG() {
                if (isUpdating || isPaused) return;
                
                try {
                    isUpdating = true;
                    
                    const response = await fetch('/ecg-data?t=' + new Date().getTime());
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const imageData = await response.text();
                    const img = document.getElementById('ecg-image');
                    
                    // Create a new image element to preload
                    const newImg = new Image();
                    newImg.onload = function() {
                        // Only replace the image once it's fully loaded
                        img.src = imageData;
                        isUpdating = false;
                    };
                    newImg.onerror = function() {
                        console.error("Failed to load ECG image");
                        isUpdating = false;
                    };
                    newImg.src = imageData;
                    
                } catch (error) {
                    console.error('Error updating ECG:', error);
                    isUpdating = false;
                }
            }
            
            // Function to toggle simulation pause
            function togglePause() {
                isPaused = !isPaused;
                const pauseButton = document.getElementById('pauseButton');
                const simulationStatus = document.getElementById('simulation-status');
                const simulationIndicator = document.getElementById('simulation-indicator');
                const heartModel = document.getElementById('heart-model');
                
                if (isPaused) {
                    pauseButton.textContent = 'Resume Simulation';
                    pauseButton.classList.add('paused');
                    simulationStatus.textContent = 'Simulation: Paused';
                    simulationIndicator.classList.remove('status-running');
                    simulationIndicator.classList.add('status-paused');
                    
                    // Pause heart model animation
                    if (heartModel) {
                        heartModel.pause();
                    }
                    
                    // Clear the timer
                    if (updateTimer) {
                        clearInterval(updateTimer);
                        updateTimer = null;
                    }
                } else {
                    pauseButton.textContent = 'Pause Simulation';
                    pauseButton.classList.remove('paused');
                    simulationStatus.textContent = 'Simulation: Ongoing';
                    simulationIndicator.classList.remove('status-paused');
                    simulationIndicator.classList.add('status-running');
                    
                    // Resume heart model animation
                    if (heartModel) {
                        heartModel.play();
                    }
                    
                    // Restart the timer
                    updateECG(); // Update immediately
                    updateTimer = setInterval(updateECG, updateInterval);
                }
                
                showNotification(isPaused ? 'Simulation paused' : 'Simulation resumed');
            }
            
            // Function to apply new settings
            async function applySettings() {
                const channel = document.getElementById('channel').value;
                const windowSize = document.getElementById('windowSize').value;
                const recordSelect = document.getElementById('record');
                const recordId = recordSelect.value;
                
                try {
                    // Check if record has changed
                    if (recordId !== currentRecord) {
                        // First, pause the simulation if it's running
                        const wasPaused = isPaused;
                        if (!wasPaused) {
                            togglePause();
                        }
                        
                        showNotification(`Loading record ${recordId}...`);
                        
                        // Load the new record
                        const recordResponse = await fetch('/set-parameters', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                record: recordId
                            })
                        });
                        
                        const recordResult = await recordResponse.json();
                        if (recordResult.success) {
                            showNotification(`Record ${recordId} loaded successfully`);
                            currentRecord = recordId;
                            
                            // Update channel dropdown with the new record's channels
                            if (recordResult.channel_names && recordResult.channel_names.length > 0) {
                                console.log('Updating channel names:', recordResult.channel_names);
                                const channelSelect = document.getElementById('channel');
                                channelSelect.innerHTML = '';
                                
                                recordResult.channel_names.forEach((channelName, index) => {
                                    const option = document.createElement('option');
                                    option.value = index;
                                    option.textContent = channelName;
                                    channelSelect.appendChild(option);
                                });
                                
                                channelSelect.value = recordResult.current_channel || 0;
                            } else {
                                console.warn('No channel names received from server');
                            }
                            
                            // Resume simulation if it wasn't previously paused
                            if (!wasPaused) {
                                togglePause();
                            }
                            
                            return; // Exit early as we've already handled the record change
                        } else {
                            showNotification(recordResult.message || `Failed to load record ${recordId}`, true);
                            // Resume if needed and continue with other settings
                            if (!wasPaused) {
                                togglePause();
                            }
                        }
                    }
                    
                    // Apply other settings (channel and window size)
                    const response = await fetch('/set-parameters', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            channel: parseInt(channel),
                            window_seconds: parseFloat(windowSize)
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        showNotification('Settings applied successfully');
                        
                        // If channel names were returned, update the dropdown
                        if (result.channel_names && result.channel_names.length > 0) {
                            const channelSelect = document.getElementById('channel');
                            
                            // Only update if needed to avoid removing user selection
                            if (channelSelect.options.length !== result.channel_names.length) {
                                channelSelect.innerHTML = ''; // Clear existing options
                                
                                // Add options for each channel
                                result.channel_names.forEach((channelName, index) => {
                                    const option = document.createElement('option');
                                    option.value = index;
                                    option.textContent = channelName;
                                    channelSelect.appendChild(option);
                                });
                            }
                            
                            // Set the current selected channel
                            channelSelect.value = result.current_channel || 0;
                        }
                    } else {
                        showNotification(result.message || 'Failed to apply settings', true);
                    }
                } catch (error) {
                    console.error('Error applying settings:', error);
                    showNotification('Network error occurred', true);
                }
            }
            
            // Function to reset ECG position
            async function resetPosition() {
                try {
                    const response = await fetch('/set-parameters', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            reset: true
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        showNotification('ECG position reset');
                        updateECG(); // Force immediate update
                    } else {
                        showNotification(result.message || 'Failed to reset position', true);
                    }
                } catch (error) {
                    console.error('Error resetting position:', error);
                    showNotification('Network error occurred', true);
                }
            }
            
            // Function to change update rate
            function changeUpdateRate() {
                const rate = parseInt(document.getElementById('updateRate').value);
                updateInterval = rate;
                
                // Reset the interval timer if not paused
                if (!isPaused) {
                    if (updateTimer) {
                        clearInterval(updateTimer);
                    }
                    updateTimer = setInterval(updateECG, updateInterval);
                }
                showNotification(`Refresh rate changed to ${rate/1000}s`);
            }
            
            // Set up event listeners
            document.getElementById('applyButton').addEventListener('click', applySettings);
            document.getElementById('resetButton').addEventListener('click', resetPosition);
            document.getElementById('updateRate').addEventListener('change', changeUpdateRate);
            document.getElementById('pauseButton').addEventListener('click', togglePause);
            
            // Start the update timer
            updateTimer = setInterval(updateECG, updateInterval);
        </script>
    </body>
    </html>
    '''

def generate_bits_logo():
    """Generate a placeholder BITS logo"""
    # Generate a placeholder logo
    fig, ax = plt.subplots(figsize=(2, 2), dpi=100)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Draw BITS text
    ax.text(50, 50, 'BITS', fontsize=24, weight='bold', 
            ha='center', va='center', color='navy')
    
    # Add border
    rect = Rectangle((5, 5), 90, 90, linewidth=2, edgecolor='blue', facecolor='none')
    ax.add_patch(rect)
    
    # Save to BytesIO
    img = io.BytesIO()
    plt.tight_layout()
    fig.savefig(img, format='png', dpi=100, transparent=True)
    plt.close(fig)
    img.seek(0)
    
    return img

def generate_into_cps_logo():
    """Generate a placeholder INTO-CPS logo"""
    # Generate a placeholder logo
    fig, ax = plt.subplots(figsize=(2, 2), dpi=100)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Draw INTO-CPS text
    ax.text(50, 50, 'INTO-CPS', fontsize=18, weight='bold', 
            ha='center', va='center', color='darkgreen')
    
    # Add border
    rect = Rectangle((5, 5), 90, 90, linewidth=2, edgecolor='green', facecolor='none')
    ax.add_patch(rect)
    
    # Save to BytesIO
    img = io.BytesIO()
    plt.tight_layout()
    fig.savefig(img, format='png', dpi=100, transparent=True)
    plt.close(fig)
    img.seek(0)
    
    return img 