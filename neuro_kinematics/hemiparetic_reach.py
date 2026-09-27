# Importing essential libraries for numerical computations and time tracking.
import time
from neuro_kinematics.base_movement import BaseMovement, MovementState

class HemipareticReachMovement(BaseMovement):
    # Kinematic FSM for Anterior MCA Stroke profiles. This primarily focuses on extension recovery and limits compensatory trunk leaning.
    def __init__(self):
        super().__init__()
        self.extension_target = 145.0  
        self.retraction_target = 60.0  
        # Trunk leaning > 25 degrees invalidates the repetition and prompts a warning
        self.compensatory_threshold = 25.0 

    def evaluate_stroke_kinematics(self, landmarks, mp_pose):
        shoulder = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
        elbow = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW)
        wrist = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_WRIST)
        hip = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_HIP)

        elbow_angle = self.compute_joint_angle(shoulder, elbow, wrist)
        trunk_lean = self.compute_trunk_angle(shoulder, hip)
        
        guidance_feedback = "Extend your arm forward slowly toward the target zone."
        safety_breach_alert = False

        # 1. This invalidates movement if patient leans forward instead of using arm muscles
        if trunk_lean > self.compensatory_threshold:
            self.state = MovementState.INVALID
            guidance_feedback = "POSTURE WARNING: Keep your torso straight. Push using your arm muscles, not your back."
            safety_breach_alert = True
            features = self.generate_feature_vector(elbow_angle, trunk_lean, safety_breach_alert)
            return self.repetition_count, guidance_feedback, safety_breach_alert, features

        # 2. MICRO FSM TRANSITIONS
        if self.state in [MovementState.READY, MovementState.INVALID, MovementState.REP_COMPLETE]:
            if elbow_angle > self.retraction_target:
                self.state = MovementState.MOVING
                self.rep_start_time = time.time()
                
        elif self.state == MovementState.MOVING:
            if elbow_angle > self.extension_target:
                self.state = MovementState.TARGET_REACHED
                guidance_feedback = "Good reach window achieved. Now return your arm back slowly."
                
        elif self.state == MovementState.TARGET_REACHED:
            if elbow_angle < self.extension_target:
                self.state = MovementState.RETURNING
                
        elif self.state == MovementState.RETURNING:
            if elbow_angle < self.retraction_target:
                self.state = MovementState.REP_COMPLETE
                self.repetition_count += 1
                guidance_feedback = "Repetition validated! Smooth motor control detected."
                # Reset ROM for next rep
                self.min_angle, self.max_angle = 999.0, 0.0

        # 3. GENERATING MACHINE LEARNING FEATURES
        features = self.generate_feature_vector(elbow_angle, trunk_lean, safety_breach_alert)
        return self.repetition_count, guidance_feedback, safety_breach_alert, features