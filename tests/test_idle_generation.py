import math
import unittest

from reachy_mini_home_assistant.motion.state_machine import (
    OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD,
    OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD,
    IdleGenerationConfig,
    build_generated_idle_pending_action,
)


class IdleGenerationTests(unittest.TestCase):
    def _config(self):
        return IdleGenerationConfig(
            yaw_range_deg=(-24.0, 24.0),
            pitch_range_deg=(-10.0, 9.0),
            roll_range_deg=(-8.0, 8.0),
            x_range_m=(-0.003, 0.003),
            y_range_m=(-0.003, 0.003),
            z_range_m=(-0.003, 0.006),
            antenna_variation_range_rad=(-0.06, 0.06),
            duration_range_s=(3.0, 6.0),
            opposite_direction_bias=0.68,
            micro_motion_probability=0.0,
            min_repeat_distance=0.35,
        )

    def test_generated_idle_is_slow_visible_and_avoids_zero_antennas(self):
        action, signature = build_generated_idle_pending_action(self._config())

        self.assertGreaterEqual(action.duration, 3.0)
        self.assertLessEqual(action.duration, 6.0)
        self.assertGreater(action.target_antenna_left, math.radians(6.0))
        self.assertLess(action.target_antenna_right, -math.radians(6.0))
        self.assertAlmostEqual(signature[6], action.target_antenna_left)
        self.assertAlmostEqual(signature[7], action.target_antenna_right)
        self.assertNotAlmostEqual(action.target_antenna_left, 0.0)
        self.assertNotAlmostEqual(action.target_antenna_right, 0.0)

    def test_generated_idle_antennas_stay_around_official_neutral(self):
        for _ in range(20):
            action, _ = build_generated_idle_pending_action(self._config())
            self.assertLess(abs(action.target_antenna_left - OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD), 0.061)
            self.assertLess(abs(action.target_antenna_right - OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD), 0.061)


if __name__ == "__main__":
    unittest.main()
