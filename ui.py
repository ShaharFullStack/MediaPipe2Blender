"""
MediaPipe Motion Capture - UI Module
This module handles the user interface components for the Blender add-on.
"""

import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty
)
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    UIList
)

# Import other modules
from . import landmark_mapping

# -------------------------------------------------------------------------
# Property Groups
# -------------------------------------------------------------------------

class MediaPipeMocapBoneMapping(PropertyGroup):
    """Property group for bone mapping"""
    
    bone_name: StringProperty(
        name="Bone",
        description="Name of the bone",
        default=""
    )
    
    landmark_type: EnumProperty(
        name="Landmark Type",
        description="Type of landmark",
        items=[
            ('FACE', "Face", "Face landmark"),
            ('HAND', "Hand", "Hand landmark"),
            ('POSE', "Pose", "Pose landmark")
        ],
        default='POSE'
    )
    
    landmark_index: IntProperty(
        name="Landmark Index",
        description="Index of the landmark",
        default=0,
        min=0
    )
    
    hand_index: IntProperty(
        name="Hand Index",
        description="Index of the hand (0 for left, 1 for right)",
        default=0,
        min=0,
        max=1
    )
    
    is_active: BoolProperty(
        name="Active",
        description="Whether this mapping is active",
        default=True
    )

# -------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------

class MEDIAPIPE_MOCAP_OT_add_bone_mapping(Operator):
    """Add a new bone mapping"""
    bl_idname = "mediapipe_mocap.add_bone_mapping"
    bl_label = "Add Bone Mapping"
    bl_description = "Add a new bone mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if target armature is set
        if settings.target_armature is None:
            self.report({'ERROR'}, "No target armature selected. Please select an armature.")
            return {'CANCELLED'}
        
        # Add new mapping
        mapping = settings.bone_mappings.add()
        mapping.bone_name = ""
        mapping.landmark_type = 'POSE'
        mapping.landmark_index = 0
        mapping.hand_index = 0
        mapping.is_active = True
        
        # Set active index
        settings.active_bone_mapping = len(settings.bone_mappings) - 1
        
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_remove_bone_mapping(Operator):
    """Remove the selected bone mapping"""
    bl_idname = "mediapipe_mocap.remove_bone_mapping"
    bl_label = "Remove Bone Mapping"
    bl_description = "Remove the selected bone mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if there are any mappings
        if len(settings.bone_mappings) == 0:
            return {'CANCELLED'}
        
        # Check if active index is valid
        if settings.active_bone_mapping < 0 or settings.active_bone_mapping >= len(settings.bone_mappings):
            return {'CANCELLED'}
        
        # Remove mapping
        settings.bone_mappings.remove(settings.active_bone_mapping)
        
        # Update active index
        if settings.active_bone_mapping >= len(settings.bone_mappings):
            settings.active_bone_mapping = max(0, len(settings.bone_mappings) - 1)
        
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_move_bone_mapping(Operator):
    """Move the selected bone mapping up or down"""
    bl_idname = "mediapipe_mocap.move_bone_mapping"
    bl_label = "Move Bone Mapping"
    bl_description = "Move the selected bone mapping up or down"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: EnumProperty(
        name="Direction",
        description="Direction to move",
        items=[
            ('UP', "Up", "Move up"),
            ('DOWN', "Down", "Move down")
        ],
        default='UP'
    )
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if there are any mappings
        if len(settings.bone_mappings) <= 1:
            return {'CANCELLED'}
        
        # Check if active index is valid
        if settings.active_bone_mapping < 0 or settings.active_bone_mapping >= len(settings.bone_mappings):
            return {'CANCELLED'}
        
        # Get new index
        new_index = settings.active_bone_mapping
        if self.direction == 'UP' and new_index > 0:
            new_index -= 1
        elif self.direction == 'DOWN' and new_index < len(settings.bone_mappings) - 1:
            new_index += 1
        else:
            return {'CANCELLED'}
        
        # Move mapping
        settings.bone_mappings.move(settings.active_bone_mapping, new_index)
        
        # Update active index
        settings.active_bone_mapping = new_index
        
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_apply_bone_mappings(Operator):
    """Apply bone mappings to the landmark mapper"""
    bl_idname = "mediapipe_mocap.apply_bone_mappings"
    bl_label = "Apply Bone Mappings"
    bl_description = "Apply bone mappings to the landmark mapper"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if target armature is set
        if settings.target_armature is None:
            self.report({'ERROR'}, "No target armature selected. Please select an armature.")
            return {'CANCELLED'}
        
        # Get landmark mapper
        from . import animation
        processor = animation.get_animation_processor()
        mapper = processor.mapper
        
        # Clear custom mapping
        mapper.clear_custom_mapping()
        
        # Apply mappings
        for mapping in settings.bone_mappings:
            if mapping.is_active and mapping.bone_name:
                # Get landmark index
                landmark_index = mapping.landmark_index
                
                # Adjust landmark index based on type and hand index
                if mapping.landmark_type == 'HAND':
                    # Hand landmarks are 0-20 for each hand
                    landmark_index = mapping.landmark_index
                
                # Set custom mapping
                mapper.set_custom_mapping(mapping.bone_name, [landmark_index])
        
        self.report({'INFO'}, f"Applied {len(settings.bone_mappings)} bone mappings.")
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_load_bone_mappings(Operator):
    """Load bone mappings from the landmark mapper"""
    bl_idname = "mediapipe_mocap.load_bone_mappings"
    bl_label = "Load Bone Mappings"
    bl_description = "Load bone mappings from the landmark mapper"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if target armature is set
        if settings.target_armature is None:
            self.report({'ERROR'}, "No target armature selected. Please select an armature.")
            return {'CANCELLED'}
        
        # Get landmark mapper
        from . import animation
        processor = animation.get_animation_processor()
        mapper = processor.mapper
        
        # Get bone mapping
        bone_mapping = mapper.get_bone_mapping()
        
        # Clear existing mappings
        settings.bone_mappings.clear()
        
        # Add mappings
        for bone_name, landmarks in bone_mapping.items():
            if not landmarks:
                continue
            
            # Add mapping for each landmark
            for landmark_index in landmarks:
                mapping = settings.bone_mappings.add()
                mapping.bone_name = bone_name
                
                # Determine landmark type
                if landmark_index < 468:
                    mapping.landmark_type = 'FACE'
                elif landmark_index < 21:
                    mapping.landmark_type = 'HAND'
                else:
                    mapping.landmark_type = 'POSE'
                
                mapping.landmark_index = landmark_index
                mapping.hand_index = 0  # Default to left hand
                mapping.is_active = True
        
        # Set active index
        settings.active_bone_mapping = 0
        
        self.report({'INFO'}, f"Loaded {len(settings.bone_mappings)} bone mappings.")
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_clear_bone_mappings(Operator):
    """Clear all bone mappings"""
    bl_idname = "mediapipe_mocap.clear_bone_mappings"
    bl_label = "Clear Bone Mappings"
    bl_description = "Clear all bone mappings"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Clear mappings
        settings.bone_mappings.clear()
        
        # Reset active index
        settings.active_bone_mapping = 0
        
        self.report({'INFO'}, "Cleared all bone mappings.")
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_select_bone(Operator):
    """Select a bone from the armature"""
    bl_idname = "mediapipe_mocap.select_bone"
    bl_label = "Select Bone"
    bl_description = "Select a bone from the armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if target armature is set
        if settings.target_armature is None:
            self.report({'ERROR'}, "No target armature selected. Please select an armature.")
            return {'CANCELLED'}
        
        # Check if active index is valid
        if settings.active_bone_mapping < 0 or settings.active_bone_mapping >= len(settings.bone_mappings):
            return {'CANCELLED'}
        
        # Get active mapping
        mapping = settings.bone_mappings[settings.active_bone_mapping]
        
        # Get selected bone
        armature = settings.target_armature
        active_bone = None
        
        if context.mode == 'POSE':
            if context.active_pose_bone:
                active_bone = context.active_pose_bone.name
        elif context.mode == 'EDIT_ARMATURE':
            if context.active_bone:
                active_bone = context.active_bone.name
        
        if active_bone:
            mapping.bone_name = active_bone
            self.report({'INFO'}, f"Selected bone: {active_bone}")
        else:
            self.report({'ERROR'}, "No bone selected. Please select a bone in pose or edit mode.")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class MEDIAPIPE_MOCAP_OT_visualize_landmarks(Operator):
    """Visualize MediaPipe landmarks in the 3D view"""
    bl_idname = "mediapipe_mocap.visualize_landmarks"
    bl_label = "Visualize Landmarks"
    bl_description = "Visualize MediaPipe landmarks in the 3D view"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get settings
        settings = context.scene.mediapipe_mocap_settings
        
        # Check if visualization is already active
        if settings.is_visualizing:
            # Stop visualization
            settings.is_visualizing = False
            
            # Remove visualization objects
            self.remove_visualization_objects()
            
            self.report({'INFO'}, "Stopped landmark visualization.")
        else:
            # Start visualization
            settings.is_visualizing = True
            
            # Create visualization objects
            self.create_visualization_objects()
            
            self.report({'INFO'}, "Started landmark visualization.")
        
        return {'FINISHED'}
    
    def create_visualization_objects(self):
        """Create objects to visualize landmarks"""
        # TODO: Implement landmark visualization
        # This will be implemented in the future
        pass
    
    def remove_visualization_objects(self):
        """Remove visualization objects"""
        # TODO: Implement landmark visualization cleanup
        # This will be implemented in the future
        pass

# -------------------------------------------------------------------------
# UI Lists
# -------------------------------------------------------------------------

class MEDIAPIPE_MOCAP_UL_bone_mappings(UIList):
    """UI list for bone mappings"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Draw bone mapping item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # Active checkbox
            row.prop(item, "is_active", text="", emboss=False)
            
            # Bone name
            if item.bone_name:
                row.label(text=item.bone_name, icon='BONE_DATA')
            else:
                row.label(text="<No Bone>", icon='ERROR')
            
            # Landmark type and index
            if item.landmark_type == 'HAND':
                hand_text = "L" if item.hand_index == 0 else "R"
                row.label(text=f"{item.landmark_type} {hand_text} {item.landmark_index}")
            else:
                row.label(text=f"{item.landmark_type} {item.landmark_index}")
        
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.bone_name)

# -------------------------------------------------------------------------
# Panels
# -------------------------------------------------------------------------

class MEDIAPIPE_MOCAP_PT_mapping_panel(Panel):
    """Panel for bone mapping settings"""
    bl_label = "Bone Mapping"
    bl_idname = "MEDIAPIPE_MOCAP_PT_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MediaPipe MoCap'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.mediapipe_mocap_settings
        
        # Target armature
        box = layout.box()
        box.label(text="Target Armature:")
        box.prop(settings, "target_armature")
        
        # Mapping mode
        box = layout.box()
        box.label(text="Mapping Mode:")
        box.prop(settings, "mapping_mode", expand=True)
        
        if settings.mapping_mode == 'PRESET':
            box.prop(settings, "mapping_preset")
        
        box.prop(settings, "scale_factor")
        
        # Create mapping button
        row = box.row()
        row.operator("mediapipe_mocap.create_mapping", icon='BONE_DATA')
        
        # Bone mappings
        if settings.mapping_mode == 'MANUAL':
            box = layout.box()
            box.label(text="Bone Mappings:")
            
            # Mapping list
            row = box.row()
            row.template_list("MEDIAPIPE_MOCAP_UL_bone_mappings", "", settings, "bone_mappings", settings, "active_bone_mapping", rows=3)
            
            # List controls
            col = row.column(align=True)
            col.operator("mediapipe_mocap.add_bone_mapping", icon='ADD', text="")
            col.operator("mediapipe_mocap.remove_bone_mapping", icon='REMOVE', text="")
            col.separator()
            col.operator("mediapipe_mocap.move_bone_mapping", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("mediapipe_mocap.mov
(Content truncated due to size limit. Use line ranges to read in chunks)