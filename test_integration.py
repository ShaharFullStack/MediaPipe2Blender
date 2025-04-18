#!/usr/bin/env python3
"""
Integration test script for MediaPipe to Blender live animation add-on.
This script tests the full integration between MediaPipe and Blender.
"""

import os
import sys
import time
import subprocess
import threading
import argparse

# Add parent directory to path to import mediapipe_module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def start_mediapipe_server(host="127.0.0.1", port=5556, camera=0, width=640, height=480, fps=30):
    """Start MediaPipe server in a separate process."""
    print(f"Starting MediaPipe server on {host}:{port}...")
    
    # Build command
    script_path = os.path.join(parent_dir, "src", "mediapipe_module", "__init__.py")
    cmd = [
        sys.executable,
        script_path,
        "--host", host,
        "--port", str(port),
        "--camera", str(camera),
        "--width", str(width),
        "--height", str(height),
        "--fps", str(fps)
    ]
    
    # Start process
    process = subprocess.Popen(cmd)
    
    # Wait for server to start
    time.sleep(2)
    
    return process

def start_blender_client(host="127.0.0.1", port=5556, blender_path=None, test_script=None):
    """Start Blender client in a separate process."""
    print(f"Starting Blender client connecting to {host}:{port}...")
    
    # Find Blender executable
    if blender_path is None:
        # Try to find Blender in common locations
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                blender_path = path
                break
        
        if blender_path is None:
            print("Blender executable not found. Please specify the path.")
            return None
    
    # Build command
    cmd = [blender_path, "--background"]
    
    # Add test script if provided
    if test_script is not None:
        cmd.extend(["--python", test_script])
    
    # Start process
    process = subprocess.Popen(cmd)
    
    return process

def test_full_integration(host="127.0.0.1", port=5556, blender_path=None):
    """Test full integration between MediaPipe and Blender."""
    print("Testing full integration...")
    
    # Start MediaPipe server
    server_process = start_mediapipe_server(host, port)
    
    try:
        # Start Blender client
        test_script = os.path.join(current_dir, "test_blender_addon.py")
        client_process = start_blender_client(host, port, blender_path, test_script)
        
        if client_process is None:
            print("Failed to start Blender client")
            return False
        
        # Wait for client to finish
        client_process.wait()
        
        # Check exit code
        if client_process.returncode != 0:
            print(f"Blender client exited with code {client_process.returncode}")
            return False
        
        print("Full integration test completed successfully")
        return True
    
    finally:
        # Stop MediaPipe server
        if server_process is not None:
            server_process.terminate()
            server_process.wait()
            print("MediaPipe server stopped")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test full integration between MediaPipe and Blender")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5556, help="Port number")
    parser.add_argument("--blender", type=str, default=None, help="Path to Blender executable")
    args = parser.parse_args()
    
    # Run full integration test
    if test_full_integration(args.host, args.port, args.blender):
        print("Full integration test passed")
    else:
        print("Full integration test failed")

if __name__ == "__main__":
    main()
