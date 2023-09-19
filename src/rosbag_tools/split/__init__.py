"""Split a long rosbag into smaller rosbag sections"""

from .main import cli as split
from .splitter import BagSplitter

__all__ = (
    "BagSplitter",
    "split",
)
