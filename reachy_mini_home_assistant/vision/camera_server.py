"""
MJPEG Camera Server for Reachy Mini.

This module streams frames from the Reachy Mini camera as MJPEG for Home
Assistant and external vision services. Robot-side face tracking and gesture
recognition are intentionally not included here.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import TYPE_CHECKING

import numpy as np

from .camera_http import handle_client, handle_index, handle_snapshot, handle_stream
from .camera_processing import (
    capture_frames,
    get_camera_frame,
    has_stream_clients,
    register_stream_client,
    unregister_stream_client,
)
from .camera_runtime import resume_from_suspend, start, stop, suspend

if TYPE_CHECKING:
    from reachy_mini import ReachyMini

_LOGGER = logging.getLogger(__name__)

MJPEG_BOUNDARY = "frame"


class MJPEGCameraServer:
    """
    MJPEG streaming server for Reachy Mini camera.

    Provides HTTP endpoints:
    - /stream - MJPEG video stream
    - /snapshot - Single JPEG snapshot
    - / - Simple status page
    """

    def __init__(
        self,
        reachy_mini: ReachyMini,
        host: str = "0.0.0.0",
        port: int = 8081,
        fps: int = 15,
        quality: int = 75,
        idle_fps: float = 1.0,
        gstreamer_lock: threading.Lock | None = None,
    ):
        """
        Initialize the MJPEG camera server.

        Args:
            reachy_mini: Reachy Mini robot instance.
            host: Host address to bind to.
            port: Port number for the HTTP server.
            fps: Target frames per second while clients are watching /stream.
            quality: JPEG quality (1-100).
            idle_fps: Low-rate frame refresh when no stream clients are connected.
            gstreamer_lock: Shared lock for SDK media access.
        """
        self.reachy_mini = reachy_mini
        self._gstreamer_lock = gstreamer_lock if gstreamer_lock is not None else threading.Lock()
        self.host = host
        self.port = port
        self.fps = fps
        self.quality = quality
        self.idle_fps = idle_fps

        self._server: asyncio.Server | None = None
        self._running = False
        self._last_frame: bytes | None = None
        self._last_frame_time: float = 0
        self._frame_lock = threading.Lock()
        self._capture_thread: threading.Thread | None = None

        self._active_stream_clients: set[int] = set()
        self._stream_client_lock = threading.Lock()
        self._next_client_id = 0

    def _get_media_camera(self):
        """Return the SDK camera object when video is available."""
        return self.reachy_mini.media.camera

    def _camera_ready(self) -> bool:
        """Whether the SDK reports a usable camera backend."""
        return self._get_media_camera() is not None

    async def start(self) -> None:
        await start(self)

    async def stop(self, join_timeout: float = 3.0) -> None:
        await stop(self, join_timeout=join_timeout)

    async def __aenter__(self) -> MJPEGCameraServer:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.stop()
        return False

    def suspend(self) -> None:
        suspend(self)

    def resume_from_suspend(self) -> None:
        resume_from_suspend(self)

    def _capture_frames(self) -> None:
        capture_frames(self)

    def _has_stream_clients(self) -> bool:
        return has_stream_clients(self)

    def _register_stream_client(self) -> int:
        return register_stream_client(self)

    def _unregister_stream_client(self, client_id: int) -> None:
        unregister_stream_client(self, client_id)

    @property
    def stream_client_count(self) -> int:
        """Get the number of active stream clients."""
        with self._stream_client_lock:
            return len(self._active_stream_clients)

    def _get_camera_frame(self) -> np.ndarray | None:
        return get_camera_frame(self)

    def get_snapshot(self) -> bytes | None:
        """Get the latest frame as JPEG bytes."""
        with self._frame_lock:
            return self._last_frame

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        await handle_client(self, reader, writer)

    async def _handle_index(self, writer: asyncio.StreamWriter) -> None:
        await handle_index(self, writer)

    async def _handle_snapshot(self, writer: asyncio.StreamWriter) -> None:
        await handle_snapshot(self, writer)

    async def _handle_stream(self, writer: asyncio.StreamWriter) -> None:
        await handle_stream(self, writer, MJPEG_BOUNDARY)

    @property
    def is_running(self) -> bool:
        """Check if camera server is running."""
        return self._running
