#!/usr/bin/env python3
"""
Test script for MediaPipe functionality.
This script tests the basic functionality of MediaPipe for face, hand, and pose detection.
"""

import cv2
import mediapipe as mp
import numpy as np
import time

def test_face_detection():
    """Test MediaPipe face detection and landmark functionality."""
    print("Testing MediaPipe Face Landmarker...")
    
    # Initialize MediaPipe Face Landmarker
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        
        # Test for 5 seconds
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 5:
            success, image = cap.read()
            if not success:
                print("Failed to capture image from webcam.")
                break
                
            # Convert the image to RGB and process it with MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image_rgb)
            
            frame_count += 1
            
            # Draw face landmarks
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                    )
            
            # Display the image
            cv2.imshow('MediaPipe Face Mesh Test', image)
            if cv2.waitKey(5) & 0xFF == 27:  # ESC key
                break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"Face detection test completed. Processed {frame_count} frames in 5 seconds.")
    print(f"Average FPS: {frame_count / 5:.2f}")
    
    return frame_count > 0

def test_hand_detection():
    """Test MediaPipe hand detection and landmark functionality."""
    print("Testing MediaPipe Hand Landmarker...")
    
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        # Test for 5 seconds
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 5:
            success, image = cap.read()
            if not success:
                print("Failed to capture image from webcam.")
                break
                
            # Convert the image to RGB and process it with MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)
            
            frame_count += 1
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
            
            # Display the image
            cv2.imshow('MediaPipe Hands Test', image)
            if cv2.waitKey(5) & 0xFF == 27:  # ESC key
                break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"Hand detection test completed. Processed {frame_count} frames in 5 seconds.")
    print(f"Average FPS: {frame_count / 5:.2f}")
    
    return frame_count > 0

def test_pose_detection():
    """Test MediaPipe pose detection and landmark functionality."""
    print("Testing MediaPipe Pose Landmarker...")
    
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        
        # Test for 5 seconds
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 5:
            success, image = cap.read()
            if not success:
                print("Failed to capture image from webcam.")
                break
                
            # Convert the image to RGB and process it with MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            frame_count += 1
            
            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            # Display the image
            cv2.imshow('MediaPipe Pose Test', image)
            if cv2.waitKey(5) & 0xFF == 27:  # ESC key
                break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"Pose detection test completed. Processed {frame_count} frames in 5 seconds.")
    print(f"Average FPS: {frame_count / 5:.2f}")
    
    return frame_count > 0

def main():
    """Run all MediaPipe tests."""
    print("Starting MediaPipe tests...")
    
    # Test face detection
    face_success = test_face_detection()
    
    # Test hand detection
    hand_success = test_hand_detection()
    
    # Test pose detection
    pose_success = test_pose_detection()
    
    # Print summary
    print("\nTest Summary:")
    print(f"Face Detection: {'Success' if face_success else 'Failed'}")
    print(f"Hand Detection: {'Success' if hand_success else 'Failed'}")
    print(f"Pose Detection: {'Success' if pose_success else 'Failed'}")
    
    if face_success and hand_success and pose_success:
        print("\nAll MediaPipe tests passed successfully!")
    else:
        print("\nSome MediaPipe tests failed. Please check the output above for details.")

if __name__ == "__main__":
    main()
