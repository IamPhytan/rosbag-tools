"""Compute the duration of every rosbag in a folder"""

from .duration_calculator import DurationCalculator
from .main import cli as compute_duration

__all__ = (
    "DurationCalculator",
    "compute_duration",
)
