"""Runtime lifecycle helpers for `MJPEGCameraServer`."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .camera_server import MJPEGCameraServer

_LOGGER = logging.getLogger(__name__)


async def start(server: "MJPEGCameraServer") -> None:
    if server._running:
        _LOGGER.warning("Camera server already running")
        return
    if not server._camera_ready():
        _LOGGER.warning("Camera server not started: SDK media camera is unavailable")
        return

    server._running = True
    try:
        from reachy_mini.media.media_manager import MediaBackend

        backend = server.reachy_mini.media.backend
        backend_name = {
            MediaBackend.NO_MEDIA: "No Media",
            MediaBackend.GSTREAMER: "GStreamer",
            MediaBackend.GSTREAMER_NO_VIDEO: "GStreamer (No Video)",
            MediaBackend.DEFAULT: "Default",
            MediaBackend.DEFAULT_NO_VIDEO: "Default (No Video)",
            MediaBackend.SOUNDDEVICE_OPENCV: "SoundDevice + OpenCV",
            MediaBackend.SOUNDDEVICE_NO_VIDEO: "SoundDevice (No Video)",
            MediaBackend.WEBRTC: "WebRTC",
        }.get(backend, str(backend))
        _LOGGER.info("Detected media backend: %s", backend_name)
    except ImportError:
        _LOGGER.debug("MediaBackend enum not available")
    except Exception as e:
        _LOGGER.debug("Failed to detect media backend: %s", e)

    server._capture_thread = threading.Thread(target=server._capture_frames, daemon=True, name="camera-capture")
    server._capture_thread.start()
    server._server = await asyncio.start_server(server._handle_client, server.host, server.port)
    _LOGGER.info("MJPEG Camera server started on http://%s:%d", server.host, server.port)
    _LOGGER.info("  Stream URL: http://<ip>:%d/stream", server.port)
    _LOGGER.info("  Snapshot URL: http://<ip>:%d/snapshot", server.port)


async def stop(server: "MJPEGCameraServer", join_timeout: float = 3.0) -> None:
    _LOGGER.info("Stopping MJPEG camera server...")
    server._running = False
    if server._capture_thread:
        server._capture_thread.join(timeout=join_timeout)
        if server._capture_thread.is_alive():
            _LOGGER.warning("Camera capture thread did not stop cleanly")
        server._capture_thread = None
    if server._server:
        server._server.close()
        await server._server.wait_closed()
        server._server = None
    with server._frame_lock:
        server._last_frame = None
        server._last_frame_time = 0
    with server._stream_client_lock:
        server._active_stream_clients.clear()
    _LOGGER.info("MJPEG Camera server stopped - stream resources released")


def suspend(server: "MJPEGCameraServer") -> None:
    if not server._running:
        _LOGGER.debug("Camera server not running, nothing to suspend")
        return
    _LOGGER.info("Suspending camera server resources...")
    server._running = False
    if server._capture_thread is not None:
        server._capture_thread.join(timeout=3.0)
        if server._capture_thread.is_alive():
            _LOGGER.warning("Camera capture thread did not stop cleanly during suspend")
        server._capture_thread = None
    _LOGGER.info("Camera server suspended")


def resume_from_suspend(server: "MJPEGCameraServer") -> None:
    if server._running:
        _LOGGER.debug("Camera server already running")
        return
    _LOGGER.info("Resuming camera server resources...")
    server._running = True
    server._capture_thread = threading.Thread(target=server._capture_frames, daemon=True, name="camera-capture")
    server._capture_thread.start()
    _LOGGER.info("Camera server resumed")
