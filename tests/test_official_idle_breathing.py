import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

from reachy_mini_home_assistant.motion import animation_player as animation_player_module
from reachy_mini_home_assistant.motion.animation_player import AnimationPlayer
from reachy_mini_home_assistant.motion.state_machine import (
    OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD,
    OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ,
    OFFICIAL_BREATHING_FREQUENCY_HZ,
    OFFICIAL_BREATHING_Z_AMPLITUDE_M,
)


class _Clock:
    def __init__(self, value: float = 0.0):
        self.value = value

    def perf_counter(self) -> float:
        return self.value


class OfficialIdleBreathingTests(unittest.TestCase):
    def test_idle_animation_layer_matches_official_breathing_formula(self):
        clock = _Clock(100.0)
        with patch.object(animation_player_module.time, "perf_counter", clock.perf_counter):
            player = AnimationPlayer()
            self.assertTrue(player.set_animation("idle"))

            clock.value += player._transition_duration + player._interpolation_duration
            player.get_offsets()
            clock.value += 0.25
            offsets = player.get_offsets()

        elapsed = player._transition_duration + player._interpolation_duration + 0.25
        expected_z = OFFICIAL_BREATHING_Z_AMPLITUDE_M * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_FREQUENCY_HZ * elapsed
        )
        expected_sway = OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ * elapsed
        )

        self.assertAlmostEqual(offsets["z"], expected_z)
        self.assertAlmostEqual(offsets["antenna_left"], expected_sway)
        self.assertAlmostEqual(offsets["antenna_right"], -expected_sway)

    def test_voice_state_animation_crossfades_without_zero_interpolation(self):
        clock = _Clock(100.0)
        with (
            patch.object(animation_player_module.time, "perf_counter", clock.perf_counter),
            patch.object(animation_player_module.random, "random", return_value=0.0),
        ):
            player = AnimationPlayer()
            player._current_animation = "listening"
            player._target_animation = "listening"
            player._last_offsets = player._zero_offsets()
            player._last_offsets["pitch"] = 0.1

            self.assertTrue(player.set_animation("thinking"))
            self.assertFalse(player._in_interpolation)

            clock.value += player._transition_duration / 2.0
            offsets = player.get_offsets()

        self.assertGreater(offsets["pitch"], 0.03)

    def test_speaking_antenna_wiggle_matches_official_breathing_antenna_timing(self):
        config = json.loads(Path("reachy_mini_home_assistant/animations/conversation_animations.json").read_text())
        speaking = config["animations"]["speaking"]

        self.assertEqual(speaking["antenna_move_name"], "wiggle")
        self.assertAlmostEqual(speaking["antenna_amplitude_rad"], OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD)
        self.assertAlmostEqual(speaking["antenna_frequency_hz"], OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ)
        self.assertAlmostEqual(speaking["frequency_hz"], OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ)

    def test_disabled_idle_rest_pose_uses_historical_sleep_posture(self):
        config = json.loads(Path("reachy_mini_home_assistant/animations/conversation_animations.json").read_text())
        rest = config["idle_rest_pose"]

        self.assertAlmostEqual(rest["pitch_deg"], 16.0)
        self.assertAlmostEqual(rest["antenna_left_rad"], 3.05)
        self.assertAlmostEqual(rest["antenna_right_rad"], -3.05)


if __name__ == "__main__":
    unittest.main()
