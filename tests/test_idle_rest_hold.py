import types
import unittest
from unittest.mock import patch

from reachy_mini_home_assistant.motion import reachy_motion
from reachy_mini_home_assistant.motion.reachy_motion import ReachyMiniMotion
from reachy_mini_home_assistant.motion.state_machine import RobotState


class FakeTimer:
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.cancelled = False
        self.daemon = False

    def start(self):
        return None

    def cancel(self):
        self.cancelled = True

    def fire(self):
        if not self.cancelled:
            self.callback()


class FakeMovementManager:
    def __init__(self, *, idle_enabled=False):
        self.state = types.SimpleNamespace(robot_state=RobotState.SPEAKING)
        self._idle_enabled = idle_enabled
        self._manual_head_yaw_hold = False
        self.calls = []

    def set_state(self, state):
        self.state.robot_state = state
        self.calls.append(("set_state", state))

    def get_idle_behavior_enabled(self):
        return self._idle_enabled

    def reset_to_neutral(self, duration=0.5):
        self.calls.append(("reset_to_neutral", duration))

    def transition_to_idle_rest(self, duration=2.0):
        self.calls.append(("transition_to_idle_rest", duration))


class IdleRestHoldTests(unittest.TestCase):
    def _make_motion(self, manager):
        motion = object.__new__(ReachyMiniMotion)
        motion.reachy_mini = None
        motion._movement_manager = manager
        motion._is_speaking = False
        motion._idle_rest_delay_timer = None
        motion._idle_rest_delay_generation = 0
        return motion

    def test_idle_disabled_holds_neutral_before_entering_rest_pose(self):
        manager = FakeMovementManager(idle_enabled=False)
        motion = self._make_motion(manager)

        with patch.object(reachy_motion.threading, "Timer", FakeTimer):
            motion.on_idle()
            timer = motion._idle_rest_delay_timer
            self.assertIsNotNone(timer)
            self.assertEqual(timer.delay, reachy_motion.IDLE_REST_HOLD_DELAY_S)
            self.assertIn(("set_state", RobotState.IDLE), manager.calls)
            self.assertIn(("reset_to_neutral", 1.0), manager.calls)
            self.assertNotIn(("transition_to_idle_rest", 2.6), manager.calls)
            timer.fire()

        self.assertIn(("transition_to_idle_rest", 2.6), manager.calls)

    def test_new_listening_state_cancels_pending_idle_rest(self):
        manager = FakeMovementManager(idle_enabled=False)
        motion = self._make_motion(manager)

        with patch.object(reachy_motion.threading, "Timer", FakeTimer):
            motion.on_idle()
            timer = motion._idle_rest_delay_timer
            motion.on_listening()
            timer.fire()

        self.assertTrue(timer.cancelled)
        self.assertNotIn(("transition_to_idle_rest", 2.6), manager.calls)
        self.assertEqual(manager.calls[-1], ("set_state", RobotState.LISTENING))


if __name__ == "__main__":
    unittest.main()
