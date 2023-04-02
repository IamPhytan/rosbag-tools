"""Remove topics from rosbags"""

from .main import cli as topic_remove
from .topic_remover import BagTopicRemover

__all__ = (
    "BagTopicRemover",
    "topic_remove",
)
