"""Compare topics between rosbags in a folder"""

from .main import cli as topic_compare
from .topic_comparator import BagTopicComparator

__all__ = (
    "BagTopicComparator",
    "topic_compare",
)
