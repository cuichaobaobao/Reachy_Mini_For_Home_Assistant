# Reachy Mini 语音助手 - 用户手册

## 系统要求

### 硬件
- Reachy Mini 机器人（带 ReSpeaker XVF3800 麦克风）
- WiFi 网络连接

### 软件
- Home Assistant（2024.1 或更高版本）
- Home Assistant 中已启用 ESPHome 集成

---

## 安装步骤

### 第一步：安装应用
从 Reachy Mini 应用商店安装 `reachy_mini_home_assistant_custom`。

### 第二步：启动应用
应用将自动：
- 在端口 6053 启动 ESPHome 卫星服务
- 加载本地唤醒词模型
- 通过 mDNS 注册以便 Home Assistant 自动发现

### 第三步：连接 Home Assistant
**自动连接（推荐）：**
Home Assistant 会通过 mDNS 自动发现 Reachy Mini。

**手动连接：**
1. 进入 设置 → 设备与服务
2. 点击“添加集成”
3. 选择“ESPHome”
4. 输入机器人的 IP 地址和端口 6053

---

## 功能介绍

### 语音助手
- **唤醒词检测**：说 “Okay Nabu” 激活（本地处理）
- **停止词**：说 “Stop” 中断播放或结束当前语音输出
- **连续对话模式**：无需重复唤醒词即可持续对话
- **语音识别/合成**：使用 Home Assistant 配置的 STT、TTS 和对话管线

**支持的唤醒词：**
- Okay Nabu（默认）
- Hey Jarvis
- Alexa
- Hey Luna

### 动作与待机
- 唤醒、聆听、思考、说话和计时器提醒都有内建动作
- 支持官方呼吸待机、天线动作和实时生成的空闲微动作
- 支持手动 Head Yaw 平滑转向并保持角度
- 手动转向时身体会跟随头部方向
- 对话结束后会按当前设置回正或保持手动角度

### DOA 声源追踪
- 使用麦克风阵列的声源方向数据
- 唤醒时机器人可转向声源
- 可通过 Home Assistant 开关启用/禁用

### 情绪响应
机器人可播放 35 种不同情绪，包括开心、难过、愤怒、惊讶、大笑、爱慕、好奇、沉思、疲倦等。

### 音频功能
- 扬声器音量控制（0-100%）
- 静音开关，可暂停/恢复语音链路
- 支持唤醒提示音与计时器完成提示音
- STT/TTS 由 Home Assistant 负责

## Home Assistant 实体

### 阶段 1：基础状态
| 实体 | 类型 | 说明 |
|------|------|------|
| Daemon State | 文本传感器 | 机器人守护进程状态 |
| Backend Ready | 二进制传感器 | 后端连接状态 |
| Mute | 开关 | 暂停/恢复语音链路 |
| Speaker Volume | 数值 (0-100%) | 扬声器音量控制 |
| Idle Behavior | 开关 | 统一空闲行为：头部、天线、微动作 |

### 阶段 2：运行状态
| 实体 | 类型 | 说明 |
|------|------|------|
| Services Suspended | 二进制传感器 | 运行中表示服务活跃 |

### 阶段 3：姿态控制
| 实体 | 类型 | 范围 |
|------|------|------|
| Head X/Y/Z | 数值 | ±50mm |
| Head Roll/Pitch/Yaw | 数值 | ±40° |
| Body Yaw | 数值 | ±160° |
| Antenna Left/Right | 数值 | ±90° |

### 阶段 5：DOA（声源定位）
| 实体 | 类型 | 说明 |
|------|------|------|
| DOA Angle | 传感器 (°) | 声源方向 |
| Speech Detected | 二进制传感器 | 语音活动检测 |
| DOA Sound Tracking | 开关 | 启用/禁用 DOA 追踪 |

### 阶段 6：诊断信息
| 实体 | 类型 | 说明 |
|------|------|------|
| Control Loop Frequency | 传感器 (Hz) | 运动控制循环频率 |
| SDK Version | 文本传感器 | Reachy Mini SDK 版本 |
| Robot Name | 文本传感器 | 设备名称 |
| Wireless Version | 二进制传感器 | 无线版本标志 |
| Simulation Mode | 二进制传感器 | 仿真模式标志 |
| WLAN IP | 文本传感器 | WiFi IP 地址 |
| Error Message | 文本传感器 | 当前错误 |

### 阶段 7：IMU 传感器（仅无线版本）
| 实体 | 类型 | 说明 |
|------|------|------|
| IMU Accel X/Y/Z | 传感器 (m/s²) | 加速度计 |
| IMU Gyro X/Y/Z | 传感器 (rad/s) | 陀螺仪 |
| IMU Temperature | 传感器 (°C) | IMU 温度 |

### 阶段 8：情绪控制
| 实体 | 类型 | 说明 |
|------|------|------|
| Emotion | 选择器 | 选择要播放的情绪（35 个选项） |

### 阶段 21：对话
| 实体 | 类型 | 说明 |
|------|------|------|
| Continuous Conversation | 开关 | 多轮对话模式 |

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 不响应唤醒词 | 检查 Mute 是否关闭，减少背景噪音，并确认已连接 Home Assistant |
| 没有音频输出 | 检查 Speaker Volume，验证 HA 中的 TTS 引擎 |
| 无法连接 HA | 确认在同一网络，检查端口 6053 |
| 动作没有响应 | 确认电机已启用，检查机器人 daemon 状态 |

---

## 快速参考

```
唤醒词：       "Okay Nabu"
停止词：       "Stop"
ESPHome 端口： 6053
```

---

*Reachy Mini 语音助手 v1.0.36*
