"""Cut out a section of a long rosbag"""

from .clipper import BagClipper
from .main import cli as clip

__all__ = (
    "BagClipper",
    "clip",
)
