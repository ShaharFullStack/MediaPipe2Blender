# MediaPipe to Blender Live Animation Add-on

This Blender add-on enables real-time animation of armature bones in Blender using MediaPipe's motion capture capabilities. It captures face, hand, and body landmarks from a webcam and maps them to Blender armature bones for live animation.

## Features

- **Complete MediaPipe Integration**: Includes all MediaPipe features such as Hands, Face, and Body landmark detection
- **Real-time Animation**: Animate Blender armatures in real-time while working in Blender
- **Automatic Bone Mapping**: Automatically maps MediaPipe landmarks to Blender armature bones
- **Preset Mappings**: Includes preset mappings for popular rigs like Rigify and Mixamo
- **Manual Mapping**: Provides a manual mapping editor for custom rigs
- **Animation Controls**: Includes controls for smoothing, influence factors, and keyframing
- **Visualization**: Visualize MediaPipe landmarks in the 3D viewport

## Installation

### Requirements

- Blender 2.93 or newer
- Python 3.7 or newer
- Webcam or video input device

### Installation Steps

1. Download the add-on ZIP file (`mediapipe_mocap.zip`)
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install..." and select the downloaded ZIP file
4. Enable the add-on by checking the box next to "Animation: MediaPipe Motion Capture"
5. The first time you use the add-on, it will automatically install required Python packages (MediaPipe, OpenCV, ZeroMQ)

## Usage

### Quick Start

1. Open the MediaPipe MoCap panel in the 3D View sidebar (press N to show the sidebar)
2. Select your target armature in the Bone Mapping panel
3. Choose a mapping mode (Auto, Preset, or Manual)
4. Click "Create Mapping" to generate bone mappings
5. Click "Connect" in the Status panel to start the MediaPipe connection
6. Click "Start Recording" in the Animation Settings panel to begin animating

### Bone Mapping

The add-on provides three ways to map MediaPipe landmarks to Blender armature bones:

1. **Auto Mapping**: Automatically maps landmarks based on bone names
2. **Preset Mapping**: Uses predefined mappings for popular rigs (Rigify, Mixamo)
3. **Manual Mapping**: Allows you to manually map each bone to specific landmarks

To use manual mapping:
1. Select "Manual" mapping mode
2. Add bone mappings using the "+" button
3. Select a bone from your armature
4. Choose the landmark type (Face, Hand, Pose) and index
5. Click "Apply Bone Mappings" to apply your changes

### Animation Settings

The Animation Settings panel provides controls for:

- **Auto Keyframe**: Automatically insert keyframes during recording
- **Keyframe Interval**: Number of frames between keyframes
- **Smoothing**: Amount of smoothing applied to the animation (0.0 - 1.0)
- **Influence**: Control how much each landmark type affects the animation

### Status and Controls

The Status panel shows:
- Connection status
- Frame count and FPS
- Error messages (if any)

Use the Connect/Disconnect and Start/Stop Recording buttons to control the animation process.

## Troubleshooting

### Common Issues

1. **MediaPipe Not Available**: Make sure you have an internet connection when first using the add-on, as it needs to download MediaPipe and other dependencies.

2. **Camera Not Found**: Ensure your webcam is connected and not being used by another application.

3. **Low Performance**: If you experience lag, try:
   - Reducing the camera resolution in the add-on preferences
   - Increasing the keyframe interval
   - Disabling features you don't need (e.g., face detection if you're only animating body)

4. **Mapping Issues**: If bones aren't moving correctly:
   - Check that your armature is selected
   - Try a different mapping mode
   - Use manual mapping for problematic bones

### Getting Help

If you encounter issues not covered here, please report them on the GitHub repository or contact the developer.

## License

This add-on is released under the MIT License. See the LICENSE file for details.

## Credits

- MediaPipe by Google: https://mediapipe.dev/
- Blender by Blender Foundation: https://www.blender.org/
- Developed by: [Your Name/Organization]

## Version History

- 1.0.0: Initial release
