#!/usr/bin/env python3
"""
Test script for data streaming functionality.
This script tests the ZeroMQ data streaming between MediaPipe and Blender.
"""

import os
import sys
import time
import threading
import pickle
import argparse

# Add parent directory to path to import mediapipe_module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def create_mock_data():
    """Create mock MediaPipe data for testing."""
    # Create mock face data
    face_data = {
        'landmarks': [
            {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0} for _ in range(468)
        ],
        'visibility': [1.0] * 468,
        'timestamp': time.time() * 1000,
        'detection_confidence': 0.95,
        'tracking_id': 0
    }
    
    # Create mock hand data (left)
    left_hand_data = {
        'landmarks': [
            {'x': 0.3, 'y': 0.6, 'z': 0.0} for _ in range(21)
        ],
        'timestamp': time.time() * 1000,
        'detection_confidence': 0.9,
        'tracking_id': 0,
        'handedness': 'Left',
        'hand_flag': 0
    }
    
    # Create mock hand data (right)
    right_hand_data = {
        'landmarks': [
            {'x': 0.7, 'y': 0.6, 'z': 0.0} for _ in range(21)
        ],
        'timestamp': time.time() * 1000,
        'detection_confidence': 0.9,
        'tracking_id': 1,
        'handedness': 'Right',
        'hand_flag': 1
    }
    
    # Create mock pose data
    pose_data = {
        'landmarks': [
            {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0} for _ in range(33)
        ],
        'visibility': [1.0] * 33,
        'timestamp': time.time() * 1000,
        'detection_confidence': 0.95,
        'tracking_id': 0
    }
    
    # Create complete data structure
    data = {
        'faces': [face_data],
        'hands': [left_hand_data, right_hand_data],
        'pose': [pose_data],
        'frame_timestamp': time.time() * 1000,
        'frame_index': 0,
        'source_dimensions': (640, 480)
    }
    
    return data

def run_mock_server(host="127.0.0.1", port=5556, topic="mediapipe", duration=10, fps=30):
    """Run a mock ZeroMQ server that sends MediaPipe data."""
    print(f"Starting mock ZeroMQ server on {host}:{port}...")
    
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
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{host}:{port}")
    
    # Send data at specified FPS
    frame_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Create mock data
            data = create_mock_data()
            data['frame_index'] = frame_count
            
            # Serialize data
            message = pickle.dumps(data)
            
            # Send data
            socket.send_multipart([topic.encode('utf-8'), message])
            
            # Update frame count
            frame_count += 1
            
            # Sleep to maintain FPS
            time.sleep(1.0 / fps)
        
        print(f"Sent {frame_count} frames in {duration} seconds")
        print(f"Average FPS: {frame_count / duration:.1f}")
    
    finally:
        # Close socket
        socket.close()
        context.term()
        print("Mock server stopped")

def run_client(host="127.0.0.1", port=5556, topic="mediapipe", duration=10):
    """Run a ZeroMQ client that receives MediaPipe data."""
    print(f"Starting ZeroMQ client connecting to {host}:{port}...")
    
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
    socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    # Receive data
    frame_count = 0
    start_time = time.time()
    
    try:
        # Set timeout
        socket.RCVTIMEO = int(duration * 1000)  # milliseconds
        
        while time.time() - start_time < duration:
            try:
                # Receive data
                topic_bytes, message = socket.recv_multipart()
                
                # Deserialize data
                data = pickle.loads(message)
                
                # Update frame count
                frame_count += 1
                
                # Print progress every 10 frames
                if frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"Received {frame_count} frames in {elapsed:.1f} seconds ({frame_count / elapsed:.1f} FPS)")
            
            except zmq.Again:
                # Timeout
                print("Timeout waiting for data")
                break
        
        elapsed = time.time() - start_time
        print(f"Received {frame_count} frames in {elapsed:.1f} seconds")
        print(f"Average FPS: {frame_count / elapsed:.1f}")
        
        return frame_count > 0
    
    finally:
        # Close socket
        socket.close()
        context.term()
        print("Client stopped")

def test_data_streaming(host="127.0.0.1", port=5556, topic="mediapipe", duration=5, fps=30):
    """Test data streaming between server and client."""
    print(f"Testing data streaming between server and client...")
    
    # Start server in a separate thread
    server_thread = threading.Thread(
        target=run_mock_server,
        args=(host, port, topic, duration, fps)
    )
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(0.5)
    
    # Run client
    success = run_client(host, port, topic, duration)
    
    # Wait for server to finish
    server_thread.join()
    
    return success

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test data streaming functionality")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5556, help="Port number")
    parser.add_argument("--topic", type=str, default="mediapipe", help="Topic for PUB/SUB")
    parser.add_argument("--duration", type=int, default=5, help="Test duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--server-only", action="store_true", help="Run server only")
    parser.add_argument("--client-only", action="store_true", help="Run client only")
    args = parser.parse_args()
    
    if args.server_only:
        run_mock_server(args.host, args.port, args.topic, args.duration, args.fps)
    elif args.client_only:
        run_client(args.host, args.port, args.topic, args.duration)
    else:
        if test_data_streaming(args.host, args.port, args.topic, args.duration, args.fps):
            print("Data streaming test passed")
        else:
            print("Data streaming test failed")

if __name__ == "__main__":
    main()
