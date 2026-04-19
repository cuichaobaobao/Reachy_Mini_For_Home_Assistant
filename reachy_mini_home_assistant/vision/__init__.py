"""Vision module for Reachy Mini.

This package provides a plain MJPEG camera stream for Home Assistant and
external vision services. Robot-side face and gesture AI have been removed to
keep this app lightweight.
"""

from .camera_server import MJPEGCameraServer

__all__ = ["MJPEGCameraServer"]
