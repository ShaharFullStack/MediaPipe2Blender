#!/usr/bin/env python3
"""
Test script for Blender add-on functionality.
This script tests the Blender add-on integration with MediaPipe.
"""

import os
import sys
import time
import bpy
import argparse

def setup_test_environment():
    """Set up test environment for Blender add-on."""
    print("Setting up test environment...")
    
    # Check if add-on is installed
    addon_name = "mediapipe_mocap"
    if addon_name not in bpy.context.preferences.addons:
        print(f"Add-on '{addon_name}' is not installed. Installing...")
        bpy.ops.preferences.addon_install(filepath=os.path.join(os.path.dirname(__file__), "..", "mediapipe_mocap.zip"))
        bpy.ops.preferences.addon_enable(module=addon_name)
    
    # Get add-on preferences
    addon_prefs = bpy.context.preferences.addons[addon_name].preferences
    
    # Set MediaPipe script path
    script_path = os.path.join(os.path.dirname(__file__), "..", "src", "mediapipe_module", "__init__.py")
    addon_prefs.mediapipe_script = script_path
    
    print("Test environment set up successfully")
    return True

def create_test_armature():
    """Create a test armature for testing the add-on."""
    print("Creating test armature...")
    
    # Delete existing objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='ARMATURE')
    bpy.ops.object.delete()
    
    # Create new armature
    bpy.ops.object.armature_add(enter_editmode=True)
    armature = bpy.context.active_object
    armature.name = "TestArmature"
    
    # Add bones
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()
    
    # Add root bone
    bpy.ops.armature.bone_primitive_add()
    root = bpy.context.active_bone
    root.name = "Root"
    root.head = (0, 0, 0)
    root.tail = (0, 0, 1)
    
    # Add spine bone
    bpy.ops.armature.bone_primitive_add()
    spine = bpy.context.active_bone
    spine.name = "Spine"
    spine.head = (0, 0, 1)
    spine.tail = (0, 0, 2)
    spine.parent = root
    
    # Add head bone
    bpy.ops.armature.bone_primitive_add()
    head = bpy.context.active_bone
    head.name = "Head"
    head.head = (0, 0, 2)
    head.tail = (0, 0, 3)
    head.parent = spine
    
    # Add left arm bones
    bpy.ops.armature.bone_primitive_add()
    left_arm = bpy.context.active_bone
    left_arm.name = "LeftArm"
    left_arm.head = (0, 0, 2)
    left_arm.tail = (1, 0, 2)
    left_arm.parent = spine
    
    bpy.ops.armature.bone_primitive_add()
    left_forearm = bpy.context.active_bone
    left_forearm.name = "LeftForeArm"
    left_forearm.head = (1, 0, 2)
    left_forearm.tail = (2, 0, 2)
    left_forearm.parent = left_arm
    
    bpy.ops.armature.bone_primitive_add()
    left_hand = bpy.context.active_bone
    left_hand.name = "LeftHand"
    left_hand.head = (2, 0, 2)
    left_hand.tail = (2.5, 0, 2)
    left_hand.parent = left_forearm
    
    # Add right arm bones
    bpy.ops.armature.bone_primitive_add()
    right_arm = bpy.context.active_bone
    right_arm.name = "RightArm"
    right_arm.head = (0, 0, 2)
    right_arm.tail = (-1, 0, 2)
    right_arm.parent = spine
    
    bpy.ops.armature.bone_primitive_add()
    right_forearm = bpy.context.active_bone
    right_forearm.name = "RightForeArm"
    right_forearm.head = (-1, 0, 2)
    right_forearm.tail = (-2, 0, 2)
    right_forearm.parent = right_arm
    
    bpy.ops.armature.bone_primitive_add()
    right_hand = bpy.context.active_bone
    right_hand.name = "RightHand"
    right_hand.head = (-2, 0, 2)
    right_hand.tail = (-2.5, 0, 2)
    right_hand.parent = right_forearm
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"Test armature '{armature.name}' created successfully")
    return armature

def test_addon_connection():
    """Test add-on connection to MediaPipe."""
    print("Testing add-on connection...")
    
    # Get settings
    settings = bpy.context.scene.mediapipe_mocap_settings
    
    # Connect to MediaPipe
    bpy.ops.mediapipe_mocap.connect()
    
    # Wait for connection
    timeout = 10  # 10 seconds timeout
    start_time = time.time()
    while not settings.is_connected and time.time() - start_time < timeout:
        time.sleep(0.1)
    
    if not settings.is_connected:
        print("Failed to connect to MediaPipe")
        return False
    
    print("Connected to MediaPipe successfully")
    
    # Wait for a few seconds to collect data
    print("Collecting data for 5 seconds...")
    time.sleep(5)
    
    # Check if frames are being received
    if settings.frame_count > 0:
        print(f"Received {settings.frame_count} frames")
    else:
        print("No frames received")
    
    # Disconnect from MediaPipe
    bpy.ops.mediapipe_mocap.disconnect()
    
    # Wait for disconnection
    timeout = 5  # 5 seconds timeout
    start_time = time.time()
    while settings.is_connected and time.time() - start_time < timeout:
        time.sleep(0.1)
    
    if settings.is_connected:
        print("Failed to disconnect from MediaPipe")
        return False
    
    print("Disconnected from MediaPipe successfully")
    return True

def test_bone_mapping():
    """Test bone mapping functionality."""
    print("Testing bone mapping...")
    
    # Get settings
    settings = bpy.context.scene.mediapipe_mocap_settings
    
    # Set target armature
    armature = bpy.data.objects.get("TestArmature")
    if not armature:
        print("Test armature not found")
        return False
    
    settings.target_armature = armature
    
    # Test automatic mapping
    settings.mapping_mode = 'AUTO'
    bpy.ops.mediapipe_mocap.create_mapping()
    
    # Test preset mapping
    settings.mapping_mode = 'PRESET'
    settings.mapping_preset = 'MIXAMO'
    bpy.ops.mediapipe_mocap.create_mapping()
    
    # Test manual mapping
    settings.mapping_mode = 'MANUAL'
    
    # Add a few mappings
    bpy.ops.mediapipe_mocap.add_bone_mapping()
    if len(settings.bone_mappings) > 0:
        mapping = settings.bone_mappings[0]
        mapping.bone_name = "Head"
        mapping.landmark_type = 'POSE'
        mapping.landmark_index = 0  # POSE_NOSE
    
    bpy.ops.mediapipe_mocap.add_bone_mapping()
    if len(settings.bone_mappings) > 1:
        mapping = settings.bone_mappings[1]
        mapping.bone_name = "LeftHand"
        mapping.landmark_type = 'POSE'
        mapping.landmark_index = 15  # POSE_LEFT_WRIST
    
    bpy.ops.mediapipe_mocap.add_bone_mapping()
    if len(settings.bone_mappings) > 2:
        mapping = settings.bone_mappings[2]
        mapping.bone_name = "RightHand"
        mapping.landmark_type = 'POSE'
        mapping.landmark_index = 16  # POSE_RIGHT_WRIST
    
    # Apply mappings
    bpy.ops.mediapipe_mocap.apply_bone_mappings()
    
    print("Bone mapping test completed")
    return True

def test_animation_recording():
    """Test animation recording functionality."""
    print("Testing animation recording...")
    
    # Get settings
    settings = bpy.context.scene.mediapipe_mocap_settings
    
    # Set target armature
    armature = bpy.data.objects.get("TestArmature")
    if not armature:
        print("Test armature not found")
        return False
    
    settings.target_armature = armature
    
    # Connect to MediaPipe
    bpy.ops.mediapipe_mocap.connect()
    
    # Wait for connection
    timeout = 10  # 10 seconds timeout
    start_time = time.time()
    while not settings.is_connected and time.time() - start_time < timeout:
        time.sleep(0.1)
    
    if not settings.is_connected:
        print("Failed to connect to MediaPipe")
        return False
    
    # Start recording
    bpy.ops.mediapipe_mocap.start_recording()
    
    # Wait for a few seconds to record animation
    print("Recording animation for 5 seconds...")
    time.sleep(5)
    
    # Stop recording
    bpy.ops.mediapipe_mocap.stop_recording()
    
    # Disconnect from MediaPipe
    bpy.ops.mediapipe_mocap.disconnect()
    
    print("Animation recording test completed")
    return True

def main():
    """Main function."""
    # Set up test environment
    if not setup_test_environment():
        print("Failed to set up test environment")
        return
    
    # Create test armature
    if not create_test_armature():
        print("Failed to create test armature")
        return
    
    # Run tests
    if test_addon_connection():
        print("Add-on connection test passed")
    else:
        print("Add-on connection test failed")
    
    if test_bone_mapping():
        print("Bone mapping test passed")
    else:
        print("Bone mapping test failed")
    
    if test_animation_recording():
        print("Animation recording test passed")
    else:
        print("Animation recording test failed")
    
    print("All tests completed")

if __name__ == "__main__":
    main()
