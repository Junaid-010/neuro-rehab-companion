import unittest
from neuro_kinematics.hemiparetic_reach import HemipareticReachMovement
from neuro_kinematics.base_movement import MovementState

class TestHemipareticReachFSM(unittest.TestCase):
    
    def setUp(self):
        self.module = HemipareticReachMovement()
        
        # Create a mock mp_pose and landmarks structure to simulate MediaPipe returns
        # Assign DISTINCT indices to each landmark so the engine can pull the right coordinates
        class MockEnum:
            def __init__(self, val):
                self.value = val
                
        class MockMPPose:
            class PoseLandmark:
                LEFT_SHOULDER = MockEnum(0)
                LEFT_ELBOW = MockEnum(1)
                LEFT_WRIST = MockEnum(2)
                LEFT_HIP = MockEnum(3)
                
        self.mp_pose = MockMPPose()
        
    def create_mock_landmarks(self, angle):
        """Simulate MediaPipe returning specific 3D coordinates to force a joint angle."""
        class MockLandmark:
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z
                
        import math
        # Geometry trick: Place elbow at origin, shoulder at (0,1), and wrist based on desired angle
        rad = math.radians(angle)
        return [
            MockLandmark(0, 1, 0),                        # 0: LEFT_SHOULDER
            MockLandmark(0, 0, 0),                        # 1: LEFT_ELBOW
            MockLandmark(math.sin(rad), math.cos(rad), 0),# 2: LEFT_WRIST
            MockLandmark(0, 2, 0)                         # 3: LEFT_HIP (straight down = 0 trunk lean)
        ]

    def test_fsm_lifecycle(self):
        """Test the strict sequential flow of the FSM."""
        # 1. Start in READY
        self.assertEqual(self.module.state, MovementState.READY)
        
        # 2. Simulate extending past retraction target (60 deg) -> MOVING
        landmarks = self.create_mock_landmarks(90.0)
        self.module.evaluate_stroke_kinematics(landmarks, self.mp_pose)
        self.assertEqual(self.module.state, MovementState.MOVING)
        
        # 3. Simulate extending past target (145 deg) -> TARGET_REACHED
        landmarks = self.create_mock_landmarks(160.0)
        self.module.evaluate_stroke_kinematics(landmarks, self.mp_pose)
        self.assertEqual(self.module.state, MovementState.TARGET_REACHED)
        
        # 4. Simulate pulling arm back slightly -> RETURNING
        landmarks = self.create_mock_landmarks(120.0)
        self.module.evaluate_stroke_kinematics(landmarks, self.mp_pose)
        self.assertEqual(self.module.state, MovementState.RETURNING)
        
        # 5. Simulate full retraction (< 60 deg) -> REP_COMPLETE
        landmarks = self.create_mock_landmarks(40.0)
        self.module.evaluate_stroke_kinematics(landmarks, self.mp_pose)
        self.assertEqual(self.module.state, MovementState.REP_COMPLETE)
        self.assertEqual(self.module.repetition_count, 1)

if __name__ == '__main__':
    unittest.main()