"""
MediaPipe Motion Capture - Animation Module
This module handles animation updates and keyframing for the Blender add-on.
"""

import bpy
import time
import threading
import math
from mathutils import Vector, Matrix, Quaternion, Euler
from typing import Dict, List, Tuple, Optional, Any, Union

# Import landmark mapping module
from . import landmark_mapping

class AnimationProcessor:
    """
    Class for processing animation data from MediaPipe.
    Handles smoothing, keyframing, and animation updates.
    """
    
    def __init__(self, armature=None, mapper=None):
        """
        Initialize the animation processor.
        
        Args:
            armature: Blender armature object
            mapper: LandmarkMapper instance
        """
        self.armature = armature
        self.mapper = mapper if mapper is not None else landmark_mapping.LandmarkMapper(armature)
        
        # Animation settings
        self.auto_keyframe = True
        self.keyframe_interval = 1
        self.smoothing = 0.5
        self.scale_factor = 1.0
        
        # Influence factors
        self.face_influence = 1.0
        self.hands_influence = 1.0
        self.pose_influence = 1.0
        
        # Animation state
        self.is_recording = False
        self.frame_count = 0
        self.last_keyframe = 0
        self.start_time = 0
        self.previous_data = None
        
        # Smoothing buffers
        self.position_buffer = {}
        self.rotation_buffer = {}
        self.buffer_size = 5  # Number of frames to buffer for smoothing
    
    def set_armature(self, armature):
        """
        Set the target armature.
        
        Args:
            armature: Blender armature object
        """
        self.armature = armature
        self.mapper.set_armature(armature)
        
        # Clear buffers
        self.position_buffer = {}
        self.rotation_buffer = {}
    
    def set_mapper(self, mapper):
        """
        Set the landmark mapper.
        
        Args:
            mapper: LandmarkMapper instance
        """
        self.mapper = mapper
        
        # Clear buffers
        self.position_buffer = {}
        self.rotation_buffer = {}
    
    def start_recording(self):
        """Start animation recording."""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.frame_count = 0
        self.last_keyframe = 0
        self.start_time = time.time()
        self.previous_data = None
        
        # Clear buffers
        self.position_buffer = {}
        self.rotation_buffer = {}
    
    def stop_recording(self):
        """Stop animation recording."""
        self.is_recording = False
    
    def process_frame(self, data):
        """
        Process a frame of MediaPipe data.
        
        Args:
            data: MediaPipe data dictionary
            
        Returns:
            bool: True if frame was processed successfully, False otherwise
        """
        if not self.is_recording or self.armature is None or data is None:
            return False
        
        # Increment frame count
        self.frame_count += 1
        
        # Apply smoothing if enabled
        if self.smoothing > 0:
            data = self.apply_smoothing(data)
        
        # Update armature
        self.update_armature(data)
        
        # Insert keyframes if needed
        if self.auto_keyframe and self.frame_count - self.last_keyframe >= self.keyframe_interval:
            self.insert_keyframes()
            self.last_keyframe = self.frame_count
        
        # Store data for next frame
        self.previous_data = data
        
        return True
    
    def apply_smoothing(self, data):
        """
        Apply smoothing to MediaPipe data.
        
        Args:
            data: MediaPipe data dictionary
            
        Returns:
            dict: Smoothed data dictionary
        """
        # If no previous data, return current data
        if self.previous_data is None:
            return data
        
        # Create a copy of the data
        smoothed_data = {
            'faces': [],
            'hands': [],
            'pose': [],
            'frame_timestamp': data.get('frame_timestamp', 0),
            'frame_index': data.get('frame_index', 0),
            'source_dimensions': data.get('source_dimensions', (0, 0))
        }
        
        # Smooth face data
        if 'faces' in data and 'faces' in self.previous_data:
            for i, face in enumerate(data['faces']):
                if i < len(self.previous_data['faces']):
                    prev_face = self.previous_data['faces'][i]
                    smoothed_face = self.smooth_landmarks(face, prev_face, 'face', i)
                    smoothed_data['faces'].append(smoothed_face)
                else:
                    smoothed_data['faces'].append(face)
        
        # Smooth hand data
        if 'hands' in data and 'hands' in self.previous_data:
            for i, hand in enumerate(data['hands']):
                # Find matching hand in previous data
                prev_hand = None
                for ph in self.previous_data['hands']:
                    if ph.get('handedness') == hand.get('handedness'):
                        prev_hand = ph
                        break
                
                if prev_hand is not None:
                    smoothed_hand = self.smooth_landmarks(hand, prev_hand, 'hand', i)
                    smoothed_data['hands'].append(smoothed_hand)
                else:
                    smoothed_data['hands'].append(hand)
        
        # Smooth pose data
        if 'pose' in data and 'pose' in self.previous_data:
            for i, pose in enumerate(data['pose']):
                if i < len(self.previous_data['pose']):
                    prev_pose = self.previous_data['pose'][i]
                    smoothed_pose = self.smooth_landmarks(pose, prev_pose, 'pose', i)
                    smoothed_data['pose'].append(smoothed_pose)
                else:
                    smoothed_data['pose'].append(pose)
        
        return smoothed_data
    
    def smooth_landmarks(self, current, previous, landmark_type, index):
        """
        Smooth landmarks between frames.
        
        Args:
            current: Current landmark data
            previous: Previous landmark data
            landmark_type: Type of landmark ('face', 'hand', 'pose')
            index: Index of the landmark set
            
        Returns:
            dict: Smoothed landmark data
        """
        # Create a copy of the current data
        smoothed = current.copy()
        
        # Smooth landmarks
        if 'landmarks' in current and 'landmarks' in previous:
            smoothed_landmarks = []
            
            for i, lm in enumerate(current['landmarks']):
                if i < len(previous['landmarks']):
                    prev_lm = previous['landmarks'][i]
                    
                    # Get buffer key
                    buffer_key = f"{landmark_type}_{index}_{i}"
                    
                    # Initialize buffer if needed
                    if buffer_key not in self.position_buffer:
                        self.position_buffer[buffer_key] = []
                    
                    # Add current position to buffer
                    self.position_buffer[buffer_key].append(Vector((lm['x'], lm['y'], lm['z'])))
                    
                    # Limit buffer size
                    if len(self.position_buffer[buffer_key]) > self.buffer_size:
                        self.position_buffer[buffer_key].pop(0)
                    
                    # Calculate smoothed position
                    smoothed_pos = Vector((0, 0, 0))
                    weights = 0
                    
                    for j, pos in enumerate(self.position_buffer[buffer_key]):
                        weight = (j + 1) / len(self.position_buffer[buffer_key])
                        smoothed_pos += pos * weight
                        weights += weight
                    
                    if weights > 0:
                        smoothed_pos /= weights
                    
                    # Apply smoothing factor
                    final_pos = Vector((lm['x'], lm['y'], lm['z'])).lerp(smoothed_pos, self.smoothing)
                    
                    # Create smoothed landmark
                    smoothed_lm = {
                        'x': final_pos.x,
                        'y': final_pos.y,
                        'z': final_pos.z
                    }
                    
                    # Copy additional properties
                    for key, value in lm.items():
                        if key not in ['x', 'y', 'z']:
                            smoothed_lm[key] = value
                    
                    smoothed_landmarks.append(smoothed_lm)
                else:
                    smoothed_landmarks.append(lm)
            
            smoothed['landmarks'] = smoothed_landmarks
        
        # Smooth world landmarks if available
        if 'world_landmarks' in current and 'world_landmarks' in previous:
            smoothed_world_landmarks = []
            
            for i, lm in enumerate(current['world_landmarks']):
                if i < len(previous['world_landmarks']):
                    prev_lm = previous['world_landmarks'][i]
                    
                    # Get buffer key
                    buffer_key = f"{landmark_type}_{index}_{i}_world"
                    
                    # Initialize buffer if needed
                    if buffer_key not in self.position_buffer:
                        self.position_buffer[buffer_key] = []
                    
                    # Add current position to buffer
                    self.position_buffer[buffer_key].append(Vector((lm['x'], lm['y'], lm['z'])))
                    
                    # Limit buffer size
                    if len(self.position_buffer[buffer_key]) > self.buffer_size:
                        self.position_buffer[buffer_key].pop(0)
                    
                    # Calculate smoothed position
                    smoothed_pos = Vector((0, 0, 0))
                    weights = 0
                    
                    for j, pos in enumerate(self.position_buffer[buffer_key]):
                        weight = (j + 1) / len(self.position_buffer[buffer_key])
                        smoothed_pos += pos * weight
                        weights += weight
                    
                    if weights > 0:
                        smoothed_pos /= weights
                    
                    # Apply smoothing factor
                    final_pos = Vector((lm['x'], lm['y'], lm['z'])).lerp(smoothed_pos, self.smoothing)
                    
                    # Create smoothed landmark
                    smoothed_lm = {
                        'x': final_pos.x,
                        'y': final_pos.y,
                        'z': final_pos.z
                    }
                    
                    # Copy additional properties
                    for key, value in lm.items():
                        if key not in ['x', 'y', 'z']:
                            smoothed_lm[key] = value
                    
                    smoothed_world_landmarks.append(smoothed_lm)
                else:
                    smoothed_world_landmarks.append(lm)
            
            smoothed['world_landmarks'] = smoothed_world_landmarks
        
        return smoothed
    
    def update_armature(self, data):
        """
        Update armature based on MediaPipe data.
        
        Args:
            data: MediaPipe data dictionary
            
        Returns:
            int: Number of bones updated
        """
        if self.armature is None or self.mapper is None:
            return 0
        
        # Get bone mapping
        bone_mapping = self.mapper.get_bone_mapping()
        if not bone_mapping:
            return 0
        
        # Update bones based on landmark type
        updated_bones = 0
        
        for bone_name in bone_mapping.keys():
            bone_name_lower = bone_name.lower()
            
            # Determine influence factor based on bone name
            influence = 1.0
            
            # Face bones
            if any(part in bone_name_lower for part in ['face', 'head', 'jaw', 'eye', 'brow', 'lip', 'tongue']):
                influence = self.face_influence
            
            # Hand bones
            elif any(part in bone_name_lower for part in ['hand', 'finger', 'thumb', 'index', 'middle', 'ring', 'pinky']):
                influence = self.hands_influence
            
            # Body bones
            else:
                influence = self.pose_influence
            
            # Update bone transform
            if self.mapper.update_bone_transform(data, bone_name, influence, self.scale_factor):
                updated_bones += 1
        
        return updated_bones
    
    def insert_keyframes(self, frame=None):
        """
        Insert keyframes for all mapped bones.
        
        Args:
            frame: Frame number (None for current frame)
            
        Returns:
            int: Number of bones keyframed
        """
        if self.armature is None or self.mapper is None:
            return 0
        
        # Use current frame if none specified
        if frame is None:
            frame = bpy.context.scene.frame_current
        
        # Insert keyframes
        return self.mapper.insert_keyframes(frame)
    
    def get_fps(self):
        """
        Get the current animation FPS.
        
        Returns:
            float: Frames per second
        """
        if not self.is_recording or self.start_time == 0:
            return 0.0
        
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        
        return self.frame_count / elapsed

# Global animation processor instance
animation_processor = None

def get_animation_processor():
    """
    Get the global animation processor instance.
    Creates a new instance if one doesn't exist.
    
    Returns:
        AnimationProcessor: Global animation processor instance
    """
    global animation_processor
    if animation_processor is None:
        animation_processor = AnimationProcessor()
    return animation_processor
