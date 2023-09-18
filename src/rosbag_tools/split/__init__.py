"""Cut out a section of a long rosbag"""

from .main import cli as split
from .splitter import BagSplitter

__all__ = (
    "BagSplitter",
    "split",
)
