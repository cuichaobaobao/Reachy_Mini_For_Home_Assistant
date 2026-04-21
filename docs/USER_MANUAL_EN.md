# Reachy Mini Voice Assistant - User Manual

## Requirements

### Hardware
- Reachy Mini robot with ReSpeaker XVF3800 microphone
- Wi-Fi network connection

### Software
- Home Assistant 2024.1 or later
- ESPHome integration enabled in Home Assistant

---

## Installation

### Step 1: Install the App
Install `reachy_mini_home_assistant_custom` from the Reachy Mini app store.

### Step 2: Start the App
The app automatically:
- Starts the ESPHome satellite service on port 6053
- Loads local wake word models
- Registers with mDNS for Home Assistant discovery
- Connects to a Sendspin server if one is available on the network

### Step 3: Connect to Home Assistant
**Automatic recommended:**
Home Assistant discovers Reachy Mini through mDNS.

**Manual:**
1. Go to Settings → Devices & Services
2. Click Add Integration
3. Select ESPHome
4. Enter the robot IP address and port 6053

---

## Features

### Voice Assistant
- **Wake word detection**: say “Okay Nabu” to activate, processed locally
- **Stop word**: say “Stop” to interrupt playback or end the current voice output
- **Continuous conversation mode**: continue talking without repeating the wake word
- **STT/TTS**: handled by the Home Assistant voice pipeline

**Supported wake words:**
- Okay Nabu default
- Hey Jarvis
- Alexa
- Hey Luna

### Motion and Idle Behavior
- Built-in motions for wake, listening, thinking, speaking, timer alerts, and emotions
- Idle breathing, antenna motion, and idle micro-actions
- Smooth manual Head Yaw control with hold behavior
- Body yaw follows manual and sound-source turns
- Conversation end recenters or preserves manual yaw according to the current hold state

### DOA Sound Tracking
- Uses microphone array direction-of-arrival data
- Turns the robot toward the sound source on wake
- Can be enabled or disabled from Home Assistant

### Emotion Responses
The robot can play 35 emotion moves, including happy, sad, angry, surprised, laughing, loving, curious, thoughtful, and tired.

### Audio Features
- Speaker volume control from 0 to 100 percent
- Mute switch for voice pipeline pause/resume
- Wake sound and timer-finished sound playback
- Home Assistant handles STT and TTS engines

### Sendspin Multi-Room Audio
- Automatic discovery of Sendspin servers via mDNS
- Synchronized multi-room audio playback
- Reachy Mini acts as a player receiving audio streams
- Auto-pauses during voice conversations
- No user configuration required

---

## Home Assistant Entities

### Phase 1: Basic Status
| Entity | Type | Description |
|--------|------|-------------|
| Daemon State | Text Sensor | Robot daemon status |
| Backend Ready | Binary Sensor | Backend connection status |
| Mute | Switch | Suspend/resume voice pipeline |
| Speaker Volume | Number 0-100% | Speaker volume control |
| Idle Behavior | Switch | Unified idle motion, antenna motion, and micro-actions |
| Sendspin | Switch | Enable/disable Sendspin discovery and playback |

### Phase 2: Runtime State
| Entity | Type | Description |
|--------|------|-------------|
| Services Suspended | Binary Sensor | Running when services are active |

### Phase 3: Pose Control
| Entity | Type | Range |
|--------|------|-------|
| Head X/Y/Z | Number | ±50mm |
| Head Roll/Pitch/Yaw | Number | ±40° |
| Body Yaw | Number | ±160° |
| Antenna Left/Right | Number | ±90° |

### Phase 4: Look At Control
| Entity | Type | Description |
|--------|------|-------------|
| Look At X/Y/Z | Number | World coordinates for gaze target |

### Phase 5: DOA Direction of Arrival
| Entity | Type | Description |
|--------|------|-------------|
| DOA Angle | Sensor ° | Sound source direction |
| Speech Detected | Binary Sensor | Voice activity detection |
| DOA Sound Tracking | Switch | Enable/disable DOA tracking |

### Phase 6: Diagnostics
| Entity | Type | Description |
|--------|------|-------------|
| Control Loop Frequency | Sensor Hz | Motion control loop rate |
| SDK Version | Text Sensor | Reachy Mini SDK version |
| Robot Name | Text Sensor | Device name |
| Wireless Version | Binary Sensor | Wireless model flag |
| Simulation Mode | Binary Sensor | Simulation flag |
| WLAN IP | Text Sensor | Wi-Fi IP address |
| Error Message | Text Sensor | Current error |

### Phase 7: IMU Sensors wireless version only
| Entity | Type | Description |
|--------|------|-------------|
| IMU Accel X/Y/Z | Sensor m/s² | Accelerometer |
| IMU Gyro X/Y/Z | Sensor rad/s | Gyroscope |
| IMU Temperature | Sensor °C | IMU temperature |

### Phase 8: Emotion Control
| Entity | Type | Description |
|--------|------|-------------|
| Emotion | Select | Choose one of 35 emotion moves |

### Phase 21: Conversation
| Entity | Type | Description |
|--------|------|-------------|
| Continuous Conversation | Switch | Multi-turn conversation mode |

### Phase 24: System Diagnostics
| Entity | Type | Description |
|--------|------|-------------|
| CPU Percent | Sensor % | CPU usage |
| CPU Temperature | Sensor °C | CPU temperature |
| Memory Percent | Sensor % | RAM usage |
| Memory Used | Sensor GB | RAM used |
| Disk Percent | Sensor % | Disk usage |
| Disk Free | Sensor GB | Disk free space |
| Uptime | Sensor hours | System uptime |
| Process CPU | Sensor % | App CPU usage |
| Process Memory | Sensor MB | App memory use |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Not responding to wake word | Check Mute is off, reduce background noise, and verify Home Assistant is connected |
| No audio output | Check Speaker Volume and verify the TTS engine in Home Assistant |
| Cannot connect to Home Assistant | Verify same network and port 6053 |
| Motion unavailable | Ensure motors are enabled and check robot daemon status |

---

## Quick Reference

```
Wake Word:     "Okay Nabu"
Stop Word:     "Stop"
ESPHome Port:  6053
```

---

*Reachy Mini Voice Assistant v1.0.13*
