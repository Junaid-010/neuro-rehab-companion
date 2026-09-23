from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
import time

# =====================================================================
# MICRO FSM: FORMAL KINEMATIC STATES (Stage 15)
# =====================================================================
class MovementState(Enum):
    READY = "READY"
    MOVING = "MOVING"
    TARGET_REACHED = "TARGET_REACHED"
    RETURNING = "RETURNING"
    REP_COMPLETE = "REP_COMPLETE"
    INVALID = "INVALID"

class BaseMovement(ABC):
    def __init__(self):
        # FSM State Tracking
        self.repetition_count = 0
        self.state = MovementState.READY
        
        # Temporal Tracking for ML Features
        self.last_frame_time = time.time()
        self.rep_start_time = None
        self.last_angle = 0.0
        
        # Range of Motion (ROM) Tracking
        self.min_angle = 999.0
        self.max_angle = 0.0

    @staticmethod
    def landmark_to_vector(landmark):
        return np.array([landmark.x, landmark.y, landmark.z], dtype=np.float64)

    def get_landmark_vector(self, landmarks, landmark_enum):
        return self.landmark_to_vector(landmarks[landmark_enum.value])

    @staticmethod
    def compute_joint_angle(point_top, point_vertex, point_bottom):
        a, b, c = np.asarray(point_top), np.asarray(point_vertex), np.asarray(point_bottom)
        v_ba, v_bc = a - b, c - b
        n_ba, n_bc = np.linalg.norm(v_ba), np.linalg.norm(v_bc)
        if n_ba < 1e-8 or n_bc < 1e-8: return 0.0
        cos_theta = np.clip(np.dot(v_ba, v_bc) / (n_ba * n_bc), -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_theta)))

    @staticmethod
    def compute_trunk_angle(shoulder, hip):
        torso = np.asarray(shoulder) - np.asarray(hip)
        vertical = np.array([0.0, -1.0, 0.0])
        norm_t = np.linalg.norm(torso)
        if norm_t < 1e-8: return 0.0
        cos_theta = np.clip(np.dot(torso, vertical) / norm_t, -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_theta)))

    # =====================================================================
    # 10-POINT ML FEATURE CONTRACT (Stage 16)
    # =====================================================================
    def generate_feature_vector(self, current_angle, compensation, safety_flag):
        """Generates the structured ML-ready numerical feature vector."""
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        
        # Avoid division by zero on the first frame
        if delta_time > 0:
            angular_velocity = abs(current_angle - self.last_angle) / delta_time
        else:
            angular_velocity = 0.0
            
        # Update ROM
        self.min_angle = min(self.min_angle, current_angle)
        self.max_angle = max(self.max_angle, current_angle)
        rom = self.max_angle - self.min_angle

        # Repetition Duration
        rep_duration = (current_time - self.rep_start_time) if self.rep_start_time else 0.0

        features = {
            'joint_angle': current_angle,
            'compensation_metric': compensation,
            'safety_flag': safety_flag,
            'movement_stage': self.state.value,
            'timestamp': current_time,
            'delta_time': delta_time,
            'angular_velocity': angular_velocity,
            'repetition_count': self.repetition_count,
            'repetition_duration': rep_duration,
            'range_of_motion': rom
        }
        
        # Update trackers for next frame
        self.last_frame_time = current_time
        self.last_angle = current_angle
        
        return features

    @abstractmethod
    def evaluate_stroke_kinematics(self, landmarks, mp_pose):
        """Must return: reps, feedback, safety_breach, ml_feature_dict"""
        pass