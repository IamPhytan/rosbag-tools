"""topic remover class to delete some topics from a rosbag"""

from __future__ import annotations

import fnmatch
import shutil
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, cast

from rosbags.interfaces import ConnectionExtRosbag1, ConnectionExtRosbag2
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.rosbag2 import Writer as Writer2
from tqdm import tqdm

if TYPE_CHECKING:
    from typing import Sequence, Tuple, Type


class BagTopicRemover:
    """Topic Remover : Remove topics from a rosbag"""

    def __init__(self, path: Path | str) -> None:
        """Create a BagTopicRemover instance

        Args:
            path: Path to the input rosbag
        """
        self._intopics: Tuple[str] = None
        self._is_ros1_reader: bool = None
        self._is_ros1_writer: bool = None
        self.inbag = Path(path)

    @property
    def inbag(self) -> Path:
        """The inbag property."""
        return self._inbag

    @inbag.setter
    def inbag(self, value: Path | str):
        """Setter for `inbag`"""
        vpath = Path(value)
        if vpath.is_file() or vpath.is_dir():
            self._inbag = vpath
            Reader = self.get_reader_class(self._inbag)
            with Reader(self._inbag) as inbag:
                self._intopics = tuple(inbag.topics.keys())
        else:
            raise ValueError(f"{value} is not an existing file")

    @property
    def topics(self):
        """The topics property."""
        return self._intopics

    def get_reader_class(self, filename: Path | str) -> Type[Reader1 | Reader2]:
        """Return the reader class that corresponds to the filename
        Needs the filename of the rosbag to read from
        """
        is_ros1 = Path(filename).suffix == ".bag"
        self._is_ros1_reader = is_ros1
        return Reader1 if is_ros1 else Reader2

    def get_writer_class(self, filename: Path | str) -> Type[Writer1 | Writer2]:
        """Return the writer class that corresponds to the filename
        Needs the filename of the rosbag to write in
        """
        is_ros1 = Path(filename).suffix == ".bag"
        self._is_ros1_writer = is_ros1
        return Writer1 if is_ros1 else Writer2

    @staticmethod
    def filter_out_topics(
        bag_topics: Sequence[str], patterns_to_remove: Sequence[str]
    ) -> Tuple[str]:
        """Filter out topics

        Examples:
        >>> bag_topics = ('/cmd_vel', '/imu/data', '/imu/data_raw', '/imu/odom', '/lidar_packets', '/map', '/velocity')
        >>> to_filter = ('/imu/*', '/lidar_packets')
        >>> BagTopicRemover.filter_out_topics(bag_topics, to_filter)
        ('/cmd_vel', '/map', '/velocity')
        >>> to_filter = ('/cmd_vel', '/map', '/velocity')
        >>> BagTopicRemover.filter_out_topics(bag_topics, to_filter)
        ('/imu/data', '/imu/data_raw', '/imu/odom', '/lidar_packets')
        >>> bag_topics = ('/imu/data', '/imu/data_raw', '/imu/odom')
        >>> to_filter = ('/camera/image_raw')
        >>> BagTopicRemover.filter_out_topics(bag_topics, to_filter)
        ('/imu/data', '/imu/data_raw', '/imu/odom')
        >>> bag_topics = ('/imu/data', '/imu/data_raw', '/imu/odom')
        >>> to_filter = ()
        >>> BagTopicRemover.filter_out_topics(bag_topics, to_filter)
        ('/imu/data', '/imu/data_raw', '/imu/odom')

        Args:
            bag_topics: input rosbag's topics
            patterns_to_remove: topics to filter out

        Returns:
            tuple: Filtered topics that were not targeted by the pattern
        """
        # Accumulate a list of topics
        topics_to_remove = []
        for pattern in patterns_to_remove:
            pattern_topics = fnmatch.filter(bag_topics, pattern)
            topics_to_remove.extend(pattern_topics)

        # Keep only one copy of each element in the list
        topics_to_remove = tuple(set(topics_to_remove))

        filtered_topics = tuple(
            topic for topic in bag_topics if topic not in topics_to_remove
        )
        return filtered_topics

    def remove(self, patterns: Sequence[str] | str = ("",)) -> None:
        """Remove topic patterns or specific topics from self._intopics

        Args:
            patterns: List, tuple of strings or string that contains a pattern or a specific topic name to remove from the bag
        """
        if isinstance(patterns, str):
            patterns = (patterns,)
        self._intopics = self.filter_out_topics(self._intopics, patterns)

    def _delete_rosbag(self, path: Path | str):
        """Function to delete a rosbag at path `path`, to use with caution

        Args:
            path: Path to rosbag to delete.
        """
        is_ros1 = path.is_file() and path.suffix == ".bag"
        is_ros2 = path.is_dir() and len(tuple(path.glob("*.db3"))) > 0
        if is_ros1:
            path.unlink()
        elif is_ros2:
            shutil.rmtree(path)
        else:
            raise ValueError(f"Path {path} is not a valid rosbag")

    def export(self, path: Path | str, force_output_overwrite: bool = False) -> None:
        """Export filtered rosbag to 'path'

        Args:
            path: Path to export the rosbag.
            force_output_overwrite: Force output overwriting if path already exists. Defaults to False.

        Raises:
            FileExistsError: _description_
            FileExistsError: _description_
        """
        outpath = Path(path)
        if outpath == self._inbag:
            raise FileExistsError(f"Cannot use same file as input and output [{path}]")
        if outpath.exists() and not force_output_overwrite:
            raise FileExistsError(
                f"Path {path} already exists. "
                "Use 'force_output_overwrite=True' or `rosbag-tools topic-remove -f` "
                f"to export to {path}, even if output bag already exists."
            )
        if outpath.exists() and force_output_overwrite:
            warnings.warn(
                f"Output path {outpath} already exists, output overwriting flag has been set, deleting old output file"
            )
            self._delete_rosbag(outpath)

        # Reader / Writer classes
        Reader = self.get_reader_class(self.inbag)
        Writer = self.get_writer_class(path)
        if self._is_ros1_reader != self._is_ros1_writer:
            raise NotImplementedError(
                "Rosbag conversion (ROS 1->ROS 2 / ROS 2->ROS 1) is not supported. "
                "Use `rosbags` to convert your rosbag before using `rosbag-tools topic-remove`."
            )
        with Reader(self.inbag) as reader, Writer(outpath) as writer:
            conn_map = {}
            ConnectionExt = (
                ConnectionExtRosbag1 if self._is_ros1_writer else ConnectionExtRosbag2
            )
            for conn in reader.connections:
                if conn.topic in self._intopics:
                    ext = cast(ConnectionExt, conn.ext)
                    if self._is_ros1_writer:
                        conn_map[conn.id] = writer.add_connection(
                            conn.topic,
                            conn.msgtype,
                            conn.msgdef,
                            conn.digest,
                            ext.callerid,
                            ext.latching,
                        )
                    else:
                        # ROS 2
                        conn_map[conn.id] = writer.add_connection(
                            conn.topic,
                            conn.msgtype,
                            serialization_format=ext.serialization_format,
                            offered_qos_profiles=ext.offered_qos_profiles,
                        )

            with tqdm(total=reader.message_count) as pbar:
                for conn, timestamp, data in reader.messages():
                    if conn.topic in self._intopics:
                        writer.write(conn_map[conn.id], timestamp, data)
                    pbar.update(1)

        print(f"[topic-remove] Done ! Exported in {path}")
