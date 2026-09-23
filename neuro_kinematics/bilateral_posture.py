import time
from neuro_kinematics.base_movement import BaseMovement, MovementState

class BilateralPostureMovement(BaseMovement):
    def __init__(self):
        super().__init__()
        # Maximum allowed difference between left/right wrist vertical positions
        self.symmetry_threshold = 0.08
        # Maximum allowed difference between left/right elbow angles
        self.angle_symmetry_threshold = 20.0
        
        self.extension_target = 120.0
        self.retraction_target = 60.0

    def evaluate_stroke_kinematics(self, landmarks, mp_pose):
        left_shoulder = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
        left_elbow = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW)
        left_wrist = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_WRIST)
        
        right_shoulder = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER)
        right_elbow = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW)
        right_wrist = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST)

        height_diff = abs(left_wrist[1] - right_wrist[1])
        left_arm_angle = self.compute_joint_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.compute_joint_angle(right_shoulder, right_elbow, right_wrist)
        
        angle_difference = abs(left_arm_angle - right_arm_angle)
        average_arm_angle = (left_arm_angle + right_arm_angle) / 2.0

        guidance_feedback = "Raise both arms together symmetrically."
        safety_breach_alert = False
        compensation_metric = max(height_diff, angle_difference)

        # 1. INVALID / SAFETY TRAP
        if height_diff > self.symmetry_threshold or angle_difference > self.angle_symmetry_threshold:
            self.state = MovementState.INVALID
            guidance_feedback = "COORDINATION WARNING: Your arms are uneven. Balance your movement."
            safety_breach_alert = True
            features = self.generate_feature_vector(average_arm_angle, compensation_metric, safety_breach_alert)
            return self.repetition_count, guidance_feedback, safety_breach_alert, features

        # 2. MICRO FSM TRANSITIONS
        if self.state in [MovementState.READY, MovementState.INVALID, MovementState.REP_COMPLETE]:
            if average_arm_angle > self.retraction_target:
                self.state = MovementState.MOVING
                self.rep_start_time = time.time()
                
        elif self.state == MovementState.MOVING:
            if average_arm_angle > self.extension_target:
                self.state = MovementState.TARGET_REACHED
                guidance_feedback = "Good bilateral alignment. Now slowly return your arms."
                
        elif self.state == MovementState.TARGET_REACHED:
            if average_arm_angle < self.extension_target:
                self.state = MovementState.RETURNING
                
        elif self.state == MovementState.RETURNING:
            if average_arm_angle < self.retraction_target:
                self.state = MovementState.REP_COMPLETE
                self.repetition_count += 1
                guidance_feedback = "Repetition validated! Great bilateral symmetry."
                # Reset ROM tracking for the next repetition
                self.min_angle, self.max_angle = 999.0, 0.0

        # 3. GENERATE ML FEATURES
        features = self.generate_feature_vector(average_arm_angle, compensation_metric, safety_breach_alert)
        return self.repetition_count, guidance_feedback, safety_breach_alert, features