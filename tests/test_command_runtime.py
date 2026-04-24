import re
import types
import unittest
from pathlib import Path

from reachy_mini_home_assistant.protocol import voice_pipeline


class CommandRuntimeSourceTests(unittest.TestCase):
    def test_non_idle_state_no_longer_resets_pose_anchor(self):
        path = Path("reachy_mini_home_assistant/motion/command_runtime.py")
        content = path.read_text(encoding="utf-8")

        match = re.search(r"if payload != RobotState\.IDLE:(?P<body>[\s\S]*?)logger\.debug", content)
        self.assertIsNotNone(match)
        body = match.group("body")

        self.assertNotIn("manager.state.target_yaw = 0.0", body)
        self.assertIn("_cancel_idle_motion_for_wakeup(manager)", body)
        self.assertIn("Preserve the current pose anchor", body)
        self.assertIn('name="wake_from_idle_rest"', body)
        self.assertIn("target_pitch=0.0", body)
        self.assertIn("target_roll=0.0", body)
        self.assertIn("target_yaw=manager.state.target_yaw", body)
        self.assertIn("target_antenna_left=0.0", body)
        self.assertIn("target_antenna_right=0.0", body)
        self.assertIn("duration=0.7", body)
        self.assertIn("old_state == RobotState.IDLE and not manager._idle_behavior_enabled()", body)
        self.assertIn('manager._pending_action.name != "idle_rest"', body)
        self.assertIn('manager._pending_action.name == "idle_rest"', body)
        self.assertIn("manager._pending_action = None", body)
        self.assertIn("start_action(manager, action)", body)
        self.assertIn("manager._antenna_controller.reset()", body)

    def test_wakeup_cancels_idle_only_motion_immediately(self):
        path = Path("reachy_mini_home_assistant/motion/command_runtime.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn("def _cancel_idle_motion_for_wakeup", content)
        self.assertIn('pending.name.startswith(("idle_action", "idle_generated"))', content)
        self.assertIn("manager._pending_action = None", content)
        self.assertIn("manager._idle_action_queue.clear()", content)
        self.assertIn("manager.state.look_around_in_progress = False", content)
        self.assertIn("manager.state.next_look_around_time = 0.0", content)
        self.assertIn("manager._idle_action_animation_suppression = 0.0", content)


class MotionTimingSourceTests(unittest.TestCase):
    def test_idle_turn_actions_keep_body_follow_enabled(self):
        path = Path("reachy_mini_home_assistant/motion/control_runtime.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn('manager._pending_action.name in {"turn_to", "doa_turn"}', content)
        self.assertIn("and not active_turn_action", content)
        self.assertIn("or active_turn_action", content)

    def test_turn_actions_keep_fast_pose_with_separate_antenna_smoothing(self):
        path = Path("reachy_mini_home_assistant/motion/movement_manager.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn('ANTENNA_WAKE_ACTIONS = frozenset({"turn_to", "doa_turn", "wake_from_idle_rest"})', content)
        self.assertIn("ANTENNA_WAKE_MIN_DURATION_S = 1.0", content)
        self.assertIn("antenna_delta > ANTENNA_LARGE_MOVE_THRESHOLD_RAD", content)
        self.assertIn("pose_progress = min(1.0, elapsed / pose_duration)", content)
        self.assertIn("antenna_progress = min(1.0, elapsed / antenna_duration)", content)
        self.assertIn("t = _smootherstep(pose_progress)", content)
        self.assertIn("antenna_t = _smootherstep(antenna_progress)", content)
        self.assertIn('completed_action.name.startswith(("idle_action", "idle_generated"))', content)
        self.assertIn('self._pending_action.name.startswith(("idle_action", "idle_generated"))', content)
        self.assertIn("def reset_yaw_to_neutral", content)
        self.assertIn('name="neutral_yaw"', content)

    def test_idle_generated_keeps_antennas_alive_and_smooths_breathing_z(self):
        path = Path("reachy_mini_home_assistant/motion/movement_manager.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn("IDLE_ACTION_ANTENNA_SUPPRESSION = 0.0", content)
        self.assertIn("IDLE_BREATHING_Z_SMOOTHING_TAU_S", content)
        self.assertIn("self._idle_breathing_z_smoothed", content)

    def test_disabled_idle_rest_return_is_gentler(self):
        path = Path("reachy_mini_home_assistant/motion/reachy_motion.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn("transition_to_idle_rest(duration=2.6)", content)

    def test_conversation_finished_recenters_yaw_before_delayed_idle(self):
        session_flow = Path("reachy_mini_home_assistant/protocol/session_flow.py").read_text(encoding="utf-8")
        reachy_motion = Path("reachy_mini_home_assistant/motion/reachy_motion.py").read_text(encoding="utf-8")

        self.assertIn('protocol._run_motion_state("conversation_finished", "on_conversation_finished")', session_flow)
        self.assertIn("def on_conversation_finished", reachy_motion)
        self.assertIn("reset_yaw_to_neutral(duration=1.2)", reachy_motion)
        self.assertIn("if not self._movement_manager._manual_head_yaw_hold", reachy_motion)


class VoicePipelineStopTests(unittest.TestCase):
    def _make_protocol(self):
        stop_word = types.SimpleNamespace(id="stop")
        tts_player = types.SimpleNamespace(stop=lambda: None)
        state = types.SimpleNamespace(stop_word=stop_word, active_wake_words={"stop"}, tts_player=tts_player)

        protocol = types.SimpleNamespace(
            _pipeline_active=True,
            _is_streaming_audio=True,
            _continue_conversation=True,
            _pending_voice_request=("wake", "conv"),
            _timer_finished=False,
            _timer_ring_start=123.0,
            _tts_url="http://example.test/tts",
            _tts_played=False,
            state=state,
        )
        protocol._set_stop_word_active_calls = []
        protocol._tts_finished_calls = 0

        def set_stop_word_active(active):
            protocol._set_stop_word_active_calls.append(active)

        def tts_finished():
            protocol._tts_finished_calls += 1

        protocol._set_stop_word_active = set_stop_word_active
        protocol._tts_finished = tts_finished
        protocol.unduck = lambda: None
        return protocol

    def test_stop_tts_finishes_session_immediately(self):
        protocol = self._make_protocol()
        stop_calls = []
        protocol.state.tts_player.stop = lambda: stop_calls.append(True)

        voice_pipeline.stop(protocol)

        self.assertFalse(protocol._pipeline_active)
        self.assertFalse(protocol._is_streaming_audio)
        self.assertFalse(protocol._continue_conversation)
        self.assertIsNone(protocol._pending_voice_request)
        self.assertIsNone(protocol._tts_url)
        self.assertTrue(protocol._tts_played)
        self.assertNotIn(protocol.state.stop_word.id, protocol.state.active_wake_words)
        self.assertEqual(protocol._set_stop_word_active_calls, [False])
        self.assertEqual(len(stop_calls), 1)
        self.assertEqual(protocol._tts_finished_calls, 1)

    def test_stop_timer_sound_does_not_finish_tts_session(self):
        protocol = self._make_protocol()
        protocol._timer_finished = True
        protocol.state.active_wake_words.add(protocol.state.stop_word.id)
        stop_calls = []
        unduck_calls = []

        protocol.state.tts_player.stop = lambda: stop_calls.append(True)
        protocol.unduck = lambda: unduck_calls.append(True)

        voice_pipeline.stop(protocol)

        self.assertFalse(protocol._timer_finished)
        self.assertIsNone(protocol._timer_ring_start)
        self.assertEqual(len(unduck_calls), 1)
        self.assertEqual(len(stop_calls), 1)
        self.assertEqual(protocol._tts_finished_calls, 0)


class CommandRuntimeStateQueueTests(unittest.TestCase):
    def test_poll_commands_coalesces_back_to_back_state_updates(self):
        path = Path("reachy_mini_home_assistant/motion/command_runtime.py")
        content = path.read_text(encoding="utf-8")

        self.assertIn('if cmd == "set_state":', content)
        self.assertIn('if next_cmd == "set_state":', content)
        self.assertIn("payload = next_payload", content)
