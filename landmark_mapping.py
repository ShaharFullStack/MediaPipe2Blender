"""
MediaPipe Motion Capture - Landmark Mapping Module
This module handles mapping between MediaPipe landmarks and Blender armature bones.
"""

import bpy
import math
import mathutils
from mathutils import Vector, Matrix, Quaternion, Euler
from typing import Dict, List, Tuple, Optional, Any, Union

# MediaPipe landmark indices
# Face landmark indices (468 total)
FACE_CONTOUR = list(range(0, 17))  # Face oval
FACE_EYEBROW_LEFT = list(range(17, 22))  # Left eyebrow
FACE_EYEBROW_RIGHT = list(range(22, 27))  # Right eyebrow
FACE_NOSE = list(range(27, 36))  # Nose bridge and tip
FACE_EYE_LEFT = list(range(36, 42))  # Left eye
FACE_EYE_RIGHT = list(range(42, 48))  # Right eye
FACE_LIPS_OUTER = list(range(48, 60))  # Outer lips
FACE_LIPS_INNER = list(range(60, 68))  # Inner lips

# Hand landmark indices (21 per hand)
HAND_WRIST = 0
HAND_THUMB_CMC = 1
HAND_THUMB_MCP = 2
HAND_THUMB_IP = 3
HAND_THUMB_TIP = 4
HAND_INDEX_MCP = 5
HAND_INDEX_PIP = 6
HAND_INDEX_DIP = 7
HAND_INDEX_TIP = 8
HAND_MIDDLE_MCP = 9
HAND_MIDDLE_PIP = 10
HAND_MIDDLE_DIP = 11
HAND_MIDDLE_TIP = 12
HAND_RING_MCP = 13
HAND_RING_PIP = 14
HAND_RING_DIP = 15
HAND_RING_TIP = 16
HAND_PINKY_MCP = 17
HAND_PINKY_PIP = 18
HAND_PINKY_DIP = 19
HAND_PINKY_TIP = 20

# Pose landmark indices (33 total)
POSE_NOSE = 0
POSE_LEFT_EYE_INNER = 1
POSE_LEFT_EYE = 2
POSE_LEFT_EYE_OUTER = 3
POSE_RIGHT_EYE_INNER = 4
POSE_RIGHT_EYE = 5
POSE_RIGHT_EYE_OUTER = 6
POSE_LEFT_EAR = 7
POSE_RIGHT_EAR = 8
POSE_MOUTH_LEFT = 9
POSE_MOUTH_RIGHT = 10
POSE_LEFT_SHOULDER = 11
POSE_RIGHT_SHOULDER = 12
POSE_LEFT_ELBOW = 13
POSE_RIGHT_ELBOW = 14
POSE_LEFT_WRIST = 15
POSE_RIGHT_WRIST = 16
POSE_LEFT_PINKY = 17
POSE_RIGHT_PINKY = 18
POSE_LEFT_INDEX = 19
POSE_RIGHT_INDEX = 20
POSE_LEFT_THUMB = 21
POSE_RIGHT_THUMB = 22
POSE_LEFT_HIP = 23
POSE_RIGHT_HIP = 24
POSE_LEFT_KNEE = 25
POSE_RIGHT_KNEE = 26
POSE_LEFT_ANKLE = 27
POSE_RIGHT_ANKLE = 28
POSE_LEFT_HEEL = 29
POSE_RIGHT_HEEL = 30
POSE_LEFT_FOOT_INDEX = 31
POSE_RIGHT_FOOT_INDEX = 32

# Mapping presets
RIGIFY_MAPPING = {
    # Face mapping
    "face.jaw": [FACE_LIPS_OUTER[0], FACE_LIPS_OUTER[6]],  # Jaw bone maps to middle of lower lip
    "face.tongue": [FACE_LIPS_INNER[3], FACE_LIPS_INNER[7]],  # Tongue bone maps to middle of inner lips
    "face.lip.T.L": [FACE_LIPS_OUTER[3]],  # Upper lip left
    "face.lip.T.R": [FACE_LIPS_OUTER[9]],  # Upper lip right
    "face.lip.B.L": [FACE_LIPS_OUTER[1]],  # Lower lip left
    "face.lip.B.R": [FACE_LIPS_OUTER[11]],  # Lower lip right
    "face.eyelid.T.L": [FACE_EYE_LEFT[1]],  # Upper eyelid left
    "face.eyelid.T.R": [FACE_EYE_RIGHT[1]],  # Upper eyelid right
    "face.eyelid.B.L": [FACE_EYE_LEFT[4]],  # Lower eyelid left
    "face.eyelid.B.R": [FACE_EYE_RIGHT[4]],  # Lower eyelid right
    "face.eyebrow.T.L": [FACE_EYEBROW_LEFT[2]],  # Eyebrow left
    "face.eyebrow.T.R": [FACE_EYEBROW_RIGHT[2]],  # Eyebrow right
    
    # Hand mapping (left)
    "hand.L": [POSE_LEFT_WRIST],  # Left hand/wrist
    "thumb.01.L": [HAND_THUMB_CMC],  # Left thumb base
    "thumb.02.L": [HAND_THUMB_MCP],  # Left thumb middle
    "thumb.03.L": [HAND_THUMB_IP],  # Left thumb tip
    "f_index.01.L": [HAND_INDEX_MCP],  # Left index finger base
    "f_index.02.L": [HAND_INDEX_PIP],  # Left index finger middle
    "f_index.03.L": [HAND_INDEX_DIP],  # Left index finger tip
    "f_middle.01.L": [HAND_MIDDLE_MCP],  # Left middle finger base
    "f_middle.02.L": [HAND_MIDDLE_PIP],  # Left middle finger middle
    "f_middle.03.L": [HAND_MIDDLE_DIP],  # Left middle finger tip
    "f_ring.01.L": [HAND_RING_MCP],  # Left ring finger base
    "f_ring.02.L": [HAND_RING_PIP],  # Left ring finger middle
    "f_ring.03.L": [HAND_RING_DIP],  # Left ring finger tip
    "f_pinky.01.L": [HAND_PINKY_MCP],  # Left pinky finger base
    "f_pinky.02.L": [HAND_PINKY_PIP],  # Left pinky finger middle
    "f_pinky.03.L": [HAND_PINKY_DIP],  # Left pinky finger tip
    
    # Hand mapping (right)
    "hand.R": [POSE_RIGHT_WRIST],  # Right hand/wrist
    "thumb.01.R": [HAND_THUMB_CMC],  # Right thumb base
    "thumb.02.R": [HAND_THUMB_MCP],  # Right thumb middle
    "thumb.03.R": [HAND_THUMB_IP],  # Right thumb tip
    "f_index.01.R": [HAND_INDEX_MCP],  # Right index finger base
    "f_index.02.R": [HAND_INDEX_PIP],  # Right index finger middle
    "f_index.03.R": [HAND_INDEX_DIP],  # Right index finger tip
    "f_middle.01.R": [HAND_MIDDLE_MCP],  # Right middle finger base
    "f_middle.02.R": [HAND_MIDDLE_PIP],  # Right middle finger middle
    "f_middle.03.R": [HAND_MIDDLE_DIP],  # Right middle finger tip
    "f_ring.01.R": [HAND_RING_MCP],  # Right ring finger base
    "f_ring.02.R": [HAND_RING_PIP],  # Right ring finger middle
    "f_ring.03.R": [HAND_RING_DIP],  # Right ring finger tip
    "f_pinky.01.R": [HAND_PINKY_MCP],  # Right pinky finger base
    "f_pinky.02.R": [HAND_PINKY_PIP],  # Right pinky finger middle
    "f_pinky.03.R": [HAND_PINKY_DIP],  # Right pinky finger tip
    
    # Body mapping
    "spine": [POSE_LEFT_HIP, POSE_RIGHT_HIP],  # Spine base (between hips)
    "spine.001": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Spine middle (between shoulders)
    "spine.002": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Chest
    "spine.003": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Upper chest
    "spine.004": [POSE_NOSE],  # Neck
    "spine.005": [POSE_NOSE],  # Head
    "spine.006": [POSE_NOSE],  # Head top
    "shoulder.L": [POSE_LEFT_SHOULDER],  # Left shoulder
    "shoulder.R": [POSE_RIGHT_SHOULDER],  # Right shoulder
    "upper_arm.L": [POSE_LEFT_SHOULDER, POSE_LEFT_ELBOW],  # Left upper arm
    "upper_arm.R": [POSE_RIGHT_SHOULDER, POSE_RIGHT_ELBOW],  # Right upper arm
    "forearm.L": [POSE_LEFT_ELBOW, POSE_LEFT_WRIST],  # Left forearm
    "forearm.R": [POSE_RIGHT_ELBOW, POSE_RIGHT_WRIST],  # Right forearm
    "thigh.L": [POSE_LEFT_HIP, POSE_LEFT_KNEE],  # Left thigh
    "thigh.R": [POSE_RIGHT_HIP, POSE_RIGHT_KNEE],  # Right thigh
    "shin.L": [POSE_LEFT_KNEE, POSE_LEFT_ANKLE],  # Left shin
    "shin.R": [POSE_RIGHT_KNEE, POSE_RIGHT_ANKLE],  # Right shin
    "foot.L": [POSE_LEFT_ANKLE, POSE_LEFT_FOOT_INDEX],  # Left foot
    "foot.R": [POSE_RIGHT_ANKLE, POSE_RIGHT_FOOT_INDEX],  # Right foot
    "toe.L": [POSE_LEFT_FOOT_INDEX],  # Left toe
    "toe.R": [POSE_RIGHT_FOOT_INDEX],  # Right toe
}

MIXAMO_MAPPING = {
    # Face mapping
    "Head": [POSE_NOSE],  # Head
    "Neck": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Neck
    
    # Hand mapping (left)
    "LeftHand": [POSE_LEFT_WRIST],  # Left hand/wrist
    "LeftHandThumb1": [HAND_THUMB_CMC],  # Left thumb base
    "LeftHandThumb2": [HAND_THUMB_MCP],  # Left thumb middle
    "LeftHandThumb3": [HAND_THUMB_IP],  # Left thumb tip
    "LeftHandIndex1": [HAND_INDEX_MCP],  # Left index finger base
    "LeftHandIndex2": [HAND_INDEX_PIP],  # Left index finger middle
    "LeftHandIndex3": [HAND_INDEX_DIP],  # Left index finger tip
    "LeftHandMiddle1": [HAND_MIDDLE_MCP],  # Left middle finger base
    "LeftHandMiddle2": [HAND_MIDDLE_PIP],  # Left middle finger middle
    "LeftHandMiddle3": [HAND_MIDDLE_DIP],  # Left middle finger tip
    "LeftHandRing1": [HAND_RING_MCP],  # Left ring finger base
    "LeftHandRing2": [HAND_RING_PIP],  # Left ring finger middle
    "LeftHandRing3": [HAND_RING_DIP],  # Left ring finger tip
    "LeftHandPinky1": [HAND_PINKY_MCP],  # Left pinky finger base
    "LeftHandPinky2": [HAND_PINKY_PIP],  # Left pinky finger middle
    "LeftHandPinky3": [HAND_PINKY_DIP],  # Left pinky finger tip
    
    # Hand mapping (right)
    "RightHand": [POSE_RIGHT_WRIST],  # Right hand/wrist
    "RightHandThumb1": [HAND_THUMB_CMC],  # Right thumb base
    "RightHandThumb2": [HAND_THUMB_MCP],  # Right thumb middle
    "RightHandThumb3": [HAND_THUMB_IP],  # Right thumb tip
    "RightHandIndex1": [HAND_INDEX_MCP],  # Right index finger base
    "RightHandIndex2": [HAND_INDEX_PIP],  # Right index finger middle
    "RightHandIndex3": [HAND_INDEX_DIP],  # Right index finger tip
    "RightHandMiddle1": [HAND_MIDDLE_MCP],  # Right middle finger base
    "RightHandMiddle2": [HAND_MIDDLE_PIP],  # Right middle finger middle
    "RightHandMiddle3": [HAND_MIDDLE_DIP],  # Right middle finger tip
    "RightHandRing1": [HAND_RING_MCP],  # Right ring finger base
    "RightHandRing2": [HAND_RING_PIP],  # Right ring finger middle
    "RightHandRing3": [HAND_RING_DIP],  # Right ring finger tip
    "RightHandPinky1": [HAND_PINKY_MCP],  # Right pinky finger base
    "RightHandPinky2": [HAND_PINKY_PIP],  # Right pinky finger middle
    "RightHandPinky3": [HAND_PINKY_DIP],  # Right pinky finger tip
    
    # Body mapping
    "Hips": [POSE_LEFT_HIP, POSE_RIGHT_HIP],  # Hips
    "Spine": [POSE_LEFT_HIP, POSE_RIGHT_HIP, POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Spine
    "Spine1": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Spine1
    "Spine2": [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],  # Spine2
    "LeftShoulder": [POSE_LEFT_SHOULDER],  # Left shoulder
    "RightShoulder": [POSE_RIGHT_SHOULDER],  # Right shoulder
    "LeftArm": [POSE_LEFT_SHOULDER, POSE_LEFT_ELBOW],  # Left upper arm
    "RightArm": [POSE_RIGHT_SHOULDER, POSE_RIGHT_ELBOW],  # Right upper arm
    "LeftForeArm": [POSE_LEFT_ELBOW, POSE_LEFT_WRIST],  # Left forearm
    "RightForeArm": [POSE_RIGHT_ELBOW, POSE_RIGHT_WRIST],  # Right forearm
    "LeftUpLeg": [POSE_LEFT_HIP, POSE_LEFT_KNEE],  # Left thigh
    "RightUpLeg": [POSE_RIGHT_HIP, POSE_RIGHT_KNEE],  # Right thigh
    "LeftLeg": [POSE_LEFT_KNEE, POSE_LEFT_ANKLE],  # Left shin
    "RightLeg": [POSE_RIGHT_KNEE, POSE_RIGHT_ANKLE],  # Right shin
    "LeftFoot": [POSE_LEFT_ANKLE, POSE_LEFT_FOOT_INDEX],  # Left foot
    "RightFoot": [POSE_RIGHT_ANKLE, POSE_RIGHT_FOOT_INDEX],  # Right foot
    "LeftToeBase": [POSE_LEFT_FOOT_INDEX],  # Left toe
    "RightToeBase": [POSE_RIGHT_FOOT_INDEX],  # Right toe
}

# Mapping presets dictionary
MAPPING_PRESETS = {
    'RIGIFY': RIGIFY_MAPPING,
    'MIXAMO': MIXAMO_MAPPING,
}

class LandmarkMapper:
    """
    Class for mapping MediaPipe landmarks to Blender armature bones.
    """
    
    def __init__(self, armature=None, mapping_preset='RIGIFY'):
        """
        Initialize the landmark mapper.
        
        Args:
            armature: Blender armature object
            mapping_preset: Mapping preset name ('RIGIFY', 'MIXAMO', 'CUSTOM')
        """
        self.armature = armature
        self.mapping_preset = mapping_preset
        self.bone_mapping = {}
        self.custom_mapping = {}
        
        # Initialize mapping
        if armature is not None:
            self.initialize_mapping()
    
    def initialize_mapping(self):
        """Initialize bone mapping based on preset or automatic detection."""
        if self.mapping_preset in MAPPING_PRESETS:
            self.bone_mapping = self.create_preset_mapping(self.mapping_preset)
        else:
            self.bone_mapping = self.create_auto_mapping()
    
    def create_preset_mapping(self, preset_name):
        """
        Create bone mapping based on preset.
        
        Args:
            preset_name: Name of the preset ('RIGIFY', 'MIXAMO')
            
        Returns:
            Dict: Bone mapping dictionary
        """
        if preset_name not in MAPPING_PRESETS:
            return {}
        
        preset_mapping = MAPPING_PRESETS[preset_name]
        bone_mapping = {}
        
        # Check if bones exist in armature
        if self.armature is not None:
            for bone_name, landmarks in preset_mapping.items():
                # Check if bone exists in armature
                if bone_name in self.armature.pose.bones:
                    bone_mapping[bone_name] = landmarks
        
        return bone_mapping
    
    def create_auto_mapping(self):
        """
        Create automatic bone mapping based on bone names.
        
        Returns:
            Dict: Bone mapping dictionary
        """
        bone_mapping = {}
        
        if self.armature is None:
            return bone_mapping
        
        # Common bone name patterns
        patterns = {
            # Head/face patterns
            'head': [POSE_NOSE],
            'neck': [POSE_LEFT_SHOULDER, POSE_RIGHT_SHOULDER],
            'jaw': [FACE_LIPS_OUTER[0], FACE_LIPS_OUTER[6]],
            'tongue': [FACE_LIPS_INNER[3], FACE_LIPS_INNER[7]],
            'eye': {
                'l': [FACE_EYE_LEFT[0]],
                'r': [FACE_EYE_RIGHT[0]],
                'left': [FACE_EYE_LEFT[0]],
                'right': [FACE_EYE_RIGHT[0]]
            },
            'brow': {
                'l': [FACE_EYEBROW_LEFT[2]],
                'r': [FACE_EYEBROW_RIGHT[2]],
                'left': [FACE_EYEBROW_LEFT[2]],
                'right': [FACE_EYEBROW_RIGHT[2]]
            },
            
            # Hand patterns
            'thumb': {
                'l': [HAND_THUMB_MCP],
                'r': [HAND_THUMB_MCP],
                'left': [HAND_THUMB_MCP],
                'right': [HAND_THUMB_MCP]
            },
            'index': {
                'l': [HAND_INDEX_MCP],
                'r': [HAND_INDEX_MCP],
                'left': [HAND_INDEX_MCP],
                'right': [HAND_INDEX_MCP]
            },
            'middle': {
                'l': [HAND_MIDDLE_MCP],
                'r': [HAND_MIDDLE_MCP],
                'left': [HAND_MIDDLE_MCP],
                'right': [HAND_MIDDLE_MCP]
            },
            'ring': {
                'l': [HAND_RING_MCP],
                'r': [HAND_RING_MCP],
                'left': [HAND_RING_MCP],
                'right': [HAND_RING_MCP]
            },
            'pinky': {
                'l': [HAND_PINKY_MCP],
                'r': [HAND_PINKY_MCP],
                'left': [HAND_PINKY_MCP],
                'right': [HAND_PINKY_MCP]
            },
            'hand': {
                'l': [POSE_LEFT_WRIST],
                'r': [POSE_RIGHT_WRIST],
                'left': [POSE_LEFT_WRIST],
                'right': [POSE_RIGHT_WRIST]
            },
            'wrist': {
                'l': [POSE_LEFT_WRIST],
                'r': [POSE_RIGHT_WRIST],
                'left': [POSE_LEFT_WRIST],
                'right': [POSE_RIGHT_WRIST]
            },
            
            # Arm patterns
            'shoulder': {
                'l': [POSE_LEFT_SHOULDER],
                'r': [POSE_RIGHT_SHOULDER],
                'left': [POSE_LEFT_SHOULDER],
                'right': [POSE_RIGHT_SHOULDER]
            },
            'upperarm': {
                'l': [POSE_LEFT_SHOULDER, POSE_LEFT_ELBOW],
                'r': [POSE_RIGHT_SHOULDER, POSE_RIGHT_ELBOW],
                'left': [POSE_LEFT_SHOULDER, POSE_LEFT_ELBOW],
                'right': [POSE_RIGHT_SHOULDER, POSE_RIGHT_ELBOW]
            },
            'forearm': {
                'l': [POSE_LEFT_ELBOW, POSE_LEFT_WRIST],
                'r': [POSE_RIGHT_ELBOW, POSE_RIGHT_WRIST],
                'left': [POSE_LEFT_ELBOW, POSE_LEFT_WRIST],
                'right': [POSE_RIGHT_ELBOW, POSE_RIGHT_WRIST]
            },
            
            # Leg patterns
            'hip': {
                'l': [POSE_LEFT_HIP],
                'r': [POSE_RIGHT_HIP],
                'left': [POSE_LEFT_HIP],
                'right': [POSE_RIGHT_HIP]
            },
            'thigh': {
                'l': [POSE_LEFT_HIP, POSE_LEFT_KNEE],
                'r': [POSE_RIGHT_HIP, POSE_RIGHT_KNEE],
                'left': [POSE_LEFT_HIP, POSE_LEFT_KNEE],
                'right': [POSE_RIGHT_HIP, POSE_RIGHT_KNEE]
            },
            'shin': {
                'l': [POSE_LEFT_KNEE, POSE_LEFT_ANKLE],
                'r': [POSE_RIGHT_KNEE, POSE_RIGHT_ANKLE],
                'left': [POSE_LEFT_KNEE, POSE_LEFT_ANKLE],
                'right': [POSE_RIGHT_KNEE, POSE_RIGHT_ANKLE]
            },
            'foot': {
                'l': [POSE_LEFT_ANKLE, POSE_LEFT_FOOT_INDEX],
                'r': [POSE_RIGHT_ANKLE, POSE_RIGHT_FOOT_INDEX],
                'left': [POSE_LEFT_ANKLE, POSE_LEFT_FOOT_INDEX],
   
(Content truncated due to size limit. Use line ranges to read in chunks)