# Reachy Mini for Home Assistant Custom - Project Summary

This custom app turns Reachy Mini Wi-Fi into a Home Assistant voice satellite with expressive robot motion and Home Assistant entities.

## Current Runtime Scope

- Home Assistant discovery through ESPHome protocol and mDNS
- Local wake word detection with MicroWakeWord/OpenWakeWord
- Home Assistant voice pipeline for STT, conversation, and TTS
- Built-in Reachy Mini listening, thinking, speaking, timer, idle, and emotion motions
- DOA sound-source orientation at wake
- Smooth manual head yaw control with body yaw following and hold behavior
- Pose controls, DOA, IMU sensors, robot status, and runtime controls exposed as Home Assistant entities

## Home Assistant Entities

Main entity groups:

- Runtime controls: mute, speaker volume, idle behavior
- Pose controls: head position/orientation, body yaw, antennas
- DOA sensors and DOA tracking switch
- Emotion selector and continuous conversation switch
- Robot diagnostics and IMU sensors
- Service state

## Motion Behavior

Motion is centralized through `MovementManager`. The current behavior preserves:

- Manual Head Yaw hold for non-zero manual turns
- Body yaw following manual and DOA turn actions
- Smooth return-to-neutral after conversation unless manual yaw hold is active
- Idle rest posture when idle behavior is disabled
- Official breathing parameters, audio-driven speaking sway, generated idle micro-motions, and emotion motions

## Removed Runtime Scope

The robot-side camera and vision pipeline is removed from the Home Assistant mini app.

## Version Notes

- v1.0.8: stable pre-cleanup custom build with manual yaw hold, DOA/body-follow refinements, antenna smoothing, and conversation recentering
- v1.0.9: removes robot-side vision AI and related Home Assistant entities
- v1.0.10: refreshes public docs and cleanup notes to match the current runtime
- v1.0.11: removes robot-side camera streaming, snapshot serving, camera entities, camera lifecycle wiring, and OpenCV dependency
