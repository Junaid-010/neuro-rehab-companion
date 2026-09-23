import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from screening import FullBodyReadinessScan

class TestFullBodyReadinessScan(unittest.TestCase):
    def setUp(self):
        self.screener = FullBodyReadinessScan()
        # Create a dummy image matrix (640x480 RGB) to simulate a webcam frame
        self.dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def create_mock_pose_result(self, l_sh, r_sh, l_hip, r_hip):
        """Generates a mock MediaPipe Pose result object with specific visibility scores."""
        mock_result = MagicMock()
        mock_landmarks = MagicMock()
        
        # 11, 12, 23, 24 are the exact MediaPipe Enum indices for shoulders and hips
        mock_landmarks.landmark = {
            11: MagicMock(visibility=l_sh),
            12: MagicMock(visibility=r_sh),
            23: MagicMock(visibility=l_hip),
            24: MagicMock(visibility=r_hip)
        }
        mock_result.pose_landmarks = mock_landmarks
        return mock_result

    @patch('mediapipe.solutions.pose.Pose.process')
    def test_optimal_clinical_positioning(self, mock_process):
        """Prove the screener passes when the patient's full torso is in frame."""
        # Inject mock data: All visibilities > 0.8
        mock_process.return_value = self.create_mock_pose_result(0.9, 0.85, 0.95, 0.88)
        
        is_safe, msg = self.screener.evaluate_full_body_readiness(self.dummy_frame)
        
        self.assertTrue(is_safe)
        self.assertEqual(msg, "Full body alignment verified. Ready to begin.")

    @patch('mediapipe.solutions.pose.Pose.process')
    def test_truncation_error_hips_occluded(self, mock_process):
        """Prove the screener halts execution if the patient is sitting too close to the camera."""
        # Shoulders are highly visible (0.9), but Hips are occluded/cut off (0.2)
        mock_process.return_value = self.create_mock_pose_result(0.9, 0.9, 0.2, 0.2)
        
        is_safe, msg = self.screener.evaluate_full_body_readiness(self.dummy_frame)
        
        self.assertFalse(is_safe)
        self.assertIn("shoulders and hips are visible", msg)

    @patch('mediapipe.solutions.pose.Pose.process')
    def test_lateral_occlusion_off_center(self, mock_process):
        """Prove the screener halts execution if the patient stands too far left/right."""
        # Left side is visible, Right side is completely off-screen
        mock_process.return_value = self.create_mock_pose_result(0.9, 0.1, 0.9, 0.1)
        
        is_safe, msg = self.screener.evaluate_full_body_readiness(self.dummy_frame)
        self.assertFalse(is_safe)

    @patch('mediapipe.solutions.pose.Pose.process')
    def test_null_detection_no_human(self, mock_process):
        """Prove the screener handles empty frames gracefully without crashing."""
        # MediaPipe returns None when it can't find a human
        mock_empty_result = MagicMock()
        mock_empty_result.pose_landmarks = None
        mock_process.return_value = mock_empty_result
        
        is_safe, msg = self.screener.evaluate_full_body_readiness(self.dummy_frame)
        
        self.assertFalse(is_safe)
        self.assertEqual(msg, "No body detected. Please step back into the camera view.")

if __name__ == '__main__':
    unittest.main()