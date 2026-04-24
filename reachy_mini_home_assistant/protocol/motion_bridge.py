"""Motion bridge helpers for `VoiceSatelliteProtocol`."""

from __future__ import annotations

import logging
import math
import statistics
import time
from typing import TYPE_CHECKING

from ..entities.event_emotion_mapper import (
    SKILL_PLAY_EMOTION,
    SKILL_TIMER_ALERT,
    VOICE_PHASE_IDLE,
    VOICE_PHASE_LISTENING,
    VOICE_PHASE_SPEAKING,
    VOICE_PHASE_THINKING,
)

if TYPE_CHECKING:
    from .satellite import VoiceSatelliteProtocol

_LOGGER = logging.getLogger(__name__)


def _read_stable_wakeup_yaw(protocol: VoiceSatelliteProtocol) -> tuple[float, int, int] | None:
    """Read a short DOA window and return a stable yaw estimate in degrees."""
    speech_yaws: list[float] = []
    fallback_yaws: list[float] = []
    sample_count = 5
    for index in range(sample_count):
        doa = protocol.reachy_controller.get_doa_angle()
        if doa is not None:
            angle_rad, speech_detected = doa
            yaw_deg = math.degrees(-(angle_rad - math.pi / 2))
            fallback_yaws.append(yaw_deg)
            if speech_detected:
                speech_yaws.append(yaw_deg)
            _LOGGER.debug(
                "DOA wake sample %d/%d: angle=%.1f°, yaw=%.1f°, speech=%s",
                index + 1,
                sample_count,
                math.degrees(angle_rad),
                yaw_deg,
                speech_detected,
            )
        if index < sample_count - 1:
            time.sleep(0.035)

    yaws = speech_yaws if speech_yaws else fallback_yaws
    if not yaws:
        return None
    return statistics.median(yaws), len(speech_yaws), len(fallback_yaws)


def turn_to_sound_source(protocol: VoiceSatelliteProtocol) -> None:
    if not protocol.state.motion_enabled:
        _LOGGER.info("DOA turn-to-sound: motion disabled")
        return
    try:
        stable = _read_stable_wakeup_yaw(protocol)
        if stable is None:
            _LOGGER.info("DOA not available, skipping turn-to-sound")
            return
        yaw_deg, speech_samples, total_samples = stable
        _LOGGER.debug("DOA stable wake yaw=%.1f° from %d speech samples/%d total", yaw_deg, speech_samples, total_samples)
        if abs(yaw_deg) < 10.0:
            _LOGGER.debug("DOA angle %.1f° below threshold (%.1f°), skipping turn", yaw_deg, 10.0)
            return
        target_yaw_deg = yaw_deg * 0.85
        _LOGGER.info(
            "Turning toward sound source: DOA yaw=%.1f°, target=%.1f°",
            yaw_deg,
            target_yaw_deg,
        )
        if protocol.state.motion and protocol.state.motion.movement_manager:
            protocol.state.motion.movement_manager.turn_to_angle(target_yaw_deg, duration=0.65)
    except Exception as e:
        _LOGGER.error("Error in turn-to-sound: %s", e)


def reachy_on_listening(protocol: VoiceSatelliteProtocol) -> None:
    protocol._behavior_controller.handle_voice_phase(VOICE_PHASE_LISTENING)


def reachy_on_thinking(protocol: VoiceSatelliteProtocol) -> None:
    protocol._behavior_controller.handle_voice_phase(VOICE_PHASE_THINKING)


def reachy_on_speaking(protocol: VoiceSatelliteProtocol) -> None:
    protocol._behavior_controller.handle_voice_phase(VOICE_PHASE_SPEAKING)


def reachy_on_idle(protocol: VoiceSatelliteProtocol) -> None:
    protocol._behavior_controller.handle_voice_phase(VOICE_PHASE_IDLE)


def reachy_on_timer_finished(protocol: VoiceSatelliteProtocol) -> None:
    protocol._behavior_controller.execute_skill(SKILL_TIMER_ALERT, context="timer_finished")


def play_emotion(protocol: VoiceSatelliteProtocol, emotion_name: str) -> None:
    protocol._behavior_controller.execute_skill(SKILL_PLAY_EMOTION, emotion_name=emotion_name, context="emotion")


def queue_emotion_move(protocol: VoiceSatelliteProtocol, emotion_name: str) -> None:
    try:
        if protocol.state.motion and protocol.state.motion.movement_manager:
            movement_manager = protocol.state.motion.movement_manager
            if movement_manager.queue_emotion_move(emotion_name):
                _LOGGER.info("Queued emotion move: %s", emotion_name)
            else:
                _LOGGER.warning("Failed to queue emotion: %s", emotion_name)
        else:
            _LOGGER.warning("Cannot play emotion: no movement manager available")
    except Exception as e:
        _LOGGER.error("Error playing emotion %s: %s", emotion_name, e)


def enter_motion_state(protocol: VoiceSatelliteProtocol, context: str, callback_name: str) -> None:
    protocol._cancel_delayed_idle_return()
    run_motion_state(protocol, context, callback_name)


def run_motion_state(protocol: VoiceSatelliteProtocol, context: str, callback_name: str) -> None:
    if not protocol.state.motion_enabled:
        if context == "speaking":
            _LOGGER.warning("Motion disabled, skipping speaking animation")
        return
    if context in {"thinking", "idle"} and not protocol.state.reachy_mini:
        return
    motion = protocol.state.motion
    if motion is None:
        if context == "speaking":
            _LOGGER.warning("No motion controller, skipping speaking animation")
        return
    try:
        _LOGGER.debug("Reachy Mini: %s animation", context.capitalize())
        getattr(motion, callback_name)()
    except Exception as e:
        _LOGGER.error("Reachy Mini motion error: %s", e)
