#!/usr/bin/env python3
"""
Main module for MediaPipe to Blender live animation add-on.
This module initializes and provides access to all MediaPipe components.
"""

import os
import sys
import importlib
from typing import Dict, Any, Optional

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import submodules
from .video_capture import VideoCapture, VideoManager, get_video_manager
from .landmark_detection import (
    MediaPipeDetector, FaceDetector, HandDetector, PoseDetector,
    MediaPipeProcessor, get_mediapipe_processor,
    DetectionResult, FaceData, HandData, PoseData
)
from .data_streaming import (
    DataStreamer, ZMQStreamer, MediaPipeStreamer, get_mediapipe_streamer
)


class MediaPipeModule:
    """
    Main class for MediaPipe module.
    Provides access to all MediaPipe components.
    """
    
    def __init__(self):
        """Initialize the MediaPipe module."""
        self.video_manager = get_video_manager()
        self.processor = get_mediapipe_processor()
        self.streamer = get_mediapipe_streamer()
        
        # Module state
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the MediaPipe module.
        
        Returns:
            bool: True if successfully initialized, False otherwise
        """
        if self.is_initialized:
            return True
        
        try:
            # Check if all components are available
            if not self.processor.is_available():
                print("MediaPipe processor is not available")
                return False
            
            self.is_initialized = True
            return True
        
        except Exception as e:
            print(f"Error initializing MediaPipe module: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start MediaPipe processing and streaming.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if not self.is_initialized and not self.initialize():
            return False
        
        return self.streamer.start()
    
    def stop(self) -> None:
        """Stop MediaPipe processing and streaming."""
        self.streamer.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the MediaPipe module.
        
        Returns:
            Dict[str, Any]: Dictionary with status information
        """
        return {
            'is_initialized': self.is_initialized,
            'is_streaming': self.streamer.is_streaming,
            'streaming_stats': self.streamer.get_streaming_stats(),
            'camera_properties': self.processor.capture.get_camera_properties()
        }
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the MediaPipe module with the specified settings.
        
        Args:
            config: Dictionary with configuration settings
            
        Returns:
            bool: True if successfully configured, False otherwise
        """
        try:
            # Stop if running
            was_streaming = self.streamer.is_streaming
            if was_streaming:
                self.stop()
            
            # Configure processor
            if 'enable_face' in config:
                self.processor.enable_face = config['enable_face']
            
            if 'enable_hands' in config:
                self.processor.enable_hands = config['enable_hands']
            
            if 'enable_pose' in config:
                self.processor.enable_pose = config['enable_pose']
            
            # Configure camera
            if 'camera_index' in config:
                self.processor.capture = self.video_manager.get_capture(config['camera_index'])
            
            if 'camera_width' in config:
                self.processor.capture.width = config['camera_width']
            
            if 'camera_height' in config:
                self.processor.capture.height = config['camera_height']
            
            if 'camera_fps' in config:
                self.processor.capture.fps = config['camera_fps']
            
            # Configure streamer
            if 'host' in config:
                self.streamer.host = config['host']
                self.streamer.streamer.host = config['host']
            
            if 'port' in config:
                self.streamer.port = config['port']
                self.streamer.streamer.port = config['port']
            
            if 'mode' in config:
                self.streamer.mode = config['mode']
                self.streamer.streamer.mode = config['mode']
            
            if 'socket_type' in config:
                self.streamer.socket_type = config['socket_type']
                self.streamer.streamer.socket_type = config['socket_type']
            
            if 'topic' in config:
                self.streamer.topic = config['topic']
                self.streamer.streamer.topic = config['topic']
            
            # Restart if was streaming
            if was_streaming:
                return self.start()
            
            return True
        
        except Exception as e:
            print(f"Error configuring MediaPipe module: {e}")
            return False
    
    def __del__(self):
        """Ensure resources are released when object is destroyed."""
        self.stop()


# Global MediaPipe module instance
mediapipe_module = None

def get_mediapipe_module() -> MediaPipeModule:
    """
    Get the global MediaPipe module instance.
    Creates a new instance if one doesn't exist.
    
    Returns:
        MediaPipeModule: Global MediaPipe module instance
    """
    global mediapipe_module
    if mediapipe_module is None:
        mediapipe_module = MediaPipeModule()
    return mediapipe_module


# Function to check if MediaPipe is available
def is_mediapipe_available() -> bool:
    """
    Check if MediaPipe is available.
    
    Returns:
        bool: True if MediaPipe is available, False otherwise
    """
    try:
        import mediapipe
        return True
    except ImportError:
        return False


# Function to install MediaPipe dependencies
def install_dependencies() -> bool:
    """
    Install MediaPipe dependencies.
    
    Returns:
        bool: True if successfully installed, False otherwise
    """
    try:
        import subprocess
        import sys
        
        # Check if pip is available
        try:
            import pip
        except ImportError:
            print("pip is not available")
            return False
        
        # Install dependencies
        packages = ["mediapipe", "opencv-python", "numpy", "pyzmq"]
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # Reload modules
        if "mediapipe" in sys.modules:
            importlib.reload(sys.modules["mediapipe"])
        
        if "cv2" in sys.modules:
            importlib.reload(sys.modules["cv2"])
        
        if "numpy" in sys.modules:
            importlib.reload(sys.modules["numpy"])
        
        if "zmq" in sys.modules:
            importlib.reload(sys.modules["zmq"])
        
        return True
    
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


if __name__ == "__main__":
    """Test the MediaPipe module functionality."""
    import argparse
    import cv2
    import time
    
    parser = argparse.ArgumentParser(description="Test MediaPipe module")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--width", type=int, default=640, help="Frame width")
    parser.add_argument("--height", type=int, default=480, help="Frame height")
    parser.add_argument("--fps", type=int, default=30, help="Target FPS")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5556, help="Port number")
    parser.add_argument("--no-face", action="store_true", help="Disable face detection")
    parser.add_argument("--no-hands", action="store_true", help="Disable hand detection")
    parser.add_argument("--no-pose", action="store_true", help="Disable pose detection")
    args = parser.parse_args()
    
    # Check if MediaPipe is available
    if not is_mediapipe_available():
        print("MediaPipe is not available. Installing dependencies...")
        if not install_dependencies():
            print("Failed to install dependencies")
            exit(1)
    
    # Create and configure MediaPipe module
    module = get_mediapipe_module()
    module.configure({
        'camera_index': args.camera,
        'camera_width': args.width,
        'camera_height': args.height,
        'camera_fps': args.fps,
        'host': args.host,
        'port': args.port,
        'enable_face': not args.no_face,
        'enable_hands': not args.no_hands,
        'enable_pose': not args.no_pose
    })
    
    # Initialize and start MediaPipe module
    if not module.initialize():
        print("Failed to initialize MediaPipe module")
        exit(1)
    
    if not module.start():
        print("Failed to start MediaPipe module")
        exit(1)
    
    try:
        print("Press ESC to exit")
        print(f"Streaming MediaPipe data to {args.host}:{args.port}")
        
        while True:
            # Get the current frame
            frame, timestamp = module.processor.capture.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Draw landmarks on the frame
            annotated_frame = module.processor.draw_landmarks(frame)
            
            # Display status
            status = module.get_status()
            stats = status['streaming_stats']
            cv2.putText(annotated_frame, f"FPS: {stats['process_fps']:.1f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Msg Rate: {stats['message_rate']:.1f}/s", (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Frames: {stats['frame_count']}", (10, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow("MediaPipe Module Test", annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
    
    finally:
        module.stop()
        cv2.destroyAllWindows()
