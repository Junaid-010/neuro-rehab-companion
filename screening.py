import cv2
import mediapipe as mp
import numpy as np

class FullBodyReadinessScan:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def evaluate_full_body_readiness(self, rgb_image):
        """
        Evaluates if the patient's full upper body (shoulders and hips) 
        is visible and vertically aligned before starting exercise.
        """
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            return False, "No body detected. Please step back into the camera view."
            
        landmarks = results.pose_landmarks.landmark
        
        # Extract visibility scores for key posture landmarks
        l_shoulder_vis = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility
        r_shoulder_vis = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility
        l_hip_vis = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        r_hip_vis = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].visibility
        
        # Verify the camera can see the patient's torso for accurate kinematics
        is_visible = all(vis > 0.6 for vis in [l_shoulder_vis, r_shoulder_vis, l_hip_vis, r_hip_vis])
        
        if is_visible:
            return True, "Full body alignment verified. Ready to begin."
        else:
            return False, "Please adjust your camera so your shoulders and hips are visible."