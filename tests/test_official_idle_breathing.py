import math
import unittest
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

        expected_z = OFFICIAL_BREATHING_Z_AMPLITUDE_M * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_FREQUENCY_HZ * 0.25
        )
        expected_sway = OFFICIAL_BREATHING_ANTENNA_AMPLITUDE_RAD * math.sin(
            2.0 * math.pi * OFFICIAL_BREATHING_ANTENNA_FREQUENCY_HZ * 0.25
        )

        self.assertAlmostEqual(offsets["z"], expected_z)
        self.assertAlmostEqual(offsets["antenna_left"], expected_sway)
        self.assertAlmostEqual(offsets["antenna_right"], -expected_sway)


if __name__ == "__main__":
    unittest.main()
