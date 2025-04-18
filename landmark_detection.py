#!/usr/bin/env python3
"""
MediaPipe landmark detection module for MediaPipe to Blender live animation add-on.
This module handles detection of face, hand, and body landmarks using MediaPipe.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field

# Import video capture module
from .video_capture import VideoCapture, get_video_manager


@dataclass
class LandmarkData:
    """Data class for storing landmark information."""
    landmarks: List[Dict[str, float]]  # List of landmarks with x, y, z coordinates
    world_landmarks: Optional[List[Dict[str, float]]] = None  # 3D world landmarks if available
    visibility: Optional[List[float]] = None  # Visibility scores for landmarks
    timestamp: float = 0.0  # Timestamp in milliseconds
    detection_confidence: float = 0.0  # Confidence score for the detection
    tracking_id: Optional[int] = None  # Tracking ID for the detection


@dataclass
class FaceData(LandmarkData):
    """Data class for storing face landmark information."""
    blendshapes: Optional[List[Dict[str, float]]] = None  # Facial expression blendshapes


@dataclass
class HandData(LandmarkData):
    """Data class for storing hand landmark information."""
    handedness: str = "UNKNOWN"  # LEFT or RIGHT
    hand_flag: int = 0  # 0 for left, 1 for right


@dataclass
class PoseData(LandmarkData):
    """Data class for storing pose landmark information."""
    segmentation_mask: Optional[np.ndarray] = None  # Segmentation mask if available


@dataclass
class DetectionResult:
    """Data class for storing detection results from all MediaPipe models."""
    faces: List[FaceData] = field(default_factory=list)
    hands: List[HandData] = field(default_factory=list)
    pose: List[PoseData] = field(default_factory=list)
    frame_timestamp: float = 0.0
    frame_index: int = 0
    source_dimensions: Tuple[int, int] = (0, 0)  # (width, height)


class MediaPipeDetector:
    """
    Base class for MediaPipe detectors.
    Provides common functionality for all detector types.
    """
    
    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        """
        Initialize the detector with specified parameters.
        
        Args:
            min_detection_confidence: Minimum confidence for detection to be considered successful
            min_tracking_confidence: Minimum confidence for tracking to be considered successful
        """
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.detector = None
        self.is_initialized = False
        
        # Performance metrics
        self.process_times = []
        self.max_process_times = 30  # Keep track of last 30 processing times
        
        # Drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
    
    def initialize(self) -> bool:
        """
        Initialize the detector.
        Must be implemented by subclasses.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement initialize()")
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: float) -> Any:
        """
        Process a frame with the detector.
        Must be implemented by subclasses.
        
        Args:
            frame: Input frame as numpy array
            timestamp_ms: Timestamp of the frame in milliseconds
            
        Returns:
            Any: Detection results
        """
        raise NotImplementedError("Subclasses must implement process_frame()")
    
    def draw_landmarks(self, frame: np.ndarray, results: Any) -> np.ndarray:
        """
        Draw landmarks on the frame.
        Must be implemented by subclasses.
        
        Args:
            frame: Input frame as numpy array
            results: Detection results from process_frame()
            
        Returns:
            np.ndarray: Frame with landmarks drawn
        """
        raise NotImplementedError("Subclasses must implement draw_landmarks()")
    
    def get_average_process_time(self) -> float:
        """
        Get the average processing time in milliseconds.
        
        Returns:
            float: Average processing time in milliseconds
        """
        if not self.process_times:
            return 0.0
        return sum(self.process_times) / len(self.process_times)
    
    def close(self) -> None:
        """Release resources used by the detector."""
        if hasattr(self, 'detector') and self.detector is not None:
            if hasattr(self.detector, 'close'):
                self.detector.close()
            self.detector = None
        self.is_initialized = False


class FaceDetector(MediaPipeDetector):
    """
    MediaPipe face landmark detector.
    Detects facial landmarks and expressions.
    """
    
    def __init__(
        self, 
        min_detection_confidence: float = 0.5, 
        min_tracking_confidence: float = 0.5,
        max_num_faces: int = 1,
        output_face_blendshapes: bool = True,
        refine_landmarks: bool = True
    ):
        """
        Initialize the face detector with specified parameters.
        
        Args:
            min_detection_confidence: Minimum confidence for detection to be considered successful
            min_tracking_confidence: Minimum confidence for tracking to be considered successful
            max_num_faces: Maximum number of faces to detect
            output_face_blendshapes: Whether to output face blendshapes
            refine_landmarks: Whether to refine landmarks (includes eye and lip landmarks)
        """
        super().__init__(min_detection_confidence, min_tracking_confidence)
        self.max_num_faces = max_num_faces
        self.output_face_blendshapes = output_face_blendshapes
        self.refine_landmarks = refine_landmarks
        
        # MediaPipe face mesh solution
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def initialize(self) -> bool:
        """
        Initialize the face detector.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.detector = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=self.max_num_faces,
                refine_landmarks=self.refine_landmarks,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing face detector: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: float) -> List[FaceData]:
        """
        Process a frame with the face detector.
        
        Args:
            frame: Input frame as numpy array
            timestamp_ms: Timestamp of the frame in milliseconds
            
        Returns:
            List[FaceData]: List of detected faces with landmarks
        """
        if not self.is_initialized:
            if not self.initialize():
                return []
        
        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        start_time = time.time()
        results = self.detector.process(image_rgb)
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Update process times
        self.process_times.append(process_time)
        if len(self.process_times) > self.max_process_times:
            self.process_times.pop(0)
        
        # Extract face landmarks
        face_data_list = []
        
        if results.multi_face_landmarks:
            for i, face_landmarks in enumerate(results.multi_face_landmarks):
                # Convert landmarks to a list of dictionaries
                landmarks = []
                for landmark in face_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': getattr(landmark, 'visibility', 1.0)
                    })
                
                # Extract visibility scores
                visibility = [lm.get('visibility', 1.0) for lm in landmarks]
                
                # Create face data
                face_data = FaceData(
                    landmarks=landmarks,
                    visibility=visibility,
                    timestamp=timestamp_ms,
                    detection_confidence=1.0,  # Face mesh doesn't provide confidence scores
                    tracking_id=i
                )
                
                # Add blendshapes if available
                if self.output_face_blendshapes and hasattr(results, 'face_blendshapes') and results.face_blendshapes:
                    if i < len(results.face_blendshapes):
                        blendshapes = []
                        for blendshape in results.face_blendshapes[i].categories:
                            blendshapes.append({
                                'name': blendshape.category_name,
                                'score': blendshape.score
                            })
                        face_data.blendshapes = blendshapes
                
                face_data_list.append(face_data)
        
        return face_data_list
    
    def draw_landmarks(self, frame: np.ndarray, results: List[FaceData]) -> np.ndarray:
        """
        Draw face landmarks on the frame.
        
        Args:
            frame: Input frame as numpy array
            results: List of FaceData objects
            
        Returns:
            np.ndarray: Frame with landmarks drawn
        """
        if not results:
            return frame
        
        # Create a copy of the frame
        annotated_frame = frame.copy()
        
        for face_data in results:
            # Convert landmarks to MediaPipe format
            face_landmarks_proto = self._convert_to_landmark_proto(face_data.landmarks)
            
            # Draw the face mesh
            self.mp_drawing.draw_landmarks(
                image=annotated_frame,
                landmark_list=face_landmarks_proto,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            
            # Draw the face contours
            self.mp_drawing.draw_landmarks(
                image=annotated_frame,
                landmark_list=face_landmarks_proto,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            
            # Draw the irises if refined landmarks are enabled
            if self.refine_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=annotated_frame,
                    landmark_list=face_landmarks_proto,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                )
        
        return annotated_frame
    
    def _convert_to_landmark_proto(self, landmarks: List[Dict[str, float]]) -> Any:
        """
        Convert landmarks from our format to MediaPipe's format.
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            Any: MediaPipe landmark protocol buffer
        """
        landmark_list = mp.framework.formats.landmark_pb2.NormalizedLandmarkList()
        for lm in landmarks:
            landmark = landmark_list.landmark.add()
            landmark.x = lm['x']
            landmark.y = lm['y']
            landmark.z = lm['z']
            if 'visibility' in lm:
                landmark.visibility = lm['visibility']
        
        return landmark_list


class HandDetector(MediaPipeDetector):
    """
    MediaPipe hand landmark detector.
    Detects hand landmarks and handedness.
    """
    
    def __init__(
        self, 
        min_detection_confidence: float = 0.5, 
        min_tracking_confidence: float = 0.5,
        max_num_hands: int = 2,
        model_complexity: int = 1
    ):
        """
        Initialize the hand detector with specified parameters.
        
        Args:
            min_detection_confidence: Minimum confidence for detection to be considered successful
            min_tracking_confidence: Minimum confidence for tracking to be considered successful
            max_num_hands: Maximum number of hands to detect
            model_complexity: Model complexity (0, 1, or 2)
        """
        super().__init__(min_detection_confidence, min_tracking_confidence)
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        
        # MediaPipe hands solution
        self.mp_hands = mp.solutions.hands
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def initialize(self) -> bool:
        """
        Initialize the hand detector.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self.max_num_hands,
                model_complexity=self.model_complexity,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing hand detector: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: float) -> List[HandData]:
        """
        Process a frame with the hand detector.
        
        Args:
            frame: Input frame as numpy array
            timestamp_ms: Timestamp of the frame in milliseconds
            
        Returns:
            List[HandData]: List of detected hands with landmarks
        """
        if not self.is_initialized:
            if not self.initialize():
                return []
        
        # Convert the image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        start_time = time.time()
        results = self.detector.process(image_rgb)
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Update process times
        self.process_times.append(process_time)
        if len(self.process_times) > self.max_process_times:
            self.process_times.pop(0)
        
        # Extract hand landmarks
        hand_data_list = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for i, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                # Convert landmarks to a list of dictionaries
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                
              
(Content truncated due to size limit. Use line ranges to read in chunks)