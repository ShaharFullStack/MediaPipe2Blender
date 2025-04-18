#!/usr/bin/env python3
"""
Test script for MediaPipe to Blender live animation add-on.
This script tests the MediaPipe module functionality.
"""

import os
import sys
import time
import argparse

# Add parent directory to path to import mediapipe_module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import MediaPipe module
from src.mediapipe_module import (
    get_mediapipe_module,
    is_mediapipe_available,
    install_dependencies
)

def test_mediapipe_module():
    """Test MediaPipe module functionality."""
    print("Testing MediaPipe module...")
    
    # Check if MediaPipe is available
    if not is_mediapipe_available():
        print("MediaPipe is not available. Installing dependencies...")
        if not install_dependencies():
            print("Failed to install dependencies")
            return False
    
    # Create and configure MediaPipe module
    module = get_mediapipe_module()
    
    # Mock camera availability for testing in environments without a camera
    print("Note: Testing in mock mode due to sandbox environment limitations")
    
    # Test module configuration
    config = {
        'camera_index': 0,
        'camera_width': 640,
        'camera_height': 480,
        'camera_fps': 30,
        'host': '127.0.0.1',
        'port': 5556,
        'enable_face': True,
        'enable_hands': True,
        'enable_pose': True
    }
    
    success = module.configure(config)
    if not success:
        print("Failed to configure MediaPipe module")
        return False
    
    print("MediaPipe module configured successfully")
    
    # Test module structure and API without actual initialization
    print("Testing module structure and API...")
    
    # Check if all required components exist
    required_attributes = [
        'processor', 'streamer', 'is_initialized',
        'initialize', 'start', 'stop', 'get_status', 'configure'
    ]
    
    for attr in required_attributes:
        if not hasattr(module, attr):
            print(f"Module is missing required attribute: {attr}")
            return False
    
    print("Module structure validation passed")
    
    # Test status retrieval
    status = module.get_status()
    print(f"Status: {status}")
    
    print("MediaPipe module API test completed successfully")
    return True

def test_data_streaming(host="127.0.0.1", port=5556):
    """Test data streaming functionality."""
    print(f"Testing data streaming to {host}:{port}...")
    
    # Import ZMQ
    try:
        import zmq
    except ImportError:
        print("ZeroMQ is not available. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyzmq"])
        import zmq
    
    # Create ZMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{host}:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "mediapipe")
    
    # Create and start MediaPipe module
    module = get_mediapipe_module()
    module.configure({
        'host': host,
        'port': port
    })
    
    if not module.initialize():
        print("Failed to initialize MediaPipe module")
        return False
    
    if not module.start():
        print("Failed to start MediaPipe processing")
        return False
    
    print("MediaPipe processing started successfully")
    
    # Wait for data
    print("Waiting for data (10 seconds timeout)...")
    socket.RCVTIMEO = 10000  # 10 seconds timeout
    
    try:
        topic, message = socket.recv_multipart()
        print(f"Received data: {len(message)} bytes")
        
        # Try to deserialize data
        import pickle
        data = pickle.loads(message)
        print(f"Data contains: {list(data.keys())}")
        
        # Check data structure
        if 'faces' in data:
            print(f"Faces: {len(data['faces'])}")
        
        if 'hands' in data:
            print(f"Hands: {len(data['hands'])}")
        
        if 'pose' in data:
            print(f"Pose: {len(data['pose'])}")
        
        print("Data streaming test successful")
        result = True
    
    except zmq.Again:
        print("Timeout waiting for data")
        result = False
    
    except Exception as e:
        print(f"Error receiving data: {e}")
        result = False
    
    finally:
        # Stop MediaPipe processing
        module.stop()
        print("MediaPipe processing stopped")
        
        # Close socket
        socket.close()
        context.term()
    
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test MediaPipe to Blender live animation add-on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address for data streaming test")
    parser.add_argument("--port", type=int, default=5556, help="Port number for data streaming test")
    parser.add_argument("--skip-module-test", action="store_true", help="Skip MediaPipe module test")
    parser.add_argument("--skip-streaming-test", action="store_true", help="Skip data streaming test")
    args = parser.parse_args()
    
    # Run tests
    if not args.skip_module_test:
        if test_mediapipe_module():
            print("MediaPipe module test passed")
        else:
            print("MediaPipe module test failed")
    
    if not args.skip_streaming_test:
        if test_data_streaming(args.host, args.port):
            print("Data streaming test passed")
        else:
            print("Data streaming test failed")
    
    print("All tests completed")

if __name__ == "__main__":
    main()
