"""Compute the duration of every rosbag in a folder"""

from .main import cli as compute_duration
from .duration_calculator import DurationCalculator

__all__ = (
    "DurationCalculator",
    "compute_duration",
)
