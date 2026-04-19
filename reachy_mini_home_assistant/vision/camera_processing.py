"""Frame capture helpers for `MJPEGCameraServer`.

The camera server intentionally provides a plain MJPEG stream only so the
robot keeps video, audio, and motion responsibilities lightweight.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from .camera_server import MJPEGCameraServer

_LOGGER = logging.getLogger(__name__)


def capture_frames(server: "MJPEGCameraServer") -> None:
    _LOGGER.info("Starting camera capture thread (fps=%s, quality=%s)", server.fps, server.quality)
    frame_count = 0
    last_log_time = time.time()
    last_capture_time = 0.0
    consecutive_failures = 0

    while server._running:
        try:
            current_time = time.time()
            active_stream = has_stream_clients(server)
            target_fps = server.fps if active_stream else server.idle_fps
            capture_interval = 1.0 / max(0.1, target_fps)

            elapsed = current_time - last_capture_time
            if elapsed < capture_interval:
                time.sleep(min(capture_interval - elapsed, 0.05))
                continue

            last_capture_time = current_time
            frame = get_camera_frame(server)
            if frame is not None:
                frame_count += 1
                consecutive_failures = 0
                success, jpeg_data = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, server.quality])
                if success:
                    with server._frame_lock:
                        server._last_frame = jpeg_data.tobytes()
                        server._last_frame_time = time.time()

                if current_time - last_log_time >= 30.0:
                    fps = frame_count / (current_time - last_log_time)
                    _LOGGER.debug("Camera: %.1f fps (%s clients)", fps, server.stream_client_count)
                    frame_count = 0
                    last_log_time = current_time
            else:
                consecutive_failures += 1
                if consecutive_failures in {30, 120, 300}:
                    _LOGGER.warning("Camera frame unavailable for %d consecutive attempts", consecutive_failures)
                time.sleep(0.05)
        except Exception as e:
            _LOGGER.error("Error capturing frame: %s", e)
            time.sleep(1.0)

    _LOGGER.info("Camera capture thread stopped")


def has_stream_clients(server: "MJPEGCameraServer") -> bool:
    with server._stream_client_lock:
        return len(server._active_stream_clients) > 0


def register_stream_client(server: "MJPEGCameraServer") -> int:
    with server._stream_client_lock:
        client_id = server._next_client_id % 1000000
        server._next_client_id += 1
        server._active_stream_clients.add(client_id)
        _LOGGER.debug("Stream client registered: %d (total: %d)", client_id, len(server._active_stream_clients))
        return client_id


def unregister_stream_client(server: "MJPEGCameraServer", client_id: int) -> None:
    with server._stream_client_lock:
        server._active_stream_clients.discard(client_id)
        _LOGGER.debug("Stream client unregistered: %d (total: %d)", client_id, len(server._active_stream_clients))


def get_camera_frame(server: "MJPEGCameraServer") -> np.ndarray | None:
    if not server._camera_ready():
        return None
    try:
        acquired = server._gstreamer_lock.acquire(timeout=0.05)
        if acquired:
            try:
                return server.reachy_mini.media.get_frame()
            finally:
                server._gstreamer_lock.release()
        _LOGGER.debug("GStreamer lock busy, skipping camera frame")
        return None
    except Exception as e:
        _LOGGER.debug("Failed to get camera frame: %s", e)
        return None
