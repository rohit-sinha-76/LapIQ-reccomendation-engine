"""Segment weight profiles for deterministic scoring calculations."""

from typing import Final

SEGMENT_WEIGHTS: Final[dict[str, dict[str, float]]] = {
    "Student": {
        "battery": 0.30,
        "value": 0.30,
        "portability": 0.20,
        "performance": 0.20,
    },
    "Professional": {
        "performance": 0.30,
        "value": 0.25,
        "portability": 0.25,
        "battery": 0.20,
    },
    "Gamer": {
        "performance": 0.50,
        "value": 0.25,
        "battery": 0.15,
        "portability": 0.10,
    },
    "Creator": {
        "performance": 0.45,
        "value": 0.25,
        "portability": 0.20,
        "battery": 0.10,
    },
}
