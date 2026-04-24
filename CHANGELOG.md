# Changelog

All notable changes to the Reachy Mini HA Voice project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No unreleased changes._

## [1.0.30] - 2026-04-24

### Changed
- Restore the idle breathing layer to the official Reachy Mini conversation parameters and sine-wave head Z formula.
- Restore the conservative TTS completion flow: recenter first, then resume idle breathing shortly after the return.
- Revert wakeup DOA turning to the previous immediate single-read behavior after the short median window showed no practical improvement.
- Restore thinking animation amplitudes to the previous conservative values to reduce visible state-transition jumps.

### Fixed
- Keep body yaw fixed during TTS speaking so audio-driven speech motion does not sway the body.

## [1.0.29] - 2026-04-24

### Changed
- Make realtime idle sequences less repetitive with a constrained random action grammar, 5-8 generated steps, and broader left/right/up/down/stretch/tuck/tilt/pause combinations.
- Retune idle breathing for visible motion with a mechanical-friendly up/hold/down/hold curve, slightly larger Z travel, slower frequency, and a small pitch component.
- Increase the thinking animation head amplitudes so the processing state reads more clearly.
- Restore idle breathing immediately while TTS completion recentering runs, instead of waiting for the delayed idle return.
- Smooth manual idle enable/disable transitions so head and antenna targets ease into neutral/rest poses.
- Stabilize wakeup DOA turning by sampling a short DOA window and using the median yaw before turning.

## [1.0.28] - 2026-04-24

### Fixed
- Stop the richer idle generator from occasionally omitting a visible up/down head movement by making side-look, up-look, neck-stretch, down-look, and neck-tuck mandatory sequence primitives.
- Further damp idle breathing on the downward Z path with a slower filter and larger deadband to reduce visible head jitter while descending.

### Changed
- Lengthen realtime idle sequences to 5-7 generated steps over about 7.0-10.5 seconds before hold and return so the motion reads as one smooth action sequence instead of a quick flick.

## [1.0.27] - 2026-04-24

### Changed
- Make realtime idle sequences richer by composing 4-6 generated steps from side-look, up-look, down-look, neck-stretch, neck-tuck, opposite-glance, and settle primitives.
- Lengthen generated idle sequence motion to about 5.8-8.6 seconds before hold and return.
- Expand generated neck travel so idle can visibly stretch upward and tuck downward while preserving official neutral antenna targets.
- Add asymmetric idle breathing Z smoothing with a small deadband so downward breathing updates are gentler.

## [1.0.26] - 2026-04-24

### Changed
- Interrupt generated idle sequences immediately when the robot leaves IDLE so wakeup/DOA/listening can take over without waiting for idle motion.
- Keep official antenna breathing at full strength during generated idle sequences instead of fading most of it out.
- Use the softer smootherstep interpolation for generated idle sequence segments.
- Add light smoothing to the idle breathing Z offset to reduce visible head micro-jitter from tiny motor updates.

## [1.0.25] - 2026-04-24

### Changed
- Upgrade realtime idle motion from single generated targets to generated multi-step sequences.
- Each idle trigger now performs a smooth look/lift/dip sequence, briefly holds, then returns to breathing neutral.
- Retune generated idle timing so visible sequence motion lasts several seconds and the next sequence waits a random 3-15 seconds.
- Keep generated idle antennas on the official neutral target while the pose sequence stays fully runtime-generated.

## [1.0.24] - 2026-04-24

### Changed
- Restore the historical disabled-idle sleep posture with the 16 degree head pitch and SDK sleep antenna pose.
- Restore the older `wake_from_idle_rest` target so static-idle wakeups lift back to head-neutral with 0/0 antenna targets while preserving yaw.
- Keep realtime generated idle motion truly parameter-generated for the head/body pose while using the official neutral antenna targets.
- Match TTS speaking antenna wiggle to the official 15 degree, 0.5Hz antenna timing while leaving audio-driven head sway in control.

## [1.0.23] - 2026-04-24

### Changed
- Turn realtime idle motion into a full breathing transition cycle: fade out breathing, perform the generated action, hold briefly, return to breathing neutral, then fade breathing back in.
- Retune generated idle ranges for a lighter ha-china-style feel while keeping runtime parameter generation and previous-motion distance checks.

### Fixed
- Use a more responsive idle-generated interpolation curve so generated idle actions feel less delayed without snapping.

## [1.0.22] - 2026-04-24

### Changed
- Restore ha-china-style continuous idle animation layering so official breathing keeps running smoothly through realtime generated idle motion.
- Increase the voice audio block size to reduce idle audio-loop CPU pressure while keeping wake latency reasonable.

### Fixed
- Remove the quiet-idle breathing short-circuit that made generated idle actions snap between control paths.
- Start realtime idle actions from the primary target pose again so breathing remains an additive layer instead of being baked into the next action target.

## [1.0.21] - 2026-04-24

### Changed
- Make realtime generated idle motions slower, more visible, and less repetitive by sampling broader pose ranges and remembering the previous generated signature.
- Restore light speaking antenna sway while keeping TTS head motion driven by `SpeechSwayRT`.

### Fixed
- Start generated idle handoffs from the last commanded breathing pose and antenna positions instead of stale target state.
- Keep generated idle antenna targets around the official +/-10 degree neutral instead of pulling them toward zero.

## [1.0.20] - 2026-04-24

### Changed
- Drive quiet idle breathing through an official `BreathingMove`-equivalent path instead of JSON offset layering.
- Match the official idle breathing interpolation, head Z sine, antenna sway formula, antenna order, and body yaw output for the breathing state.

## [1.0.19] - 2026-04-24

### Changed
- Keep idle breathing aligned with the official Reachy Mini conversation app parameters without adding an extra output smoothing layer.

### Fixed
- Remove idle antenna output smoothing so the antenna breathing sway follows the official 15 degree, 0.5Hz timing directly.

## [1.0.18] - 2026-04-24

### Fixed
- Fix generated idle motion completion tracking so realtime idle actions can keep triggering instead of getting stuck after a generated action.
- Smooth idle antenna output before sending targets to the robot to reduce visible step jitter while keeping the official breathing parameters.
- Report `Backend Ready` as practical daemon operational readiness because the daemon's internal `backend_status.ready` flag can stay false on wireless robots even while the app, motors, and control loop are healthy.

## [1.0.17] - 2026-04-24

### Changed
- Replace preset idle action templates with realtime generated idle micro-motions so each idle action samples fresh yaw, pitch, roll, position, and duration parameters.
- Align idle breathing exactly with the official Reachy Mini conversation app parameters: 0.005m Z amplitude, 0.1Hz breathing, 15 degree antenna sway, and 0.5Hz antenna sway.
- Make the speaking animation a state marker only so visible TTS motion comes from the official-style audio-driven `SpeechSwayRT` path.
- Debounce Home Assistant disconnect handling so brief ESPHome connection drops do not immediately suspend wake/STT/TTS services.
- Report `Backend Ready` from the real daemon `backend_status.ready` flag instead of treating daemon `running` as backend readiness.

### Removed
- Remove Sendspin discovery/playback, the Sendspin Home Assistant switch, the `aiosendspin` dependency, and related playback buffering.
- Remove the unused blueprint, local health/memory monitors, system diagnostics entities, and disabled look-at controls.

## [1.0.16] - 2026-04-24

### Changed
- Align all idle, neutral, wake-from-rest, and motion-fallback antenna neutral paths to the official Reachy Mini conversation app's ~+/-10 degree baseline so antennas return to a consistent calmer center instead of mixing 0 degree and offset neutral states.
- Raise the package Python baseline to 3.12 so project metadata matches the runtime requirement already imposed by `aiosendspin`.

## [1.0.15] - 2026-04-23

### Changed
- Align the motion control loop with the official Reachy Mini conversation app at 60Hz to reduce long-running motor command pressure and improve antenna/head smoothness.

## [1.0.14] - 2026-04-21

### Changed
- Limit bundled selectable wake words to the Linux Voice Assistant MicroWakeWord set: Okay Nabu, Hey Mycroft, and Hey Jarvis.
- Replace Hey Jarvis with the Linux Voice Assistant MicroWakeWord model and keep Okay Nabu, Hey Mycroft, and Stop aligned with the same source set.

### Removed
- Remove OpenWakeWord runtime support, the pyopen-wakeword dependency, and bundled openWakeWord model assets.
- Remove unused bundled wake words and external wake-word download support so Home Assistant only exposes the three curated wake words.

## [1.0.13] - 2026-04-21

### Fixed
- Restore the pre-1.0.12 microphone/TTS media access behavior after the serialized microphone-read change caused worse TTS stutter on the robot.

## [1.0.12] - 2026-04-21

### Fixed
- Serialize microphone reads with TTS audio pushes on the SDK media pipeline to reduce TTS stutter when an external RTSP/WebRTC video bridge is active.

## [1.0.11] - 2026-04-21

### Removed
- Remove robot-side MJPEG camera streaming, snapshot serving, and Home Assistant camera entities from the mini app.
- Remove camera runtime modules, camera command-line/configuration options, camera lifecycle wiring, and OpenCV runtime dependency.

## [1.0.10] - 2026-04-19

### Changed
- Refresh the Hugging Face landing page and user manuals to match the current voice and motion focused app.
- Replace the old project summary with a concise current architecture note for the custom app.

### Removed
- Remove stale public-facing references to removed robot-side vision AI features from current docs and landing content.
- Remove obsolete face/gesture comments and unused preference-number helpers left after the 1.0.9 cleanup.

## [1.0.9] - 2026-04-19

### Removed
- Remove robot-side face tracking and gesture detection, including their Home Assistant switches/sensors and bundled vision AI model files.
- Remove YOLO/ONNX/PyTorch vision AI runtime dependencies while keeping OpenCV for MJPEG encoding.

### Changed
- Keep the camera server as a pure MJPEG video stream for Home Assistant and external vision services.
- Preserve 15fps active streaming and reduce JPEG quality from 80 to 75 for lower bandwidth/encoding pressure without sacrificing smoothness.
- Refresh frames at 1fps when no stream client is connected, keeping snapshots available with lower idle load.

### Fixed
- Prevent voice-state transitions from re-enabling face tracking after the user intends vision AI to stay disabled.

## [1.0.8] - 2026-04-15

### Changed
- Increase large wake/turn antenna smoothing from 0.75s to 1.0s while keeping DOA yaw/body turn timing at 0.5s.
- Recenter yaw after a completed non-continuous conversation before the delayed idle-rest timer fires, so a second wake word starts from a clean forward orientation.

### Fixed
- Preserve manual head-yaw hold by skipping the post-conversation yaw recenter when the user has manually anchored the head direction.
- Keep the delayed idle/rest behavior intact; the robot recenters yaw after TTS but still waits before entering neutral idle or disabled-idle rest.

## [1.0.7] - 2026-04-15

### Changed
- Keep DOA turn-to-sound yaw timing fast at 0.5s while allowing large antenna moves to use a separate minimum 0.75s smoothing window.
- Make disabled-idle return-to-rest motion gentler by extending the idle rest transition from 2.0s to 2.6s.

### Fixed
- Allow body yaw to follow `turn_to` and `doa_turn` actions even while the robot is still technically in IDLE, preventing the head-only turn that could happen just before LISTENING state arrives.
- Smooth only large antenna jumps for wake/turn actions, so idle-rest antennas no longer snap up while head and body still turn quickly toward the sound source.

## [1.0.6] - 2026-04-15

### Changed
- Tune idle breathing to a smoother cadence by lowering the idle base and Z-axis frequency from 0.24Hz to 0.18Hz while keeping the official-style 0.5Hz antenna sway and 0.262rad antenna amplitude.
- Keep the listening animation unchanged to preserve the current attentive response during STT.
- Increase the thinking animation cadence from 0.26Hz to 0.34Hz so processing feels less sluggish without returning to a fast mechanical rhythm.
- Increase the speaking animation cadence from 0.32Hz to 0.42Hz so TTS motion feels more expressive while keeping the existing movement amplitudes.

### Fixed
- Smooth the wake transition from disabled-idle rest pose over 0.7s instead of snapping pitch and antennas directly to neutral.
- Preserve the current yaw anchor and manual head-yaw hold behavior during wake-from-rest smoothing, so manual turn-and-hold and body-follow behavior stay intact.
- Avoid overwriting an already queued DOA/manual motion action when leaving disabled-idle rest, allowing that action to provide its own smooth interpolation.

## [1.0.5] - 2026-04-12

### Changed
- Remove app-managed robot sleep/wake handling because current Reachy Mini SDK no longer supports mini apps remaining active while the robot enters sleep
- Keep resource suspend/resume limited to ESPHome-driven runtime toggles such as Home Assistant disconnect, mute, camera disable, and service recovery
- Align `pyproject.toml` runtime constraints with the current Reachy Mini reference SDK package (`reachy-mini>=1.6.3`, `websockets>=12,<16`, Python baseline `>=3.10`, and uv gstreamer metadata)

### Removed
- Remove `SleepManager` integration and app-side sleep/wake callback flow from the voice assistant runtime
- Remove Home Assistant sleep control entities and internal robot sleep state tracking from the mini app

## [1.0.4] - 2026-03-19

### Fixed
- Align Reachy Mini integration with current SDK assumptions by removing legacy compatibility paths and private client health checks
- Replace direct SDK private `_respeaker` access with `audio_control_utils`-based ReSpeaker initialization
- Tighten camera and pose composition to require current SDK media/utils APIs and valid `look_at_image` inputs

### Improved
- Unify idle behavior into a single persisted Home Assistant entity and remove old idle compatibility aliases
- Replace separate wake/sleep buttons with a single sleep control entity
- Update Sendspin integration for current `aiosendspin` lifecycle, stream handling, listener cleanup, and synchronized buffering
- Standardize daemon URL usage on shared config across controller, sleep manager, and daemon monitor

## [1.0.3] - 2026-03-07

### Added
- Idle Random Actions switch in Home Assistant with preferences persistence and startup restore
- Configurable `idle_random_actions` presets in `conversation_animations.json` for centralized idle motion tuning

### Fixed
- Remove duplicate `idle_random_actions` fields/methods and complete runtime control wiring in controller/entity registry/movement manager

### Optimized
- Increase idle breathing and antenna sway cadence to 0.24Hz with wiggle antenna profile for more natural standby motion
- Remove `set_target` global rate limiting and unchanged-pose skip gating to continuously stream motion commands each control tick
- Remove idle antenna slew-rate limiter so antenna motion follows animation waveforms directly for reference-like smoothness

## [1.0.2] - 2026-03-06

### Fixed
- Restore idle antenna sway animation and tune idle breathing parameters to reduce perceived stiffness
- Reintroduce idle anti-chatter smoothing/deadband for antenna and body updates to reduce mechanical jitter/noise
- Switch sleep/wake control to daemon API (`start` with `wake_up=true`, `stop` with `goto_sleep=true`) so `/api/daemon/status` reflects real sleep state on SDK 1.5
- Normalize daemon status parsing for SDK 1.5 object-based status responses
- Remove all app-side antenna power on/off operations to avoid SDK instability and external-control conflicts
- Sync Idle Motion toggle with Idle Antenna Motion toggle for expected behavior in ESPHome
- Remove legacy app-managed audio routing hooks and rely on native SDK/system audio selection
- Harden startup against import-time failures (lazy emotion library loading and graceful Sendspin disable)

### Changed
- Keep idle antenna behavior as animation-only control (no torque coupling)
- Tighten preference loading to current schema (no legacy config fallback filtering)

### Added
- Home Assistant blueprint for Reachy presence companion automation
- GitHub workflow to auto-create releases when pyproject/changelog version updates produce a new tag

### Improved
- Blueprint supports device-first auto-binding and richer usage instructions
- Refresh landing page (`index.html`) with current version, GitHub source link, and new Blueprint/Auto Release capability cards

## [1.0.1] - 2026-03-05

### Changed
- Update runtime dependency baseline to `reachy-mini>=1.5.0`

### Fixed
- Remove legacy Zenoh 7447 startup precheck for SDK v1.5 compatibility
- Remove legacy ZError string matching from connection error handling
- Adapt daemon status handling to SDK v1.5 `DaemonStatus` object (prevents `AttributeError` on `status.get`)
- Harden stop-word handling with runtime activation/deactivation and mute-aware trigger gating
- Align wakeup stream start timing with reference behavior (start microphone stream after wakeup sound)
- Improve TTS streaming robustness and reduce cutoffs with retry-based audio push

### Optimized
- Support single-request streaming with in-memory fallback cache for one-time TTS URLs (no temp file dependency)
- Lower streaming fetch chunk size and apply unthrottled preroll for faster first audio

## [1.0.0] - 2026-03-04

### Changed
- Require `reachy-mini[gstreamer]>=1.4.1`

### Added
- Sendspin switch in ESPHome (default OFF, persistent, runtime enable/disable)
- Face Tracking and Gesture Detection switches in ESPHome (both default OFF, persistent)
- Face Confidence number entity (0.0-1.0, persistent)

### Fixed
- Improve gesture responsiveness and stability (faster smoothing, min processing cadence, no-gesture alignment)
- Auto-match ONNX gesture input size from model shape to prevent `INVALID_ARGUMENT` dimension errors
- Disable antenna torque in idle mode and re-enable outside idle to reduce chatter/noise
- Enforce deterministic audio startup path and fail fast when microphone capture is not ready
- Add on-demand `/snapshot` JPEG generation when no cached stream frame is available

### Optimized
- Unload/reload face and gesture models when toggled off/on to save resources
- Update idle behavior to breathing + look-around alternation, idle antenna sway disabled
- Adjust idle breathing to human-like cadence
- Make MJPEG streaming viewer-aware (skip continuous JPEG encode/push when no stream clients)
- Keep face/gesture AI processing active even when stream viewers are absent

### Changed
- Use camera backend default FPS/resolution for stream path instead of forcing fixed 1080p/25fps

## [0.9.9] - 2026-01-28

### Fixed
- **SDK Buffer Overflow During Idle**
  - Add SDK buffer flush on GStreamer lock timeout
  - Prevents buffer overflow during long idle periods when lock contention prevents buffer drainage
  - Audio thread flushes SDK audio buffer when lock acquisition times out
  - Camera thread flushes SDK video buffer when lock acquisition times out
  - Audio playback flushes SDK playback buffer when lock acquisition times out
  - Resolves SDK crashes during extended wake-up idle periods without conversation
  - Requires Reachy Mini hardware (not applicable to simulation mode)

### Fixed
- **Memory Leaks**
  - Audio buffer memory leak - added size limit to prevent unbounded growth
  - Temp file leak - downloaded audio files now cleaned up after playback
  - Multiple memory leak and resource leak issues fixed
  - Thread-safe draining flag using threading.Event
  - Silent failures now logged for debugging

### Optimized
- **Gesture Recognition Sensitivity**
  - Simplify GestureSmoother to frequency-based confirmation (1 frame)
  - Remove all confidence filtering - return all detections to Home Assistant
  - Remove unused parameters (confidence_threshold, detection_threshold, GestureConfig)
  - Remove duplicate empty check in gesture detection
  - Add GestureSmoother class with history tracking for stable output
  - Reduce gesture detection interval from 3 frames to 1 frame for higher frequency
  - Fix: Gesture detection now returns all detected hands instead of only the highest confidence one
  - Matches reference implementation behavior for improved detection rate
  - No conflicts with face tracking (shared frame, independent processing)

### Code Quality
- Fix Ruff linter issues (import ordering, missing newlines, __all__ sorting)
- Format code with Ruff formatter (5 files reformatted)
- Fix slice index error in gesture detection (convert coordinates to integers)
- Fix Python 3.12 type annotation compatibility

## [0.9.8] - 2026-01-27

### New
- Mute switch entity - suspends voice services only (not camera/motion)
- Disable Camera switch entity - suspends camera and AI processing
- Home Assistant connection-driven feature loading
- Automatic suspend/resume on HA disconnect/reconnect

### Fixed
- Camera disable logic - corrected inverted conditions for proper operation
- Prevent daemon crash when entering idle state
- Camera preview in Home Assistant
- SDK crash during idle - optimized audio processing to skip get_frame() when not streaming to Home Assistant, reducing GStreamer resource competition
- Add GStreamer threading lock to prevent pipeline competition between audio, playback, and camera threads
- Audio thread gets priority during conversations - bypasses lock when conversation is active
- Remove GStreamer lock to fix wake word detection in idle state (lock was preventing wake word detection)

### Optimized
- Reduce log output by 30-40%
- Bundle face tracking model with package - eliminated HuggingFace download dependency, removed huggingface_hub from requirements, models now load from local package directory for offline operation
- Replace HTTP API polling with SDK Zenoh for daemon status monitoring to reduce uvicorn blocking and improve stability
- Device ID now reads /etc/machine-id directly - removed uuid.getnode() and file persistence
- Implement high-priority SDK improvements
- Remove aiohttp dependency from daemon_monitor - fully migrated to SDK Zenoh

### Removed
- Temporarily disable emotion playback during TTS
- Unused config items (connection_timeout)

### Code Quality
- Code quality improvements

## [0.9.7] - 2026-01-20

### Fixed
- Device ID file path corrected after util.py moved to core/ subdirectory (prevents HA seeing device as new)
- Animation file path corrected (was looking in wrong directory)
- Remove hey_jarvis from required wake words (it's optional in openWakeWord/)

## [0.9.6] - 2026-01-20

### New
- Add ruff linter/formatter and mypy type checker configuration
- Add pre-commit hooks for automated code quality checks

### Fixed
- Remove duplicate resume() method in audio_player.py
- Remove duplicate connection_lost() method in satellite.py
- Store asyncio task reference in sleep_manager.py to prevent garbage collection

### Optimized
- Use dict.items() for efficient iteration in smoothing.py

## [0.9.5] - 2026-01-19

### Refactored
- Modularize codebase - new core/motion/vision/audio/entities module structure
- Remove legacy/compatibility code
- Remove audio diagnostics debug code

### New
- Direct callbacks for HA sleep/wake buttons to suspend/resume services

### Optimized
- Audio processing latency - reduced chunk size from 1024 to 256 samples (64ms → 16ms)
- Audio loop delay reduced from 10ms to 1ms for faster VAD response
- Stereo to mono conversion uses first channel instead of mean for cleaner signal

### Improved
- Camera resume_from_suspend now synchronous for reliable wake from sleep
- Rotation clamping in face tracking to prevent IK collisions
- Audio gain boosted for faster VAD detection
- Audio NaN/Inf values causing STT issues fixed

## [0.9.0] - 2026-01-18

### New
- Robot state monitor for proper sleep mode handling - services pause when robot disconnects and resume on reconnect
- System diagnostics entities (CPU, memory, disk, uptime) exposed as Home Assistant diagnostic sensors
- Phase 24 with 9 diagnostic sensors (cpu_percent, cpu_temperature, memory_percent, memory_used_gb, disk_percent, disk_free_gb, uptime_hours, process_cpu_percent, process_memory_mb)

### Fixed
- Voice assistant and movement manager now properly pause during robot sleep mode instead of generating error spam

### Improved
- Graceful service lifecycle management with RobotStateMonitor callbacks

## [0.8.7] - 2026-01-18

### Fixed
- Clamp body_yaw to safe range to prevent IK collision warnings during emotion playback
- Emotion moves and face tracking now respect SDK safety limits

### Improved
- Face tracking smoothness - removed EMA smoothing (matches reference project)
- Face tracking timing updated to match reference (2s delay, 1s interpolation)

## [0.8.6] - 2026-01-18

### Fixed
- Audio buffer memory leak - added size limit to prevent unbounded growth
- Temp file leak - downloaded audio files now cleaned up after playback
- Camera thread termination timeout increased for clean shutdown
- Thread-safe draining flag using threading.Event
- Silent failures now logged for debugging

## [0.8.5] - 2026-01-18

### Fixed
- DOA turn-to-sound direction inverted - now turns correctly toward sound source
- Graceful shutdown prevents daemon crash on app stop

## [0.8.4] - 2026-01-18

### Improved
- Smooth idle animation with interpolation phase (matches reference BreathingMove)
- Two-phase animation - interpolates to neutral before oscillation
- Antenna frequency updated to 0.5Hz (was 0.15Hz) for more natural sway

## [0.8.3] - 2026-01-18

### Fixed
- Body now properly follows head rotation during face tracking
- body_yaw extracted from final head pose matrix and synced with head_yaw
- Matches reference project sweep_look behavior for natural body movement

## [0.8.2] - 2026-01-18

### Fixed
- Body follows head rotation during face tracking - body_yaw syncs with head_yaw
- Matches reference project sweep_look behavior for natural body movement

## [0.8.1] - 2026-01-18

### Fixed
- face_detected entity now pushes state updates to Home Assistant in real-time
- Body yaw simplified to match reference project - SDK automatic_body_yaw handles collision prevention
- Idle animation now starts immediately on app launch
- Smooth antenna animation - removed pose change threshold for continuous motion

## [0.8.0] - 2026-01-17

### New
- Comprehensive emotion keyword mapping with 280+ Chinese and English keywords
- 35 emotion categories mapped to robot expressions
- Auto-trigger expressions from conversation text patterns

## [0.7.3] - 2026-01-12

### Fixed
- Revert to reference project pattern - use refractory period instead of state flags
- Remove broken _in_pipeline and _tts_playing state management
- Restore correct RUN_END event handling from linux-voice-assistant

## [0.7.2] - 2026-01-12

### Fixed
- Remove premature _tts_played reset in RUN_END event
- Ensure _in_pipeline stays True until TTS playback completes

## [0.7.1] - 2026-01-12

### Fixed
- Prevent wake word detection during TTS playback
- Add _tts_playing flag to track TTS audio state precisely

## [0.7.0] - 2026-01-12

### New
- Gesture detection using HaGRID ONNX models (18 gesture classes)
- gesture_detected and gesture_confidence entities in Home Assistant

### Fixed
- Gesture state now properly pushed to Home Assistant in real-time

### Optimized
- Aggressive power saving - 0.5fps idle mode after 30s without face
- Gesture detection only runs when face detected (saves CPU)

## [0.6.1] - 2026-01-12

### Fixed
- Prioritize MicroWakeWord over OpenWakeWord for same-name wake words
- OpenWakeWord wake words now visible in Home Assistant selection
- Stop word detection now works correctly
- STT/LLM response time improved with fixed audio chunk size

## [0.6.0] - 2026-01-11

### New
- Real-time audio-driven speech animation (SwayRollRT algorithm)
- JSON-driven animation system - all animations configurable

### Refactored
- Remove hardcoded actions, use animation offsets only

### Fixed
- TTS audio analysis now works with local playback

## [0.5.16] - 2026-01-11

### Removed
- Tap-to-wake feature (too many false triggers)

### New
- Continuous Conversation switch in Home Assistant

### Refactored
- Simplified satellite.py and voice_assistant.py

## [0.5.15] - 2026-01-11

### New
- Audio settings persistence (AGC, Noise Suppression, Tap Sensitivity)

### Refactored
- Move Sendspin mDNS discovery to zeroconf.py

### Fixed
- Tap detection not re-enabled during emotion playback in conversation

## [0.5.14] - 2026-01-11

### Fixed
- Skip ALL wake word processing when pipeline is active
- Eliminate race condition in pipeline state during continuous conversation

### Improved
- Control loop increased to 100Hz (daemon updated)

## [0.5.13] - 2026-01-10

### New
- JSON-driven animation system for conversation states
- AnimationPlayer class inspired by SimpleDances project

### Refactored
- Replace SpeechSwayGenerator and BreathingAnimation with unified animation system

## [0.5.12] - 2026-01-10

### Removed
- Deleted broken hey_reachy wake word model

### Revert
- Default wake word back to "Okay Nabu"

## [0.5.11] - 2026-01-10

### Fixed
- Reset feature extractors when switching wake words
- Add refractory period after wake word switch

## [0.5.10] - 2026-01-10

### Fixed
- Wake word models now have 'id' attribute set correctly
- Wake word switching from Home Assistant now works

## [0.5.9] - 2026-01-10

### New
- Default wake word changed to hey_reachy

### Fixed
- Wake word switching bug

## [0.5.8] - 2026-01-09

### Fixed
- Tap detection waits for emotion playback to complete
- Poll daemon API for move completion

## [0.5.7] - 2026-01-09

### New
- DOA turn-to-sound at wakeup

### Fixed
- Show raw DOA angle in Home Assistant (0-180)
- Invert DOA yaw direction

## [0.5.6] - 2026-01-08

### Fixed
- Better pipeline state tracking to prevent duplicate audio

## [0.5.5] - 2026-01-08

### New
- Prevent concurrent pipelines
- Add prompt sound for continuous conversation

## [0.5.4] - 2026-01-08

### Fixed
- Wait for RUN_END before starting new conversation

## [0.5.3] - 2026-01-08

### Fixed
- Improve continuous conversation with conversation_id tracking

## [0.5.2] - 2026-01-08

### Fixed
- Enable HA control of robot pose
- Continuous conversation improvements

## [0.5.1] - 2026-01-08

### Fixed
- Sendspin connects to music_player instead of tts_player
- Persist tap_sensitivity settings
- Pause Sendspin during voice assistant wakeup
- Sendspin prioritize 16kHz sample rate

## [0.5.0] - 2026-01-07

### New
- Face tracking with adaptive frequency
- Sendspin multi-room audio integration

### Optimized
- Shutdown mechanism improvements

## [0.4.0] - 2026-01-07

### Fixed
- Daemon stability fixes

### New
- Face tracking enabled by default

### Optimized
- Microphone settings for better sensitivity

## [0.3.0] - 2026-01-06

### New
- Tap sensitivity slider entity

### Fixed
- Music Assistant compatibility

### Optimized
- Face tracking and tap detection

## [0.2.21] - 2026-01-06

### Fixed
- Daemon crash - reduce control loop to 2Hz
- Pause control loop during audio playback

## [0.2.20] - 2026-01-06

### Revert
- Audio/satellite/voice_assistant to v0.2.9 working state

## [0.2.19] - 2026-01-06

### Fixed
- Force localhost connection mode to prevent WebRTC errors

## [0.2.18] - 2026-01-06

### Fixed
- Audio playback - restore wakeup sound
- Use push_audio_sample for TTS

## [0.2.17] - 2026-01-06

### Removed
- head_joints/passive_joints entities
- error_message to diagnostic category

## [0.2.16] - 2026-01-06

### Fixed
- TTS playback - pause recording during playback

## [0.2.15] - 2026-01-06

### Fixed
- Use play_sound() instead of push_audio_sample() for TTS

## [0.2.14] - 2026-01-06

### Fixed
- Pause audio recording during TTS playback

## [0.2.13] - 2026-01-06

### Fixed
- Don't manually start/stop media - let SDK/daemon manage it

## [0.2.12] - 2026-01-05

### Fixed
- Disable breathing animation to prevent serial port overflow

## [0.2.11] - 2026-01-05

### Fixed
- Disable wakeup sound to prevent daemon crash
- Add debug logging for troubleshooting

## [0.2.10] - 2026-01-05

### Added
- Debug logging for motion init

### Fixed
- Audio fallback samplerate

## [0.2.9] - 2026-01-05

### Removed
- DOA/speech detection - replaced by face tracking

## [0.2.8] - 2026-01-05

### New
- Replace DOA with YOLO face tracking

## [0.2.7] - 2026-01-05

### Fixed
- Add DOA caching to prevent ReSpeaker query overload

## [0.2.6] - 2026-01-05

### New
- Thread-safe ReSpeaker USB access to prevent daemon deadlock

## [0.2.4] - 2026-01-05

### Fixed
- Microphone volume control via daemon HTTP API

## [0.2.3] - 2026-01-05

### Fixed
- Daemon crash caused by conflicting pose commands
- Disable: Pose setter methods in ReachyController

## [0.2.2] - 2026-01-05

### Fixed
- Second conversation motion failure
- Reduce: Control loop from 20Hz to 10Hz
- Improve: Connection recovery (faster reconnect)

## [0.2.1] - 2026-01-05

### Fixed
- Daemon crash issue
- Optimize: Code structure

## [0.2.0] - 2026-01-05

### New
- Automatic facial expressions during conversation
- New: Emotion playback integration

### Refactored
- Integrate emotion playback into MovementManager

## [0.1.5] - 2026-01-04

### Optimized
- Code splitting and organization

### Fixed
- Program crash issues

## [0.1.0] - 2026-01-01

### New
- Initial release
- ESPHome protocol server implementation
- mDNS auto-discovery for Home Assistant
- Local wake word detection (microWakeWord)
- Voice assistant pipeline integration
- Basic motion feedback (nod, shake)

---

## Version History Summary

| Version | Date | Major Changes |
|---------|------|--------------|
| 0.9.9 | 2026-01-28 | SDK buffer overflow fixes, memory leak fixes, gesture detection optimization |
| 0.9.8 | 2026-01-27 | Mute/Disable entities, HA connection-driven features, log reduction |
| 0.9.7 | 2026-01-20 | Device ID path fix, animation path fix |
| 0.9.6 | 2026-01-20 | Code quality tools (ruff, mypy, pre-commit) |
| 0.9.5 | 2026-01-19 | Modular architecture refactoring, audio latency optimization |
| 0.9.0 | 2026-01-18 | Robot state monitor, system diagnostics entities |
| 0.8.7 | 2026-01-18 | Body yaw clamping, face tracking smoothness |
| 0.8.0 | 2026-01-17 | Emotion keyword mapping (280+ keywords, 35 categories) |
| 0.7.0 | 2026-01-12 | Gesture detection with HaGRID ONNX models (18 gestures) |
| 0.6.0 | 2026-01-11 | Real-time audio-driven speech animation, JSON animation system |
| 0.5.0 | 2026-01-07 | Face tracking, Sendspin multi-room audio |
| 0.4.0 | 2026-01-07 | Daemon stability, microphone optimization |
| 0.3.0 | 2026-01-06 | Tap sensitivity slider |
| 0.2.0 | 2026-01-05 | Emotion playback integration |
| 0.1.0 | 2026-01-01 | Initial release |

## Project Statistics

- **Total Versions**: 29 (from 0.1.0 to 0.9.9)
- **Development Period**: ~30 days (2026-01-01 to 2026-01-28)
- **Average Release Rate**: ~1 version per day
- **Lines of Code**: ~18,000 lines across 52 Python files
- **ESPHome Entities**: 54 entities implemented
- **Supported Features**:
  - Voice assistant pipeline integration
  - Local wake word detection (multiple models)
  - Face tracking with YOLO
  - Gesture detection (18 classes)
  - Multi-room audio (Sendspin)
  - Real-time speech animation
  - Emotion keyword detection (280+ keywords)
  - System diagnostics

For detailed implementation notes, see [PROJECT_PLAN.md](./PROJECT_PLAN.md).
