"""ROSBag clipper class"""

from __future__ import annotations

import shutil
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, List, cast

from rosbags.interfaces import Connection, ConnectionExtRosbag1, ConnectionExtRosbag2
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.rosbag2 import Writer as Writer2
from tqdm import tqdm

from rosbag_tools import exceptions

if TYPE_CHECKING:
    from typing import Type


class BagClipper:
    """Clipper: Cut a rosbag based on timestamps."""

    def __init__(
        self,
        path: Path | str,
    ) -> None:
        self._bag_start: float = None
        self._bag_end: float = None
        self._bag_duration: float = None
        self._is_ros1_reader: bool = None
        self._is_ros1_writer: bool = None
        self.inbag: Path = Path(path)

    @property
    def inbag(self) -> Path:
        """Path to input rosbag"""
        return self._inbag

    @inbag.setter
    def inbag(self, value: Path | str):
        # Check that path exists
        if not Path(value).exists():
            raise FileNotFoundError(
                f"File {value} is not an existing file. Please provide a path that exists in your file system"
            )
        self._inbag = Path(value)
        Reader = self.get_reader_class(self._inbag)
        with Reader(self._inbag) as bag:
            self._bag_start = bag.start_time
            self._bag_end = bag.end_time
            self._bag_duration = bag.duration

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

    def _check_cutoff_limits(
        self,
        start: float | None = None,
        end: float | None = None,
    ):
        """Check that clip limits are in the range of the bag

        Args:
            start (float, optional): Starting time. Defaults to None.
            end (float, optional): Ending time. Defaults to None.

        Raises:
            InvalidTimestampError: _raised if `start` is not in the rosbag_
            InvalidTimestampError: _raised if `end` is not in the rosbag_
            InvalidTimestampError: _raised if `end` < `start`_
        """
        slimit = start is not None
        elimit = end is not None
        start_ns = start * 10**9 if slimit else start
        end_ns = end * 10**9 if elimit else end
        if slimit and start_ns < 0 and start_ns > self._bag_duration:
            raise exceptions.InvalidTimestampError(
                f"Start time ({start} s) is not in the bag. "
                f"Start time should be defined between 0 and {self._bag_duration} s."
            )
        if elimit and end_ns < 0 and end_ns > self._bag_duration:
            raise exceptions.InvalidTimestampError(
                f"End time ({end} s) is not in the bag. "
                f"End time should be defined between 0 and {self._bag_duration} s."
            )
        if slimit and elimit and end < start:
            raise exceptions.InvalidTimestampError(
                f"Start time (s: {start}) should come " f"before ending time (e: {end})."
            )

    def _check_export_path(self, export_path: Path, force_out: bool) -> None:
        """Check export path
        Avoids overwriting when not requested
        """
        if export_path == self._inbag:
            raise FileExistsError(
                f"Cannot use same file as input and output [{export_path.name}]"
            )
        if export_path.exists() and not force_out:
            raise FileExistsError(
                f"Path {export_path.name} already exists. "
                "Use 'force_out=True' or 'rosbag-tools clip -f' to "
                f"export to {export_path.name} even if output bag already exists."
            )
        if export_path.exists() and force_out:
            warnings.warn(
                f"Output path {export_path.name} already exists, output overwriting flag has been set, deleting old output file"
            )
            self._delete_rosbag(export_path)

    def _set_writer_connections(
        self,
        writer: Writer1 | Writer2,
        connections: List[Connection],
    ) -> dict:
        """Generate connection map from Reader connections and a Writer instance

        Args:
            writer (Writer1 | Writer2): Writer Instance
            connections (List[Connection]): List of connections from Reader

        Returns:
            dict: Connection Map dictionary
        """
        conn_map = {}
        ConnectionExt = (
            ConnectionExtRosbag1 if self._is_ros1_writer else ConnectionExtRosbag2
        )
        for conn in connections:
            if conn.topic == "/events/write_split":
                continue
            ext = cast(ConnectionExt, conn.ext)
            if self._is_ros1_writer:
                # ROS 1
                conn_map[conn.id] = writer.add_connection(
                    conn.topic,
                    conn.msgtype,
                    conn.msgdef,
                    conn.md5sum,
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
        return conn_map

    def clip_rosbag(
        self,
        start: float | None = None,
        end: float | None = None,
        outbag_path: Path | str = None,
        force_out: bool = False,
    ):
        """Clip rosbag between two elapsed times, given relative to the beginning of the rosbag

        Args:
            start (float, optional): Start of the clip, in seconds relative to the beginning of the bag. Defaults to None. If None, the clip starts at the beginning of the rosbag.
            end (float, optional): End of the clip, in seconds relative to the beginning of the bag. Defaults to None. If None, the clip stops at the end of the rosbag.
            outbag_path (Path | str): Path of output bag.
            force_squash (bool); Force output bag overwriting, if outbag already exists. Defaults to False.
        """
        self._check_cutoff_limits(start, end)

        if start is None:
            s_cliptstamp = self._bag_start
        else:
            s_cliptstamp = self._bag_start + start * 10**9

        if end is None:
            e_cliptstamp = self._bag_end
        else:
            e_cliptstamp = self._bag_start + end * 10**9

        # Reader / Writer classes
        Reader = self.get_reader_class(self._inbag)
        Writer = self.get_writer_class(outbag_path)
        export_path = Path(outbag_path)
        self._check_export_path(export_path, force_out)
        if self._is_ros1_reader != self._is_ros1_writer:
            raise NotImplementedError(
                "Rosbag conversion (ROS 1->ROS 2 / ROS 2->ROS 1) is not supported. "
                "Use `rosbags` to convert your rosbag before using `rosbag-tools clip`."
            )
        with Reader(self._inbag) as reader, Writer(export_path) as writer:
            conn_map = self._set_writer_connections(
                writer,
                reader.connections,
            )

            with tqdm(total=reader.message_count) as pbar:
                for conn, timestamp, data in reader.messages():
                    if s_cliptstamp <= timestamp <= e_cliptstamp:
                        writer.write(conn_map[conn.id], timestamp, data)
                    pbar.update(1)

        print(f"[clip] Clipping done ! Exported in {outbag_path}")
