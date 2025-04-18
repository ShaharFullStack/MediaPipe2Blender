#!/usr/bin/env python3
"""
Video capture module for MediaPipe to Blender live animation add-on.
This module handles webcam capture and provides frames for MediaPipe processing.
"""

import cv2
import time
import threading
import numpy as np
from typing import Tuple, Optional, Callable, Dict, Any

class VideoCapture:
    """
    Video capture class that handles webcam access and frame retrieval.
    Supports multiple camera sources and provides thread-safe access to frames.
    """
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initialize the video capture with specified parameters.
        
        Args:
            camera_index: Index of the camera to use (default: 0 for primary webcam)
            width: Desired frame width (default: 640)
            height: Desired frame height (default: 480)
            fps: Desired frames per second (default: 30)
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        
        self.cap = None
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Current frame and timestamp
        self.current_frame = None
        self.current_timestamp = 0
        
        # Performance metrics
        self.frame_count = 0
        self.start_time = 0
        self.actual_fps = 0
        
        # Callbacks
        self.frame_callbacks = []
    
    def start(self) -> bool:
        """
        Start the video capture in a separate thread.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if self.is_running:
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Start capture thread
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            
            return True
        
        except Exception as e:
            print(f"Error starting video capture: {e}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return False
    
    def stop(self) -> None:
        """Stop the video capture thread and release resources."""
        self.is_running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def _capture_loop(self) -> None:
        """Main capture loop that runs in a separate thread."""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                time.sleep(0.1)
                continue
            
            timestamp = time.time() * 1000  # Timestamp in milliseconds
            
            # Update current frame with thread safety
            with self.lock:
                self.current_frame = frame
                self.current_timestamp = timestamp
                self.frame_count += 1
                
                # Calculate actual FPS every second
                elapsed = timestamp / 1000 - self.start_time
                if elapsed >= 1.0:
                    self.actual_fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.start_time = timestamp / 1000
            
            # Call frame callbacks
            for callback in self.frame_callbacks:
                try:
                    callback(frame, timestamp)
                except Exception as e:
                    print(f"Error in frame callback: {e}")
            
            # Limit frame rate if needed
            time.sleep(max(0, 1.0/self.fps - 0.01))
    
    def get_frame(self) -> Tuple[Optional[np.ndarray], float]:
        """
        Get the current frame and its timestamp.
        
        Returns:
            Tuple containing:
                - np.ndarray: Current frame or None if not available
                - float: Timestamp of the frame in milliseconds
        """
        with self.lock:
            if self.current_frame is None:
                return None, 0
            return self.current_frame.copy(), self.current_timestamp
    
    def add_frame_callback(self, callback: Callable[[np.ndarray, float], None]) -> None:
        """
        Add a callback function that will be called for each new frame.
        
        Args:
            callback: Function that takes frame and timestamp as arguments
        """
        self.frame_callbacks.append(callback)
    
    def remove_frame_callback(self, callback: Callable[[np.ndarray, float], None]) -> None:
        """
        Remove a previously added callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
    
    def get_camera_properties(self) -> Dict[str, Any]:
        """
        Get current camera properties.
        
        Returns:
            Dict containing camera properties
        """
        if self.cap is None:
            return {}
        
        return {
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "actual_fps": self.actual_fps,
            "camera_index": self.camera_index
        }
    
    def is_available(self) -> bool:
        """
        Check if the camera is available.
        
        Returns:
            bool: True if camera is available, False otherwise
        """
        if self.cap is not None and self.cap.isOpened():
            return True
        
        # Try to open the camera temporarily
        try:
            temp_cap = cv2.VideoCapture(self.camera_index)
            available = temp_cap.isOpened()
            temp_cap.release()
            return available
        except:
            return False
    
    def __del__(self):
        """Ensure resources are released when object is destroyed."""
        self.stop()


class VideoManager:
    """
    Manager class for handling multiple video capture instances.
    Provides a centralized interface for accessing different camera sources.
    """
    
    def __init__(self):
        """Initialize the video manager."""
        self.captures = {}
        self.default_camera_index = 0
    
    def get_capture(self, camera_index: int = None) -> VideoCapture:
        """
        Get a video capture instance for the specified camera index.
        Creates a new instance if one doesn't exist.
        
        Args:
            camera_index: Index of the camera to use, or None for default
        
        Returns:
            VideoCapture: Video capture instance
        """
        if camera_index is None:
            camera_index = self.default_camera_index
        
        if camera_index not in self.captures:
            self.captures[camera_index] = VideoCapture(camera_index=camera_index)
        
        return self.captures[camera_index]
    
    def start_all(self) -> None:
        """Start all video capture instances."""
        for capture in self.captures.values():
            capture.start()
    
    def stop_all(self) -> None:
        """Stop all video capture instances."""
        for capture in self.captures.values():
            capture.stop()
    
    def list_available_cameras(self) -> list:
        """
        List all available camera indices.
        
        Returns:
            list: List of available camera indices
        """
        available_cameras = []
        for i in range(10):  # Check first 10 camera indices
            try:
                temp_cap = cv2.VideoCapture(i)
                if temp_cap.isOpened():
                    available_cameras.append(i)
                temp_cap.release()
            except:
                pass
        
        return available_cameras
    
    def set_default_camera(self, camera_index: int) -> None:
        """
        Set the default camera index.
        
        Args:
            camera_index: Index of the camera to use as default
        """
        self.default_camera_index = camera_index
    
    def __del__(self):
        """Ensure all resources are released when object is destroyed."""
        self.stop_all()


# Global video manager instance
video_manager = VideoManager()

def get_video_manager() -> VideoManager:
    """
    Get the global video manager instance.
    
    Returns:
        VideoManager: Global video manager instance
    """
    return video_manager


if __name__ == "__main__":
    """Test the video capture functionality."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test video capture")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--width", type=int, default=640, help="Frame width")
    parser.add_argument("--height", type=int, default=480, help="Frame height")
    parser.add_argument("--fps", type=int, default=30, help="Target FPS")
    args = parser.parse_args()
    
    # Create and start video capture
    capture = VideoCapture(
        camera_index=args.camera,
        width=args.width,
        height=args.height,
        fps=args.fps
    )
    
    if not capture.start():
        print("Failed to start video capture")
        exit(1)
    
    try:
        print("Press ESC to exit")
        while True:
            frame, timestamp = capture.get_frame()
            if frame is not None:
                # Display camera properties and FPS
                props = capture.get_camera_properties()
                fps_text = f"FPS: {props.get('actual_fps', 0):.1f}"
                cv2.putText(frame, fps_text, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("Video Capture Test", frame)
                
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
    
    finally:
        capture.stop()
        cv2.destroyAllWindows()
