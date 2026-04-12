from __future__ import annotations

import hashlib
import logging
import socket

_LOGGER = logging.getLogger(__name__)

MOVEMENT_LATENCY_S = 0.2
SWAY_FRAME_DT_S = 0.05
STREAM_FETCH_CHUNK_SIZE = 2048
UNTHROTTLED_PREROLL_S = 0.35
SENDSPIN_LOCAL_BUFFER_CAPACITY_BYTES = 1_048_576
SENDSPIN_LATE_DROP_GRACE_US = 150_000
SENDSPIN_SCHEDULE_AHEAD_LIMIT_US = 2_000_000


def get_stable_client_id() -> str:
    try:
        hostname = socket.gethostname()
        hash_input = f"reachy-mini-{hostname}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    except Exception:
        return "reachy-mini-default"
