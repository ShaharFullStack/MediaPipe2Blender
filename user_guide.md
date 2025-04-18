"""
MediaPipe to Blender Live Animation Add-on
User Guide

This guide provides detailed instructions for using the MediaPipe to Blender live animation add-on.
"""

# Installation

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Blender**: Version 2.93 or newer (Blender 4.0+ recommended)
- **Python**: Version 3.7 or newer (included with Blender)
- **Hardware**: 
  - Webcam or video input device
  - 4GB RAM minimum (8GB+ recommended)
  - GPU recommended for better performance

## Installation Steps

1. **Download the Add-on**:
   - Download the `mediapipe_mocap.zip` file from the releases page

2. **Install in Blender**:
   - Open Blender
   - Go to Edit > Preferences > Add-ons
   - Click "Install..." and select the downloaded ZIP file
   - Enable the add-on by checking the box next to "Animation: MediaPipe Motion Capture"

3. **First-Time Setup**:
   - The first time you use the add-on, it will automatically install required Python packages
   - This requires an internet connection and may take a few minutes
   - Required packages include:
     - MediaPipe
     - OpenCV
     - NumPy
     - PyZMQ

# Getting Started

## Interface Overview

The add-on adds a new panel to the 3D View sidebar. To access it:
1. In the 3D View, press `N` to open the sidebar
2. Select the "MediaPipe MoCap" tab

The interface is divided into three main panels:
- **Bone Mapping**: Configure how MediaPipe landmarks map to armature bones
- **Animation Settings**: Control animation parameters and recording
- **Status**: Monitor connection status and statistics

## Quick Start Guide

1. **Prepare Your Armature**:
   - Open a Blender file with an armature you want to animate
   - Make sure the armature is in rest position

2. **Configure Bone Mapping**:
   - In the Bone Mapping panel, select your armature from the dropdown
   - Choose a mapping mode:
     - **Auto**: Automatically maps based on bone names
     - **Preset**: Uses predefined mappings for common rigs
     - **Manual**: Create custom mappings
   - Click "Create Mapping" to generate the initial mapping

3. **Connect to MediaPipe**:
   - In the Status panel, click "Connect"
   - The first time you connect, you may see a webcam permission request
   - Once connected, you should see "Status: Connected" and statistics

4. **Start Recording**:
   - In the Animation Settings panel, click "Start Recording"
   - Your armature should now move in response to your movements
   - To stop recording, click "Stop Recording"

5. **Adjust Settings as Needed**:
   - Use the Animation Settings panel to adjust smoothing, influence, etc.
   - If bones aren't moving correctly, try a different mapping mode or create manual mappings

# Detailed Features

## Bone Mapping

### Mapping Modes

- **Auto Mapping**:
  - Analyzes bone names and automatically maps to appropriate landmarks
  - Works best with standard naming conventions
  - Example: Bones named "head", "lefthand", "rightarm" will be mapped automatically

- **Preset Mapping**:
  - Provides predefined mappings for popular rigs
  - Available presets:
    - **Rigify**: For Blender's built-in Rigify system
    - **Mixamo**: For characters from Mixamo

- **Manual Mapping**:
  - Create custom mappings for each bone
  - Useful for custom rigs or fine-tuning automatic mappings

### Manual Mapping Editor

To create manual mappings:
1. Select "Manual" mapping mode
2. Click the "+" button to add a new mapping
3. Select the bone you want to map:
   - Type the bone name, or
   - Click the eyedropper icon and select a bone in the 3D view
4. Choose the landmark type:
   - **Face**: 468 facial landmarks
   - **Hand**: 21 landmarks per hand
   - **Pose**: 33 body landmarks
5. Set the landmark index (refer to the MediaPipe documentation for specific indices)
6. For hand landmarks, select which hand (Left or Right)
7. Click "Apply Bone Mappings" to apply your changes

## Animation Settings

### Recording Controls

- **Auto Keyframe**: When enabled, automatically inserts keyframes during recording
- **Keyframe Interval**: Sets how often keyframes are inserted (in frames)
- **Smoothing**: Controls how much smoothing is applied to the animation:
  - 0.0: No smoothing, raw data
  - 1.0: Maximum smoothing, very stable but less responsive
  - Recommended: 0.3-0.7 for a good balance

### Influence Settings

Control how much each landmark type affects the animation:
- **Face Influence**: How much facial landmarks affect the animation (0.0-1.0)
- **Hands Influence**: How much hand landmarks affect the animation (0.0-1.0)
- **Pose Influence**: How much body landmarks affect the animation (0.0-1.0)

These settings allow you to focus on specific parts of the animation or blend different influences.

## Visualization

The add-on can visualize MediaPipe landmarks in the 3D viewport:
1. In the Bone Mapping panel, click "Show Landmarks"
2. Landmarks will appear as small spheres in the 3D view
3. To hide landmarks, click "Hide Landmarks"

This is useful for debugging and understanding how landmarks map to bones.

# Advanced Usage

## Working with Animation Data

The add-on creates standard Blender animation data, which means you can:
- Edit the recorded animation in the Dope Sheet or Graph Editor
- Apply Blender's animation modifiers and constraints
- Mix with other animation techniques
- Export to any format Blender supports

## Command Line Usage

For advanced users, the MediaPipe module can be run separately from the command line:
```
python3 mediapipe_module/__init__.py --host 127.0.0.1 --port 5556 --camera 0
```

This allows for more flexible setups, such as:
- Running MediaPipe on a different computer
- Processing pre-recorded video instead of webcam
- Custom integration with other software

## Performance Optimization

To improve performance:
1. In the add-on preferences, adjust camera resolution
2. Disable features you don't need (e.g., face detection if only animating body)
3. Increase keyframe interval
4. Run Blender in a dedicated graphics mode

# Troubleshooting

## Common Issues and Solutions

### MediaPipe Not Available
- **Issue**: Error message about MediaPipe not being available
- **Solution**: 
  - Ensure you have an internet connection for the first-time setup
  - Try manually installing MediaPipe: `pip install mediapipe opencv-python pyzmq`

### Camera Not Found
- **Issue**: Cannot connect to camera
- **Solution**:
  - Ensure your webcam is connected and not being used by another application
  - Try a different camera index in the add-on preferences
  - Check webcam permissions for your operating system

### Low Performance
- **Issue**: Lag or stuttering during animation
- **Solution**:
  - Reduce camera resolution in the add-on preferences
  - Increase smoothing value
  - Disable unused features (face, hands, or pose)
  - Close other applications to free up resources

### Incorrect Bone Mapping
- **Issue**: Bones move incorrectly or not at all
- **Solution**:
  - Try a different mapping mode
  - Use manual mapping for problematic bones
  - Check that your armature is in rest position before mapping
  - Ensure the armature is selected in the 3D view

## Getting Help

If you encounter issues not covered here:
- Check the GitHub repository for known issues
- Join the community forum for user discussions
- Contact the developer directly for support

# Reference

## MediaPipe Landmark Indices

### Face Landmarks
- 0-67: Face contour
- 68-151: Right eye and eyebrow
- 152-234: Left eye and eyebrow
- 235-293: Nose
- 294-379: Mouth (outer and inner lips)
- 380-467: Additional facial features

### Hand Landmarks
- 0: Wrist
- 1-4: Thumb (from base to tip)
- 5-8: Index finger (from base to tip)
- 9-12: Middle finger (from base to tip)
- 13-16: Ring finger (from base to tip)
- 17-20: Pinky finger (from base to tip)

### Pose Landmarks
- 0: Nose
- 1-4: Left and right eyes
- 5-10: Left and right ears and mouth
- 11-12: Left and right shoulders
- 13-14: Left and right elbows
- 15-16: Left and right wrists
- 17-22: Left and right hands
- 23-24: Left and right hips
- 25-26: Left and right knees
- 27-28: Left and right ankles
- 29-32: Left and right feet

## Keyboard Shortcuts

- `N`: Open/close the sidebar in the 3D View
- `Ctrl+Z`: Undo changes to bone mappings
- `Ctrl+Shift+Z`: Redo changes to bone mappings
- `Spacebar`: Start/stop recording (when in the 3D View)

# Appendix

## Version History

- 1.0.0: Initial release
  - Complete MediaPipe integration (Face, Hands, Body)
  - Automatic and preset bone mapping
  - Manual mapping editor
  - Animation controls and visualization

## License

This add-on is released under the MIT License.

## Credits

- MediaPipe by Google: https://mediapipe.dev/
- Blender by Blender Foundation: https://www.blender.org/
- Developed by: [Your Name/Organization]

## Contact

For support, feature requests, or bug reports:
- GitHub: [Repository URL]
- Email: [Contact Email]
- Website: [Website URL]
