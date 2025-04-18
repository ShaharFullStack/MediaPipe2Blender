#!/usr/bin/env python3
"""
Data streaming module for MediaPipe to Blender live animation add-on.
This module handles real-time data streaming between MediaPipe and Blender.
"""

import zmq
import json
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Callable, Union
import pickle

# Import landmark detection module
from .landmark_detection import DetectionResult, get_mediapipe_processor


class DataStreamer:
    """
    Base class for data streaming.
    Provides common functionality for all streamer types.
    """
    
    def __init__(self):
        """Initialize the data streamer."""
        self.is_running = False
        self.thread = None
    
    def start(self) -> bool:
        """
        Start the data streamer.
        Must be implemented by subclasses.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        raise NotImplementedError("Subclasses must implement start()")
    
    def stop(self) -> None:
        """
        Stop the data streamer.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement stop()")
    
    def is_connected(self) -> bool:
        """
        Check if the streamer is connected.
        Must be implemented by subclasses.
        
        Returns:
            bool: True if connected, False otherwise
        """
        raise NotImplementedError("Subclasses must implement is_connected()")


class ZMQStreamer(DataStreamer):
    """
    ZeroMQ-based data streamer.
    Provides real-time data streaming using ZeroMQ sockets.
    """
    
    def __init__(
        self,
        mode: str = "server",
        host: str = "127.0.0.1",
        port: int = 5556,
        socket_type: str = "PUB",
        topic: str = "mediapipe"
    ):
        """
        Initialize the ZMQ streamer with specified parameters.
        
        Args:
            mode: "server" or "client"
            host: Host address
            port: Port number
            socket_type: ZMQ socket type ("PUB", "SUB", "REQ", "REP", "PUSH", "PULL")
            topic: Topic for PUB/SUB sockets
        """
        super().__init__()
        self.mode = mode
        self.host = host
        self.port = port
        self.socket_type = socket_type
        self.topic = topic
        
        self.context = None
        self.socket = None
        self.lock = threading.Lock()
        
        # Performance metrics
        self.message_count = 0
        self.start_time = 0
        self.message_times = []
        self.max_message_times = 30
        
        # Callbacks
        self.message_callbacks = []
    
    def start(self) -> bool:
        """
        Start the ZMQ streamer.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if self.is_running:
            return True
        
        try:
            # Initialize ZMQ context and socket
            self.context = zmq.Context()
            
            if self.socket_type == "PUB":
                self.socket = self.context.socket(zmq.PUB)
                if self.mode == "server":
                    self.socket.bind(f"tcp://{self.host}:{self.port}")
                else:
                    self.socket.connect(f"tcp://{self.host}:{self.port}")
            
            elif self.socket_type == "SUB":
                self.socket = self.context.socket(zmq.SUB)
                if self.mode == "server":
                    self.socket.bind(f"tcp://{self.host}:{self.port}")
                else:
                    self.socket.connect(f"tcp://{self.host}:{self.port}")
                self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
            
            elif self.socket_type == "REQ":
                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect(f"tcp://{self.host}:{self.port}")
            
            elif self.socket_type == "REP":
                self.socket = self.context.socket(zmq.REP)
                self.socket.bind(f"tcp://{self.host}:{self.port}")
            
            elif self.socket_type == "PUSH":
                self.socket = self.context.socket(zmq.PUSH)
                if self.mode == "server":
                    self.socket.bind(f"tcp://{self.host}:{self.port}")
                else:
                    self.socket.connect(f"tcp://{self.host}:{self.port}")
            
            elif self.socket_type == "PULL":
                self.socket = self.context.socket(zmq.PULL)
                if self.mode == "server":
                    self.socket.bind(f"tcp://{self.host}:{self.port}")
                else:
                    self.socket.connect(f"tcp://{self.host}:{self.port}")
            
            else:
                print(f"Unsupported socket type: {self.socket_type}")
                return False
            
            # Start thread for receiving messages if needed
            if self.socket_type in ["SUB", "REP", "PULL"]:
                self.is_running = True
                self.start_time = time.time()
                self.message_count = 0
                self.thread = threading.Thread(target=self._receive_loop)
                self.thread.daemon = True
                self.thread.start()
            else:
                self.is_running = True
                self.start_time = time.time()
                self.message_count = 0
            
            return True
        
        except Exception as e:
            print(f"Error starting ZMQ streamer: {e}")
            self._cleanup()
            return False
    
    def stop(self) -> None:
        """Stop the ZMQ streamer and release resources."""
        self.is_running = False
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up ZMQ resources."""
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        
        if self.context is not None:
            self.context.term()
            self.context = None
    
    def _receive_loop(self) -> None:
        """Main receive loop that runs in a separate thread."""
        while self.is_running:
            try:
                if self.socket_type == "SUB":
                    # For SUB sockets, use non-blocking receive with timeout
                    if self.socket.poll(100) == 0:  # 100ms timeout
                        continue
                    
                    topic, message = self.socket.recv_multipart()
                    topic = topic.decode('utf-8')
                    
                    # Process the message
                    self._process_message(message)
                
                elif self.socket_type == "REP":
                    # For REP sockets, receive request and send reply
                    message = self.socket.recv()
                    
                    # Process the message
                    reply = self._process_message(message)
                    
                    # Send reply
                    self.socket.send(reply if reply is not None else b'')
                
                elif self.socket_type == "PULL":
                    # For PULL sockets, use non-blocking receive with timeout
                    if self.socket.poll(100) == 0:  # 100ms timeout
                        continue
                    
                    message = self.socket.recv()
                    
                    # Process the message
                    self._process_message(message)
            
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    # Non-blocking receive timeout
                    time.sleep(0.01)
                else:
                    print(f"ZMQ error in receive loop: {e}")
                    time.sleep(0.1)
            
            except Exception as e:
                print(f"Error in receive loop: {e}")
                time.sleep(0.1)
    
    def _process_message(self, message: bytes) -> Optional[bytes]:
        """
        Process a received message.
        
        Args:
            message: Received message as bytes
            
        Returns:
            Optional[bytes]: Reply message for REP sockets, None otherwise
        """
        timestamp = time.time()
        
        try:
            # Try to deserialize the message
            data = pickle.loads(message)
            
            # Update performance metrics
            with self.lock:
                self.message_count += 1
                message_time = timestamp - self.start_time
                self.message_times.append(message_time)
                if len(self.message_times) > self.max_message_times:
                    self.message_times.pop(0)
            
            # Call message callbacks
            reply_data = None
            for callback in self.message_callbacks:
                try:
                    result = callback(data)
                    if result is not None:
                        reply_data = result
                except Exception as e:
                    print(f"Error in message callback: {e}")
            
            # Return reply for REP sockets
            if self.socket_type == "REP" and reply_data is not None:
                return pickle.dumps(reply_data)
            
            return None
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return None
    
    def send_message(self, data: Any) -> bool:
        """
        Send a message through the ZMQ socket.
        
        Args:
            data: Data to send
            
        Returns:
            bool: True if successfully sent, False otherwise
        """
        if not self.is_running or self.socket is None:
            return False
        
        try:
            # Serialize the data
            message = pickle.dumps(data)
            
            # Send the message
            if self.socket_type == "PUB":
                self.socket.send_multipart([self.topic.encode('utf-8'), message])
            elif self.socket_type in ["REQ", "PUSH"]:
                self.socket.send(message)
            else:
                print(f"Cannot send message with socket type: {self.socket_type}")
                return False
            
            # Update performance metrics
            with self.lock:
                self.message_count += 1
                message_time = time.time() - self.start_time
                self.message_times.append(message_time)
                if len(self.message_times) > self.max_message_times:
                    self.message_times.pop(0)
            
            return True
        
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def add_message_callback(self, callback: Callable[[Any], Optional[Any]]) -> None:
        """
        Add a callback function that will be called for each received message.
        
        Args:
            callback: Function that takes message data as argument and optionally returns reply data
        """
        self.message_callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable[[Any], Optional[Any]]) -> None:
        """
        Remove a previously added callback function.
        
        Args:
            callback: Function to remove
        """
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)
    
    def get_message_rate(self) -> float:
        """
        Get the current message rate in messages per second.
        
        Returns:
            float: Current message rate
        """
        with self.lock:
            elapsed = time.time() - self.start_time
            if elapsed <= 0:
                return 0.0
            return self.message_count / elapsed
    
    def is_connected(self) -> bool:
        """
        Check if the ZMQ socket is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.is_running and self.socket is not None
    
    def __del__(self):
        """Ensure resources are released when object is destroyed."""
        self.stop()


class MediaPipeStreamer:
    """
    MediaPipe data streamer.
    Streams MediaPipe detection results to Blender.
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5556,
        mode: str = "server",
        socket_type: str = "PUB",
        topic: str = "mediapipe"
    ):
        """
        Initialize the MediaPipe streamer with specified parameters.
        
        Args:
            host: Host address
            port: Port number
            mode: "server" or "client"
            socket_type: ZMQ socket type ("PUB", "PUSH", "REQ")
            topic: Topic for PUB/SUB sockets
        """
        self.host = host
        self.port = port
        self.mode = mode
        self.socket_type = socket_type
        self.topic = topic
        
        # Initialize ZMQ streamer
        self.streamer = ZMQStreamer(
            mode=mode,
            host=host,
            port=port,
            socket_type=socket_type,
            topic=topic
        )
        
        # Initialize MediaPipe processor
        self.processor = get_mediapipe_processor()
        
        # Processing state
        self.is_streaming = False
        self.frame_count = 0
        self.last_frame_time = 0
    
    def start(self) -> bool:
        """
        Start MediaPipe processing and data streaming.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if self.is_streaming:
            return True
        
        # Start ZMQ streamer
        if not self.streamer.start():
            print("Failed to start ZMQ streamer")
            return False
        
        # Set result callback for MediaPipe processor
        self.processor.set_result_callback(self._result_callback)
        
        # Start MediaPipe processor
        if not self.processor.start():
            print("Failed to start MediaPipe processor")
            self.streamer.stop()
            return False
        
        self.is_streaming = True
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        return True
    
    def stop(self) -> None:
        """Stop MediaPipe processing and data streaming."""
        if not self.is_streaming:
            return
        
        # Stop MediaPipe processor
        self.processor.set_result_callback(None)
        self.processor.stop()
        
        # Stop ZMQ streamer
        self.streamer.stop()
        
        self.is_streaming = False
    
    def _result_callback(self, result: DetectionResult) -> None:
        """
        Callback function for MediaPipe detection results.
        
        Args:
            result: MediaPipe detection result
        """
        # Convert result to serializable format
        data = self._convert_result_to_dict(result)
        
        # Send data through ZMQ streamer
        self.streamer.send_message(data)
        
        # Update state
        self.frame_count += 1
        self.last_frame_time = time.time()
    
    def _convert_result_to_dict(self, result: DetectionResult) -> Dict[str, Any]:
        """
        Convert DetectionResult to a serializable dictionary.
        
        Args:
            result: MediaPipe detection result
            
        Returns:
            Dict[str, Any]: Serializable dictionary
        """
        # Convert faces
        faces = []
        for face in result.faces:
            face_dict = {
                'landmarks': face.landmarks,
                'visibility': face.visibility,
                'timestamp': face.timestamp,
      
(Content truncated due to size limit. Use line ranges to read in chunks)