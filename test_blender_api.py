#!/usr/bin/env python3
"""
Test script for Blender Python API functionality.
This script tests basic Blender Python API operations for add-on development.
"""

import bpy
import os
import sys

def test_blender_api():
    """Test basic Blender Python API functionality."""
    print("\nTesting Blender Python API...")
    
    # Print Blender version
    print(f"Blender Version: {bpy.app.version_string}")
    
    # Test creating a simple object
    try:
        # Create a cube
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.name = "TestCube"
        
        # Create an armature
        bpy.ops.object.armature_add(location=(3, 0, 0))
        armature = bpy.context.active_object
        armature.name = "TestArmature"
        
        # Enter edit mode for the armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Add some bones
        edit_bones = armature.data.edit_bones
        bone1 = edit_bones[0]
        bone1.name = "Bone"
        bone1.head = (3, 0, 0)
        bone1.tail = (3, 0, 1)
        
        bone2 = edit_bones.new("Bone.001")
        bone2.head = bone1.tail
        bone2.tail = (3, 0, 2)
        bone2.parent = bone1
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Test animation
        armature.animation_data_create()
        action = bpy.data.actions.new("TestAction")
        armature.animation_data.action = action
        
        # Create a keyframe
        armature.location = (3, 0, 0)
        armature.keyframe_insert(data_path="location", frame=1)
        
        armature.location = (3, 2, 0)
        armature.keyframe_insert(data_path="location", frame=30)
        
        print("Successfully created test objects and animation.")
        return True
    
    except Exception as e:
        print(f"Error testing Blender API: {e}")
        return False

def test_addon_registration():
    """Test add-on registration functionality."""
    print("\nTesting add-on registration...")
    
    # Define a simple operator
    class SimpleOperator(bpy.types.Operator):
        bl_idname = "object.simple_operator"
        bl_label = "Simple Operator"
        
        def execute(self, context):
            print("Simple operator executed")
            return {'FINISHED'}
    
    # Define a simple panel
    class SimplePanel(bpy.types.Panel):
        bl_idname = "VIEW3D_PT_simple_panel"
        bl_label = "Simple Panel"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'Tool'
        
        def draw(self, context):
            layout = self.layout
            layout.operator(SimpleOperator.bl_idname)
    
    # Test registration
    try:
        bpy.utils.register_class(SimpleOperator)
        bpy.utils.register_class(SimplePanel)
        print("Successfully registered test classes.")
        
        # Test unregistration
        bpy.utils.unregister_class(SimplePanel)
        bpy.utils.unregister_class(SimpleOperator)
        print("Successfully unregistered test classes.")
        
        return True
    
    except Exception as e:
        print(f"Error testing add-on registration: {e}")
        return False

def main():
    """Run all Blender Python API tests."""
    print("Starting Blender Python API tests...")
    
    # Test basic API functionality
    api_success = test_blender_api()
    
    # Test add-on registration
    reg_success = test_addon_registration()
    
    # Print summary
    print("\nTest Summary:")
    print(f"Blender API Functionality: {'Success' if api_success else 'Failed'}")
    print(f"Add-on Registration: {'Success' if reg_success else 'Failed'}")
    
    if api_success and reg_success:
        print("\nAll Blender Python API tests passed successfully!")
    else:
        print("\nSome Blender Python API tests failed. Please check the output above for details.")

if __name__ == "__main__":
    main()
