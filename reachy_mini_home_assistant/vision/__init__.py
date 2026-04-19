"""Video streaming module for Reachy Mini.

This package provides a plain MJPEG camera stream for Home Assistant and
external video services while keeping the robot-side camera path lightweight.
"""

from .camera_server import MJPEGCameraServer

__all__ = ["MJPEGCameraServer"]
