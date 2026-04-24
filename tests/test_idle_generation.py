import math
import random
import types
import unittest
from collections import deque
from unittest.mock import patch

from reachy_mini_home_assistant.motion.idle_runtime import enqueue_generated_idle_cycle
from reachy_mini_home_assistant.motion.state_machine import (
    OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD,
    OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD,
    IdleGenerationConfig,
    build_generated_idle_pending_action,
)


class IdleGenerationTests(unittest.TestCase):
    def _config(self):
        return IdleGenerationConfig(
            yaw_range_deg=(-20.0, 20.0),
            pitch_range_deg=(-8.0, 7.0),
            roll_range_deg=(-6.0, 6.0),
            x_range_m=(-0.003, 0.003),
            y_range_m=(-0.003, 0.003),
            z_range_m=(-0.002, 0.006),
            antenna_variation_range_rad=(-0.06, 0.06),
            duration_range_s=(2.2, 4.2),
            hold_range_s=(0.35, 0.9),
            return_duration_range_s=(1.0, 1.8),
            fade_out_duration_range_s=(0.55, 0.85),
            opposite_direction_bias=0.68,
            micro_motion_probability=0.0,
            min_repeat_distance=0.35,
        )

    def test_generated_idle_is_slow_visible_and_avoids_zero_antennas(self):
        action, signature = build_generated_idle_pending_action(self._config())

        self.assertGreaterEqual(action.duration, 2.2)
        self.assertLessEqual(action.duration, 4.2)
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

    def test_generated_idle_cycle_crossfades_holds_and_returns_to_neutral(self):
        action, _ = build_generated_idle_pending_action(self._config())
        manager = types.SimpleNamespace(
            _idle_generation_config=self._config(),
            _idle_action_queue=deque(),
            state=types.SimpleNamespace(
                target_pitch=0.01,
                target_yaw=0.02,
                target_roll=0.03,
                target_x=0.001,
                target_y=-0.001,
                target_z=0.002,
                target_antenna_left=OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD,
                target_antenna_right=OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD,
            ),
        )

        with patch.object(random, "uniform", side_effect=[0.7, 0.5, 1.2]):
            queued_duration = enqueue_generated_idle_cycle(manager, action)

        names = [item.name for item in manager._idle_action_queue]
        self.assertEqual(
            names,
            [
                "idle_generated_fade_out",
                "idle_generated",
                "idle_generated_hold",
                "idle_generated_return",
            ],
        )
        self.assertAlmostEqual(queued_duration, 0.7 + action.duration + 0.5 + 1.2)
        self.assertAlmostEqual(manager._idle_action_queue[2].target_yaw, action.target_yaw)
        self.assertEqual(manager._idle_action_queue[3].target_yaw, 0.0)
        self.assertEqual(manager._idle_action_queue[3].target_z, 0.0)
        self.assertAlmostEqual(
            manager._idle_action_queue[3].target_antenna_left,
            OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD,
        )


if __name__ == "__main__":
    unittest.main()
