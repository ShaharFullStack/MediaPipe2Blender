"""
MediaPipe to Blender Live Animation Add-on
Developer Documentation

This document provides technical details for developers who want to understand or extend the add-on.
"""

# Architecture Overview

The MediaPipe to Blender live animation add-on consists of two main components:

1. **MediaPipe Module**: A standalone Python module that handles video capture, landmark detection, and data streaming
2. **Blender Add-on**: A Blender Python add-on that receives landmark data and animates armature bones

These components communicate via ZeroMQ, a high-performance asynchronous messaging library.

## System Architecture Diagram

```
┌─────────────────────┐                  ┌─────────────────────┐
│                     │                  │                     │
│  MediaPipe Module   │                  │   Blender Add-on    │
│                     │                  │                     │
│  ┌───────────────┐  │                  │  ┌───────────────┐  │
│  │ Video Capture │  │                  │  │ Data Receiver │  │
│  └───────┬───────┘  │                  │  └───────┬───────┘  │
│          │          │                  │          │          │
│  ┌───────┴───────┐  │                  │  ┌───────┴───────┐  │
│  │   Landmark    │  │                  │  │   Landmark    │  │
│  │   Detection   │  │                  │  │    Mapping    │  │
│  └───────┬───────┘  │                  │  └───────┬───────┘  │
│          │          │                  │          │          │
│  ┌───────┴───────┐  │      ZeroMQ      │  ┌───────┴───────┐  │
│  │ Data Streaming│◄─┼─────────────────►│  │   Animation   │  │
│  └───────────────┘  │                  │  │   Processor   │  │
│                     │                  │  └───────────────┘  │
└─────────────────────┘                  └─────────────────────┘
```

# MediaPipe Module

## Components

### Video Capture (`video_capture.py`)

Handles webcam access and frame retrieval using OpenCV.

**Key Classes:**
- `VideoCapture`: Manages video capture from webcam or video file
- `VideoManager`: Singleton manager for video capture resources

**Key Methods:**
- `initialize()`: Set up video capture
- `get_frame()`: Retrieve the next video frame
- `release()`: Release video capture resources

### Landmark Detection (`landmark_detection.py`)

Processes video frames to detect face, hand, and body landmarks using MediaPipe.

**Key Classes:**
- `FaceDetector`: Detects facial landmarks
- `HandDetector`: Detects hand landmarks
- `PoseDetector`: Detects body pose landmarks
- `MediaPipeProcessor`: Combines all detectors and processes frames

**Key Methods:**
- `process_frame()`: Process a video frame and detect landmarks
- `get_landmarks()`: Retrieve detected landmarks
- `set_result_callback()`: Set callback for detection results

### Data Streaming (`data_streaming.py`)

Streams landmark data to Blender using ZeroMQ.

**Key Classes:**
- `DataStreamer`: Handles ZeroMQ communication

**Key Methods:**
- `initialize()`: Set up ZeroMQ socket
- `send_data()`: Send landmark data
- `close()`: Close ZeroMQ connection

## Data Structures

### Landmark Data Format

The data is serialized using Python's `pickle` module and has the following structure:

```python
{
    'faces': [
        {
            'landmarks': [{'x': float, 'y': float, 'z': float, 'visibility': float}, ...],
            'visibility': [float, ...],
            'detection_confidence': float,
            'tracking_id': int
        },
        ...
    ],
    'hands': [
        {
            'landmarks': [{'x': float, 'y': float, 'z': float}, ...],
            'handedness': str,  # 'Left' or 'Right'
            'hand_flag': int,   # 0 for left, 1 for right
            'detection_confidence': float,
            'tracking_id': int
        },
        ...
    ],
    'pose': [
        {
            'landmarks': [{'x': float, 'y': float, 'z': float, 'visibility': float}, ...],
            'visibility': [float, ...],
            'detection_confidence': float,
            'tracking_id': int
        },
        ...
    ],
    'frame_timestamp': float,
    'frame_index': int,
    'source_dimensions': (width, height)
}
```

# Blender Add-on

## Components

### Add-on Registration (`__init__.py`)

Handles add-on registration, preferences, and property definitions.

**Key Functions:**
- `register()`: Register the add-on with Blender
- `unregister()`: Unregister the add-on

**Property Groups:**
- `MediaPipeMocapSettings`: Main settings for the add-on
- `MediaPipeMocapPreferences`: Add-on preferences

### Landmark Mapping (`landmark_mapping.py`)

Maps MediaPipe landmarks to Blender armature bones.

**Key Classes:**
- `LandmarkMapper`: Maps landmarks to bones

**Key Methods:**
- `initialize_mapping()`: Set up initial bone mapping
- `create_preset_mapping()`: Create mapping based on preset
- `create_auto_mapping()`: Create automatic mapping based on bone names
- `update_bone_transform()`: Update bone transform based on landmark data
- `update_armature()`: Update entire armature based on landmark data

### Animation Processing (`animation.py`)

Handles animation updates and keyframing.

**Key Classes:**
- `AnimationProcessor`: Processes animation data

**Key Methods:**
- `process_frame()`: Process a frame of landmark data
- `apply_smoothing()`: Apply smoothing to landmark data
- `update_armature()`: Update armature based on landmark data
- `insert_keyframes()`: Insert keyframes for animated bones

### User Interface (`ui.py`)

Provides the Blender user interface for the add-on.

**Key Classes:**
- `MEDIAPIPE_MOCAP_PT_mapping_panel`: Bone mapping panel
- `MEDIAPIPE_MOCAP_PT_animation_panel`: Animation settings panel
- `MEDIAPIPE_MOCAP_PT_status_panel`: Status panel

**Key Operators:**
- `MEDIAPIPE_MOCAP_OT_connect`: Connect to MediaPipe
- `MEDIAPIPE_MOCAP_OT_disconnect`: Disconnect from MediaPipe
- `MEDIAPIPE_MOCAP_OT_start_recording`: Start animation recording
- `MEDIAPIPE_MOCAP_OT_stop_recording`: Stop animation recording
- `MEDIAPIPE_MOCAP_OT_create_mapping`: Create bone mapping

## Data Flow

1. The Blender add-on connects to the MediaPipe module via ZeroMQ
2. MediaPipe captures video frames and detects landmarks
3. Landmark data is streamed to Blender
4. The add-on receives the data and maps landmarks to bones
5. Bone transforms are updated based on landmark positions
6. Keyframes are inserted if auto-keyframing is enabled

# Extension Points

## Adding New Landmark Types

To add support for new MediaPipe landmark types:

1. Add a new detector class in `landmark_detection.py`
2. Update the `MediaPipeProcessor` class to use the new detector
3. Add the new landmark indices in `landmark_mapping.py`
4. Update the mapping presets to include the new landmarks
5. Add UI elements in `ui.py` to control the new landmark type

## Adding New Mapping Presets

To add a new mapping preset for a specific rig:

1. Define the mapping dictionary in `landmark_mapping.py`
2. Add the preset to the `MAPPING_PRESETS` dictionary
3. Update the mapping preset enum in `__init__.py`

## Custom Data Processing

To add custom data processing:

1. Extend the `AnimationProcessor` class in `animation.py`
2. Add new processing methods
3. Update the `process_frame()` method to use the new processing
4. Add UI elements in `ui.py` to control the new processing options

# Development Guidelines

## Coding Standards

- Follow PEP 8 for Python code style
- Use type hints where appropriate
- Document all classes and methods with docstrings
- Keep the MediaPipe module and Blender add-on components separate

## Testing

- Use the test scripts in the `tests` directory
- Test MediaPipe functionality with `test_mediapipe_module.py`
- Test Blender add-on functionality with `test_blender_addon.py`
- Test data streaming with `test_data_streaming.py`
- Test full integration with `test_integration.py`

## Debugging

- Enable debug logging in the add-on preferences
- Check the Blender System Console for error messages
- Use the visualization feature to see landmark positions
- Test components separately to isolate issues

## Performance Considerations

- Minimize operations in the main thread
- Use threading for long-running operations
- Apply smoothing to reduce jitter
- Optimize landmark detection by disabling unused features
- Consider downscaling video frames for faster processing

# Deployment

## Building the Add-on

To build the add-on for distribution:

1. Run the `build.py` script
2. This will create a ZIP file with all necessary files
3. The ZIP file can be installed in Blender using the Add-on preferences

## Required Files

The following files must be included in the add-on ZIP:

- `__init__.py`: Main add-on file
- `landmark_mapping.py`: Landmark mapping module
- `animation.py`: Animation processing module
- `ui.py`: User interface module
- `mediapipe_module/`: Directory containing MediaPipe module files
  - `__init__.py`: MediaPipe module entry point
  - `video_capture.py`: Video capture module
  - `landmark_detection.py`: Landmark detection module
  - `data_streaming.py`: Data streaming module

## Version Management

- Update the version number in `__init__.py`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Document changes in the README.md file

# API Reference

## MediaPipe Module API

### `get_mediapipe_module()`

Returns the MediaPipe module instance.

### `MediaPipeModule.configure(config)`

Configure the MediaPipe module.

**Parameters:**
- `config`: Dictionary with configuration options
  - `camera_index`: Camera device index
  - `camera_width`: Camera width
  - `camera_height`: Camera height
  - `camera_fps`: Camera FPS
  - `host`: ZeroMQ host address
  - `port`: ZeroMQ port
  - `enable_face`: Enable face detection
  - `enable_hands`: Enable hand detection
  - `enable_pose`: Enable pose detection

### `MediaPipeModule.initialize()`

Initialize the MediaPipe module.

### `MediaPipeModule.start()`

Start MediaPipe processing.

### `MediaPipeModule.stop()`

Stop MediaPipe processing.

### `MediaPipeModule.get_status()`

Get the current status of the MediaPipe module.

## Blender Add-on API

### `landmark_mapping.LandmarkMapper`

**Methods:**
- `set_armature(armature)`: Set the target armature
- `set_mapping_preset(preset_name)`: Set the mapping preset
- `set_custom_mapping(bone_name, landmarks)`: Set custom mapping for a bone
- `update_armature(data, influence, scale_factor)`: Update armature based on landmark data
- `insert_keyframes(frame)`: Insert keyframes for mapped bones

### `animation.AnimationProcessor`

**Methods:**
- `set_armature(armature)`: Set the target armature
- `start_recording()`: Start animation recording
- `stop_recording()`: Stop animation recording
- `process_frame(data)`: Process a frame of landmark data

# Appendix

## Dependencies

- **MediaPipe**: Face, hand, and body landmark detection
- **OpenCV**: Video capture and image processing
- **NumPy**: Numerical operations
- **PyZMQ**: ZeroMQ messaging library

## References

- MediaPipe Documentation: https://mediapipe.dev/
- Blender Python API: https://docs.blender.org/api/current/
- ZeroMQ Documentation: https://zeromq.org/

## License

This add-on is released under the MIT License.

## Contact

For developer support or contributions:
- GitHub: [Repository URL]
- Email: [Contact Email]
