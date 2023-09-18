"""A ROS-agnostic toolbox for common rosbag operations"""


from .clip import clip
from .split import split
from .compute_duration import compute_duration
from .topic_compare import topic_compare
from .topic_remove import topic_remove

__version__ = "0.0.5"
