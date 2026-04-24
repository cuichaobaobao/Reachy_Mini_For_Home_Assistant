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
    build_generated_idle_action_sequence,
    build_generated_idle_pending_action,
)


class IdleGenerationTests(unittest.TestCase):
    def _config(self):
        return IdleGenerationConfig(
            yaw_range_deg=(-28.0, 28.0),
            pitch_range_deg=(-10.0, 10.0),
            roll_range_deg=(-8.0, 8.0),
            x_range_m=(-0.004, 0.004),
            y_range_m=(-0.004, 0.004),
            z_range_m=(-0.006, 0.014),
            antenna_variation_range_rad=(-0.06, 0.06),
            duration_range_s=(5.8, 8.6),
            hold_range_s=(0.8, 1.6),
            return_duration_range_s=(1.8, 2.8),
            fade_out_duration_range_s=(0.25, 0.45),
            opposite_direction_bias=0.68,
            micro_motion_probability=0.0,
            min_repeat_distance=0.35,
        )

    def test_generated_idle_is_slow_visible_and_uses_official_neutral_antennas(self):
        action, signature = build_generated_idle_pending_action(self._config())

        self.assertGreaterEqual(action.duration, 5.8)
        self.assertLessEqual(action.duration, 8.6)
        self.assertAlmostEqual(action.target_antenna_left, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD)
        self.assertAlmostEqual(action.target_antenna_right, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD)
        self.assertAlmostEqual(signature[6], action.target_antenna_left)
        self.assertAlmostEqual(signature[7], action.target_antenna_right)
        self.assertNotAlmostEqual(action.target_antenna_left, 0.0)
        self.assertNotAlmostEqual(action.target_antenna_right, 0.0)

    def test_generated_idle_antennas_are_fixed_official_neutral(self):
        for _ in range(20):
            action, _ = build_generated_idle_pending_action(self._config())
            self.assertAlmostEqual(action.target_antenna_left, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD)
            self.assertAlmostEqual(action.target_antenna_right, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD)

    def test_generated_idle_sequence_has_rich_slow_continuous_steps(self):
        actions, _ = build_generated_idle_action_sequence(self._config())

        self.assertGreaterEqual(len(actions), 4)
        self.assertLessEqual(len(actions), 6)
        self.assertTrue(all(action.name.startswith("idle_generated_") for action in actions))
        self.assertGreaterEqual(sum(action.duration for action in actions), 5.8)
        self.assertLessEqual(sum(action.duration for action in actions), 8.6)
        self.assertTrue(any(abs(action.target_yaw) > 0.15 for action in actions))
        self.assertTrue(any(action.target_pitch < -0.07 for action in actions))
        self.assertTrue(any(action.target_pitch > 0.07 for action in actions))
        self.assertTrue(any(action.target_z > 0.007 for action in actions))
        self.assertTrue(any(action.target_z < -0.001 for action in actions))
        for action in actions:
            self.assertAlmostEqual(action.target_antenna_left, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD)
            self.assertAlmostEqual(action.target_antenna_right, OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD)

    def test_generated_idle_cycle_crossfades_runs_sequence_holds_and_returns_to_neutral(self):
        actions, _ = build_generated_idle_action_sequence(self._config())
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
            queued_duration = enqueue_generated_idle_cycle(manager, actions)

        names = [item.name for item in manager._idle_action_queue]
        self.assertEqual(
            names,
            [
                "idle_generated_fade_out",
                *[action.name for action in actions],
                "idle_generated_hold",
                "idle_generated_return",
            ],
        )
        self.assertAlmostEqual(queued_duration, 0.7 + sum(action.duration for action in actions) + 0.5 + 1.2)
        hold_index = 1 + len(actions)
        return_index = hold_index + 1
        self.assertAlmostEqual(manager._idle_action_queue[hold_index].target_yaw, actions[-1].target_yaw)
        self.assertEqual(manager._idle_action_queue[return_index].target_yaw, 0.0)
        self.assertEqual(manager._idle_action_queue[return_index].target_z, 0.0)
        self.assertAlmostEqual(
            manager._idle_action_queue[return_index].target_antenna_left,
            OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD,
        )


if __name__ == "__main__":
    unittest.main()
