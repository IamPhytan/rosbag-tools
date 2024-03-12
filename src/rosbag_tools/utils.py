from __future__ import annotations

from functools import wraps
from itertools import chain
from pathlib import Path
from typing import Sequence

import click
from rosbags.typesys import get_types_from_msg, register_types


def slugify_topic(topic: str) -> str:
    """Convert topic into a filename-compatible string, slugify the topic name

    Examples:
    >>> slugify('/imu/data')
    'imu_data'
    >>> slugify('/imu/data_raw')
    'imu_data_raw'
    >>> slugify('/lidar_packets')
    'lidar_packets'

    Args:
        topic (str): ROS Topic

    Returns:
        str: Slugified ROS Topic
    """
    topic = topic[1:] if topic.startswith("/") else topic
    return topic.replace("/", "_")


def guess_msgtype(path: Path) -> str:
    """Guess message type name from path."""
    name = path.relative_to(path.parents[2]).with_suffix("")
    if "msg" not in name.parts:
        name = name.parent / "msg" / name.name
    return str(name)


def retrieve_msg_paths(parent_path: Path) -> Sequence[str | Path]:
    """Retrieve msg paths inside a parent path

    Args:
        parent_path (Path): Parent path

    Returns:
        Sequence[str, Path]: message paths in subfolders of parent_path
    """
    par_path = Path(parent_path).resolve()
    all_msg_paths = tuple(par_path.rglob("**/msg/*.msg"))
    msg_paths = tuple(p for p in all_msg_paths if "install" not in p.parts)
    return msg_paths


def custom_message_path(f):
    @wraps(f)
    @click.option(
        "--msg",
        "--msg-path",
        "msg_paths",
        type=click.Path(exists=True),
        help="Custom messages path. Can be a path to a ROS workspace.",
        multiple=True,
    )
    def wrapper(msg_paths, *args, **kwargs):
        if msg_paths:
            add_types = {}
            custom_paths = [retrieve_msg_paths(msg_path) for msg_path in msg_paths]
            custom_msg_paths = tuple(chain.from_iterable(custom_paths))
            for msgpath in custom_msg_paths:
                msgdef = msgpath.read_text(encoding="utf-8")
                add_types.update(get_types_from_msg(msgdef, guess_msgtype(msgpath)))
            register_types(add_types)
        return f(*args, **kwargs)

    return wrapper
