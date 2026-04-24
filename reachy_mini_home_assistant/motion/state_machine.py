"""Movement state machine and related motion data structures.

This module now also contains idle-behavior data helpers so the control-loop
implementation can stay focused on runtime orchestration.
"""

import logging
import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..animations.animation_config import load_animation_config

logger = logging.getLogger(__name__)

OFFICIAL_NEUTRAL_ANTENNA_SDK_LEFT_RAD = -0.1745
OFFICIAL_NEUTRAL_ANTENNA_SDK_RIGHT_RAD = 0.1745
OFFICIAL_NEUTRAL_ANTENNA_LOCAL_LEFT_RAD = 0.1745
OFFICIAL_NEUTRAL_ANTENNA_LOCAL_RIGHT_RAD = -0.1745


class RobotState(Enum):
    """Robot state machine states."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


# State to animation mapping
# SPEAKING uses a dedicated antenna-forward animation while speech_sway
# continues to drive the head motion on top.
STATE_ANIMATION_MAP = {
    "idle": "idle",
    "listening": "listening",
    "thinking": "thinking",
    "speaking": "speaking",
}


@dataclass
class MovementState:
    """Internal movement state (only modified by control loop)."""

    # Current robot state
    robot_state: RobotState = RobotState.IDLE

    # Animation offsets (from AnimationPlayer)
    anim_pitch: float = 0.0
    anim_yaw: float = 0.0
    anim_roll: float = 0.0
    anim_x: float = 0.0
    anim_y: float = 0.0
    anim_z: float = 0.0
    anim_antenna_left: float = 0.0
    anim_antenna_right: float = 0.0

    # Speech sway offsets (from audio analysis)
    sway_pitch: float = 0.0
    sway_yaw: float = 0.0
    sway_roll: float = 0.0
    sway_x: float = 0.0
    sway_y: float = 0.0
    sway_z: float = 0.0

    # Target pose (from actions)
    target_pitch: float = 0.0
    target_yaw: float = 0.0
    target_roll: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    target_z: float = 0.0
    target_antenna_left: float = 0.0
    target_antenna_right: float = 0.0

    # Timing
    last_activity_time: float = 0.0
    idle_start_time: float = 0.0

    # Note: Antenna freeze state is now managed by AntennaController (motion/antenna.py)

    # Idle look-around behavior
    next_look_around_time: float = 0.0
    look_around_in_progress: bool = False

    animation_blend: float = 1.0


@dataclass
class PendingAction:
    """A pending motion action."""

    name: str
    target_pitch: float = 0.0
    target_yaw: float = 0.0
    target_roll: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    target_z: float = 0.0
    target_antenna_left: float = 0.0
    target_antenna_right: float = 0.0
    duration: float = 0.5
    callback: Callable | None = None


@dataclass
class IdleRestPose:
    """Low-energy rest pose used when idle behavior is disabled."""

    pitch_rad: float
    antenna_left_rad: float
    antenna_right_rad: float


@dataclass
class IdleBehaviorConfig:
    """Parsed idle behavior configuration from the unified JSON file."""

    rest_pose: IdleRestPose
    min_interval_s: float
    max_interval_s: float
    trigger_probability: float
    generation: "IdleGenerationConfig"


@dataclass
class IdleGenerationConfig:
    """Realtime generated idle motion ranges."""

    yaw_range_deg: tuple[float, float]
    pitch_range_deg: tuple[float, float]
    roll_range_deg: tuple[float, float]
    x_range_m: tuple[float, float]
    y_range_m: tuple[float, float]
    z_range_m: tuple[float, float]
    duration_range_s: tuple[float, float]
    opposite_direction_bias: float
    micro_motion_probability: float


def parse_numeric_range(value: Any, default_min: float, default_max: float) -> tuple[float, float]:
    """Parse a numeric range from config value."""
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        try:
            min_v = float(value[0])
            max_v = float(value[1])
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            return min_v, max_v
        except (TypeError, ValueError):
            return default_min, default_max

    if value is None:
        return default_min, default_max

    try:
        span = abs(float(value))
        return -span, span
    except (TypeError, ValueError):
        return default_min, default_max


def parse_probability(value: Any, default: float) -> float:
    """Parse a probability-like value in the 0..1 range."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def load_idle_behavior_config(
    *,
    config_path: Path,
    default_rest_pose: dict[str, float],
    default_min_interval_s: float,
    default_max_interval_s: float,
    default_probability: float,
    default_yaw_range_deg: float,
    default_pitch_range_deg: float,
    default_duration_s: float,
) -> IdleBehaviorConfig:
    """Load idle behavior configuration from the unified animation file."""
    rest_pose = IdleRestPose(
        pitch_rad=math.radians(float(default_rest_pose["pitch_deg"])),
        antenna_left_rad=float(default_rest_pose["antenna_left_rad"]),
        antenna_right_rad=float(default_rest_pose["antenna_right_rad"]),
    )
    min_interval_s = default_min_interval_s
    max_interval_s = default_max_interval_s
    trigger_probability = default_probability
    generation = IdleGenerationConfig(
        yaw_range_deg=(-default_yaw_range_deg, default_yaw_range_deg),
        pitch_range_deg=(-default_pitch_range_deg, default_pitch_range_deg),
        roll_range_deg=(-6.0, 6.0),
        x_range_m=(-0.002, 0.002),
        y_range_m=(-0.002, 0.002),
        z_range_m=(-0.002, 0.003),
        duration_range_s=(max(0.2, default_duration_s * 0.55), max(0.2, default_duration_s * 1.25)),
        opposite_direction_bias=0.68,
        micro_motion_probability=0.18,
    )

    if not config_path.exists():
        logger.debug("Idle behavior config file not found: %s", config_path)
        return IdleBehaviorConfig(rest_pose, min_interval_s, max_interval_s, trigger_probability, generation)

    try:
        config = load_animation_config(config_path)
    except Exception as e:
        logger.warning("Failed to read idle behavior config: %s", e)
        return IdleBehaviorConfig(rest_pose, min_interval_s, max_interval_s, trigger_probability, generation)

    rest_pose_section = config.get("idle_rest_pose")
    if isinstance(rest_pose_section, dict):
        try:
            rest_pose.pitch_rad = math.radians(
                float(rest_pose_section.get("pitch_deg", default_rest_pose["pitch_deg"]))
            )
        except (TypeError, ValueError):
            pass
        try:
            rest_pose.antenna_left_rad = float(
                rest_pose_section.get("antenna_left_rad", default_rest_pose["antenna_left_rad"])
            )
        except (TypeError, ValueError):
            pass
        try:
            rest_pose.antenna_right_rad = float(
                rest_pose_section.get("antenna_right_rad", default_rest_pose["antenna_right_rad"])
            )
        except (TypeError, ValueError):
            pass

    section = config.get("idle_generated_motion")
    if not isinstance(section, dict):
        return IdleBehaviorConfig(rest_pose, min_interval_s, max_interval_s, trigger_probability, generation)

    try:
        min_interval = float(section.get("min_interval_s", default_min_interval_s))
        max_interval = float(section.get("max_interval_s", default_max_interval_s))
        if min_interval > max_interval:
            min_interval, max_interval = max_interval, min_interval
        min_interval_s = max(0.5, min_interval)
        max_interval_s = max(min_interval_s, max_interval)
    except (TypeError, ValueError):
        min_interval_s = default_min_interval_s
        max_interval_s = default_max_interval_s

    try:
        probability = float(section.get("trigger_probability", default_probability))
    except (TypeError, ValueError):
        probability = default_probability
    trigger_probability = max(0.0, min(1.0, probability))

    generation = IdleGenerationConfig(
        yaw_range_deg=parse_numeric_range(section.get("yaw_range_deg"), -default_yaw_range_deg, default_yaw_range_deg),
        pitch_range_deg=parse_numeric_range(
            section.get("pitch_range_deg"), -default_pitch_range_deg, default_pitch_range_deg
        ),
        roll_range_deg=parse_numeric_range(section.get("roll_range_deg"), -6.0, 6.0),
        x_range_m=parse_numeric_range(section.get("x_range_m"), -0.002, 0.002),
        y_range_m=parse_numeric_range(section.get("y_range_m"), -0.002, 0.002),
        z_range_m=parse_numeric_range(section.get("z_range_m"), -0.002, 0.003),
        duration_range_s=parse_numeric_range(
            section.get("duration_range_s"), max(0.2, default_duration_s * 0.55), max(0.2, default_duration_s * 1.25)
        ),
        opposite_direction_bias=parse_probability(section.get("opposite_direction_bias"), 0.68),
        micro_motion_probability=parse_probability(section.get("micro_motion_probability"), 0.18),
    )

    return IdleBehaviorConfig(rest_pose, min_interval_s, max_interval_s, trigger_probability, generation)


def _sample_biased_yaw(config: IdleGenerationConfig, last_yaw_rad: float) -> float:
    yaw_min, yaw_max = config.yaw_range_deg
    if abs(last_yaw_rad) > math.radians(2.0) and random.random() < config.opposite_direction_bias:
        if last_yaw_rad > 0.0 and yaw_min < 0.0:
            yaw_max = min(yaw_max, -2.0)
        elif last_yaw_rad < 0.0 and yaw_max > 0.0:
            yaw_min = max(yaw_min, 2.0)
    return math.radians(random.uniform(float(yaw_min), float(yaw_max)))


def build_generated_idle_pending_action(config: IdleGenerationConfig, *, last_yaw_rad: float = 0.0) -> PendingAction:
    """Generate one idle action from ranges at runtime."""
    pitch_min, pitch_max = config.pitch_range_deg
    roll_min, roll_max = config.roll_range_deg
    x_min, x_max = config.x_range_m
    y_min, y_max = config.y_range_m
    z_min, z_max = config.z_range_m
    duration_min, duration_max = config.duration_range_s

    yaw = _sample_biased_yaw(config, last_yaw_rad)
    pitch = math.radians(random.uniform(float(pitch_min), float(pitch_max)))
    roll = math.radians(random.uniform(float(roll_min), float(roll_max)))
    x = random.uniform(float(x_min), float(x_max))
    y = random.uniform(float(y_min), float(y_max))
    z = random.uniform(float(z_min), float(z_max))

    if random.random() < config.micro_motion_probability:
        yaw *= 0.35
        pitch *= 0.45
        roll *= 0.45
        x *= 0.4
        y *= 0.4
        z *= 0.4

    if abs(yaw) < math.radians(1.5) and abs(pitch) < math.radians(1.0) and abs(roll) < math.radians(1.0):
        yaw = math.copysign(math.radians(random.uniform(2.5, 6.0)), yaw or random.choice((-1.0, 1.0)))

    return PendingAction(
        name="idle_generated",
        target_yaw=yaw,
        target_pitch=pitch,
        target_roll=roll,
        target_x=x,
        target_y=y,
        target_z=z,
        duration=max(0.2, random.uniform(float(duration_min), float(duration_max))),
    )
