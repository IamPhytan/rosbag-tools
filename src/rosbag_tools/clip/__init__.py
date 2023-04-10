"""Cut out a section of a long rosbag"""

from .main import cli as clip
from .clipper import BagClipper

__all__ = (
    "BagClipper",
    "clip",
)
