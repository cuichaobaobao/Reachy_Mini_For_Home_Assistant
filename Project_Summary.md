# Reachy Mini for Home Assistant Custom - Project Summary

This custom app turns Reachy Mini Wi-Fi into a Home Assistant voice satellite with expressive robot motion and a lightweight MJPEG camera stream.

## Current Runtime Scope

- Home Assistant discovery through ESPHome protocol and mDNS
- Local wake word detection with MicroWakeWord/OpenWakeWord
- Home Assistant voice pipeline for STT, conversation, and TTS
- Built-in Reachy Mini listening, thinking, speaking, timer, idle, and emotion motions
- DOA sound-source orientation at wake
- Smooth manual head yaw control with body yaw following and hold behavior
- MJPEG camera stream and snapshot endpoints for Home Assistant or external video systems
- Optional Sendspin multi-room audio playback
- System diagnostics, pose controls, IMU sensors, and camera controls exposed as Home Assistant entities

## Camera Stream

The app keeps the robot-side camera path intentionally simple. It captures frames from the Reachy Mini SDK and serves:

```text
http://<robot-ip>:8081/stream
http://<robot-ip>:8081/snapshot
```

Active stream clients receive the configured high-rate MJPEG stream. When no stream client is connected, the app keeps a low-rate snapshot refresh to reduce idle load.

External systems such as Frigate or go2rtc can pull the MJPEG stream. For long-running analysis, an external restream/transcode layer is recommended so heavy video work runs away from the robot.

## Home Assistant Entities

Main entity groups:

- Runtime controls: mute, speaker volume, camera enable/disable, idle behavior, Sendspin
- Pose controls: head position/orientation, body yaw, antennas, look-at target
- DOA sensors and DOA tracking switch
- Camera entity
- Emotion selector and continuous conversation switch
- Robot diagnostics and IMU sensors
- Service state and system diagnostics

## Motion Behavior

Motion is centralized through `MovementManager`. The current behavior preserves:

- Manual Head Yaw hold for non-zero manual turns
- Body yaw following manual and DOA turn actions
- Smooth return-to-neutral after conversation unless manual yaw hold is active
- Idle rest posture when idle behavior is disabled
- Breathing, antenna, speaking sway, and emotion motions

## Removed Runtime Scope

The robot-side camera AI pipeline was removed in v1.0.9 to keep this custom app focused and lighter on robot resources. Video remains available as a plain stream for external systems.

## Version Notes

- v1.0.8: stable pre-cleanup custom build with manual yaw hold, DOA/body-follow refinements, antenna smoothing, and conversation recentering
- v1.0.9: removes robot-side vision AI and related Home Assistant entities while preserving video streaming
- v1.0.10: refreshes public docs and cleanup notes to match the current runtime
