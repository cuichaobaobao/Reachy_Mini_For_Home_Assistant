import math
import types
import unittest

import numpy as np

from reachy_mini_home_assistant.motion.control_runtime import evaluate_official_idle_breathing
from reachy_mini_home_assistant.motion.pose_composer import create_head_pose_matrix
from reachy_mini_home_assistant.motion.state_machine import (
    OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD,
    OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ,
    OFFICIAL_BREATHING_FREQUENCY_HZ,
    OFFICIAL_BREATHING_INTERPOLATION_DURATION_S,
    OFFICIAL_BREATHING_Z_AMPLITUDE_M,
    RobotState,
)


class _Robot:
    def get_current_joint_positions(self):
        return {}, (-0.12, 0.08)

    def get_current_head_pose(self):
        return create_head_pose_matrix(z=0.002)


class OfficialIdleBreathingTests(unittest.TestCase):
    def _make_manager(self, now):
        return types.SimpleNamespace(
            state=types.SimpleNamespace(robot_state=RobotState.IDLE, look_around_in_progress=False),
            _idle_motion_enabled=True,
            _idle_antenna_enabled=True,
            _pending_action=None,
            _idle_action_queue=[],
            _now=lambda: now,
            robot=_Robot(),
            _last_sent_head_pose=None,
            _last_sent_antennas=None,
            _official_idle_breathing_active=False,
            _official_idle_breathing_start_time=0.0,
            _official_idle_breathing_start_head_pose=None,
            _official_idle_breathing_start_antennas=None,
        )

    def test_continuous_phase_matches_official_breathing_formula(self):
        manager = self._make_manager(now=10.0)
        fallback_head = np.eye(4)
        fallback_antennas = (0.0, 0.0)

        evaluate_official_idle_breathing(manager, fallback_head, fallback_antennas)
        manager._now = lambda: 10.0 + OFFICIAL_BREATHING_INTERPOLATION_DURATION_S + 0.25

        head, antennas, body_yaw = evaluate_official_idle_breathing(manager, fallback_head, fallback_antennas)

        expected_z = OFFICIAL_BREATHING_Z_AMPLITUDE_M * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_FREQUENCY_HZ * 0.25
        )
        expected_sway = OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ * 0.25
        )

        self.assertAlmostEqual(float(head[2, 3]), expected_z)
        self.assertAlmostEqual(antennas[0], expected_sway)
        self.assertAlmostEqual(antennas[1], -expected_sway)
        self.assertEqual(body_yaw, 0.0)


if __name__ == "__main__":
    unittest.main()
