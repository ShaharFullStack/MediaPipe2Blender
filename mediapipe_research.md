# MediaPipe Research Findings

## MediaPipe Overview

MediaPipe is a framework developed by Google that provides ready-to-use ML solutions for computer vision tasks. For our add-on, we're particularly interested in the following features:

### Face Landmark Detection
- Uses the Face Landmarker task to detect face landmarks and facial expressions
- Outputs 3D face landmarks (468 points)
- Provides blendshape scores (coefficients representing facial expressions)
- Supports transformation matrices for effects rendering
- Configuration options include:
  - Running mode (IMAGE, VIDEO, LIVE_STREAM)
  - Number of faces to detect
  - Detection confidence thresholds
  - Output options for blendshapes and transformation matrices

### Hand Landmark Detection
- Uses the Hand Landmarker task to detect hand landmarks
- Outputs 21 3D landmarks per hand
- Supports tracking to reduce latency in video/live stream modes
- Configuration options include:
  - Running mode (IMAGE, VIDEO, LIVE_STREAM)
  - Number of hands to detect
  - Detection confidence thresholds
  - Tracking confidence threshold

### Pose Landmark Detection
- Uses the Pose Landmarker task to detect body pose landmarks
- Outputs body pose landmarks in image coordinates and 3D world coordinates
- Supports tracking to reduce latency in video/live stream modes
- Configuration options include:
  - Running mode (IMAGE, VIDEO, LIVE_STREAM)
  - Number of poses to detect
  - Detection confidence thresholds
  - Tracking confidence threshold
  - Segmentation mask output option

## MediaPipe Python API Usage

All three landmark detection systems follow a similar pattern:

1. Install dependencies:
   ```
   python -m pip install mediapipe
   ```

2. Import necessary modules:
   ```python
   import mediapipe as mp
   from mediapipe.tasks import python
   from mediapipe.tasks.python import vision
   ```

3. Load the model:
   ```python
   model_path = '/path/to/model.task'
   ```

4. Create the task with configuration options:
   ```python
   BaseOptions = mp.tasks.BaseOptions
   LandmarkerClass = mp.tasks.vision.[Face|Hand|Pose]Landmarker
   LandmarkerOptions = mp.tasks.vision.[Face|Hand|Pose]LandmarkerOptions
   VisionRunningMode = mp.tasks.vision.RunningMode

   options = LandmarkerOptions(
       base_options=BaseOptions(model_asset_path=model_path),
       running_mode=VisionRunningMode.[IMAGE|VIDEO|LIVE_STREAM],
       # Additional options specific to each landmarker
   )
   ```

5. Create the landmarker and process data:
   ```python
   with LandmarkerClass.create_from_options(options) as landmarker:
       # For image mode
       result = landmarker.detect(mp_image)
       
       # For video mode
       result = landmarker.detect_for_video(mp_image, timestamp_ms)
       
       # For live stream mode (requires callback)
       landmarker.detect_async(mp_image, timestamp_ms)
   ```

6. Handle results:
   - Face landmarks: `result.face_landmarks`
   - Face blendshapes: `result.face_blendshapes`
   - Hand landmarks: `result.hand_landmarks`
   - Pose landmarks: `result.pose_landmarks`
   - Pose world landmarks: `result.pose_world_landmarks`

## Blender Add-on Development

Blender add-ons are Python modules with specific requirements:

1. Basic structure:
   ```python
   bl_info = {
       "name": "Add-on Name",
       "blender": (2, 80, 0),
       "category": "Category",
   }

   def register():
       # Register classes, operators, panels, etc.
       pass

   def unregister():
       # Unregister everything registered by register()
       pass

   if __name__ == "__main__":
       register()
   ```

2. Operators:
   ```python
   class MyOperator(bpy.types.Operator):
       bl_idname = "my.operator"
       bl_label = "My Operator"
       bl_options = {'REGISTER', 'UNDO'}
       
       def execute(self, context):
           # Operator code
           return {'FINISHED'}
   ```

3. Panels:
   ```python
   class MyPanel(bpy.types.Panel):
       bl_idname = "MY_PT_panel"
       bl_label = "My Panel"
       bl_space_type = "VIEW_3D"
       bl_region_type = "UI"
       bl_category = "My Tab"
       
       def draw(self, context):
           layout = self.layout
           # Panel UI code
   ```

4. Registration:
   ```python
   def register():
       bpy.utils.register_class(MyOperator)
       bpy.utils.register_class(MyPanel)

   def unregister():
       bpy.utils.unregister_class(MyPanel)
       bpy.utils.unregister_class(MyOperator)
   ```

## Real-time Data Streaming Options

For real-time communication between MediaPipe and Blender:

1. ZeroMQ (pyzmq):
   - Lightweight messaging library
   - Supports various communication patterns (request-reply, publish-subscribe, etc.)
   - Good for real-time data streaming
   - Can be used to stream landmark data from MediaPipe to Blender

2. WebSockets:
   - Bidirectional communication protocol
   - Can be used with libraries like websockets or websocket-client
   - Good for real-time applications

3. Direct Integration:
   - Run MediaPipe directly within Blender's Python environment
   - Avoids network overhead
   - Requires managing dependencies within Blender

## Existing MediaPipe-Blender Integration Solutions

### BlendArMocap
- GitHub: https://github.com/cgtinker/BlendArMocap
- Features:
  - Real-time motion tracking in Blender using MediaPipe
  - Supports pose, hand, face, and holistic features
  - Calculates rotation data based on detection results
  - Transfers tracking data to rigs
  - Supports rigify rigs
  - Uses mapping objects with instructions and constraints
  - Imports Freemocap session data

### VIPER-Blender-Facial-Motion-Capture
- GitHub: https://github.com/Daniel-W-Blender-Python/VIPER-Blender-Facial-Motion-Capture
- Features:
  - Uses MediaPipe Face Landmarker for facial motion capture
  - Maps facial expressions onto 3D characters in real-time
  - Uses blendshapes from MediaPipe
  - Supports customization of expressiveness for different facial features
  - Includes dependency installation within Blender
  - Works with Rigify bone rigs

## Key Insights for Our Implementation

1. **Dependency Management**:
   - Both existing solutions handle MediaPipe dependencies installation
   - Need to consider how to manage dependencies in our add-on

2. **Landmark Mapping**:
   - BlendArMocap uses a mapping object system with constraints
   - VIPER uses blendshapes for facial expressions
   - Need to design a flexible mapping system for all landmark types

3. **Real-time Processing**:
   - Both solutions process MediaPipe data in real-time
   - Need to consider performance optimization

4. **User Interface**:
   - VIPER provides expressiveness controls for customization
   - Need to design a user-friendly interface with manual adjustment options

5. **Integration with Blender**:
   - Both solutions integrate with Blender's animation system
   - Need to consider how to handle keyframing and animation recording

6. **Architecture**:
   - Consider separating MediaPipe processing from Blender integration
   - Design for extensibility to support future MediaPipe features
