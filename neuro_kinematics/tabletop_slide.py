import time
from neuro_kinematics.base_movement import BaseMovement, MovementState

class TabletopSlideMovement(BaseMovement):
    def __init__(self):
        super().__init__()
        self.slide_target = 150.0
        self.retraction_target = 80.0
        # Y-axis tolerance for shoulder hiking
        self.shoulder_hike_threshold = 0.05

    def evaluate_stroke_kinematics(self, landmarks, mp_pose):
        left_shoulder = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
        right_shoulder = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER)
        left_elbow = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW)
        left_wrist = self.get_landmark_vector(landmarks, mp_pose.PoseLandmark.LEFT_WRIST)

        elbow_angle = self.compute_joint_angle(left_shoulder, left_elbow, left_wrist)
        
        # Smaller Y means higher in the image. This measures if the patient is raising their shoulder to compensate.
        shoulder_hike_val = right_shoulder[1] - left_shoulder[1]

        guidance_feedback = "Slide your hand forward across the table smoothly."
        safety_breach_alert = False

        # 1. INVALID / SAFETY TRAP
        if shoulder_hike_val > self.shoulder_hike_threshold:
            self.state = MovementState.INVALID
            guidance_feedback = "POSTURE WARNING: Relax your neck. Do not hike your shoulder to slide your arm."
            safety_breach_alert = True
            features = self.generate_feature_vector(elbow_angle, shoulder_hike_val, safety_breach_alert)
            return self.repetition_count, guidance_feedback, safety_breach_alert, features

        # 2. MICRO FSM TRANSITIONS
        if self.state in [MovementState.READY, MovementState.INVALID, MovementState.REP_COMPLETE]:
            if elbow_angle > self.retraction_target:
                self.state = MovementState.MOVING
                self.rep_start_time = time.time()
                
        elif self.state == MovementState.MOVING:
            if elbow_angle > self.slide_target:
                self.state = MovementState.TARGET_REACHED
                guidance_feedback = "Good slide distance. Now pull your hand back slowly."
                
        elif self.state == MovementState.TARGET_REACHED:
            if elbow_angle < self.slide_target:
                self.state = MovementState.RETURNING
                
        elif self.state == MovementState.RETURNING:
            if elbow_angle < self.retraction_target:
                self.state = MovementState.REP_COMPLETE
                self.repetition_count += 1
                guidance_feedback = "Repetition validated! Excellent control."
                # Reset ROM tracking for the next repetition
                self.min_angle, self.max_angle = 999.0, 0.0

        # 3. GENERATE ML FEATURES
        features = self.generate_feature_vector(elbow_angle, shoulder_hike_val, safety_breach_alert)
        return self.repetition_count, guidance_feedback, safety_breach_alert, features