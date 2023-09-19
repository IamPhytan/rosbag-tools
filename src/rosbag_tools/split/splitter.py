"""ROSBag splitter class"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, List, Sequence, cast

from rosbags.interfaces import Connection, ConnectionExtRosbag1, ConnectionExtRosbag2
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.rosbag2 import Writer as Writer2
from tqdm import tqdm

from rosbag_tools import exceptions

if TYPE_CHECKING:
    from typing import Type


class BagSplitter:
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

    @property
    def total_duration(self) -> int:
        """Duration of the bag file"""
        return self._bag_duration

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

    def _delete_rosbag(self, path: Path | str) -> None:
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

    def _check_cutoff_limits(self, timestamps: Sequence[float]) -> None:
        """Check that provided timestamps are in the range of the bag

        Args:
            timestamps (Sequence[float]): ROS timestamps

        Raises:
            InvalidTimestampError: _raised if `timestamp` is not in the rosbag_
        """
        for ts in timestamps:
            if ts < 0:
                raise exceptions.InvalidTimestampError(
                    f"Split time (s: {ts}) should come " f"after start time (s: 0)."
                )
            if ts > self.total_duration:
                raise exceptions.InvalidTimestampError(
                    f"Split time (s: {ts}) should come "
                    f"before ending time (s: {self.total_duration})."
                )

    def _check_export_path(self, export_path: Path, force_out: bool) -> None:
        if export_path == self._inbag:
            raise FileExistsError(
                f"Cannot use same file as input and output [{export_path}]"
            )
        if export_path.exists() and not force_out:
            raise FileExistsError(
                f"Path {export_path.name} already exists. "
                "Use 'force_out=True' or 'rosbag-tools split -f' to "
                f"export to {export_path.name} even if output bag already exists."
            )
        if export_path.exists() and force_out:
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

    def etoa(self, elapsed_time: float) -> float:
        """Elapsed to absolute timestamp

        Args:
            elapsed_time (float): time since the start of the ROSbag

        Returns:
            float: Absolute ROS timestamp
        """
        return elapsed_time * 1e9 + self._bag_start

    def atoe(self, absolute_time: float) -> float:
        """Absolute timstamp to elapsed time

        Args:
            absolute_time (float): Absolute ROS timestamp

        Returns:
            float: time since the start of the ROSbag
        """
        return (absolute_time - self._bag_start) / 1e9

    def split_rosbag(
        self,
        timestamps: Sequence[float] | None = None,
        outbag_path: Path | str = None,
        force_out: bool = False,
    ):
        """Clip rosbag between two elapsed times, given relative to the beginning of the rosbag

        Args:
            timestamps: Timestamps indicating where to split the bagfiles,
            outbag_path (Path | str): Path of output bag.
            force_squash (bool); Force output bag overwriting, if outbag already exists. Defaults to False.
        """
        if timestamps is None:
            timestamps = []
        split_tstamps = [t for t in timestamps]
        self._check_cutoff_limits(split_tstamps)
        split_tstamps.insert(0, 0)
        split_tstamps.append(self.atoe(self._bag_end))
        split_tstamps.sort()

        # Reader / Writer classes
        # Should be the same type of rosbag for both
        Reader = self.get_reader_class(self._inbag)
        Writer = self.get_writer_class(outbag_path)
        if self._is_ros1_reader != self._is_ros1_writer:
            raise NotImplementedError(
                "Rosbag conversion (ROS 1->ROS 2 / ROS 2->ROS 1) is not supported. "
                "Use `rosbags` to convert your rosbag before using `rosbag-tools split`."
            )

        base_path = Path(outbag_path)

        with Reader(self._inbag) as reader:
            for idx in range(1, len(split_tstamps)):
                export_path = base_path.with_name(
                    f"{base_path.stem}_{idx:02d}{base_path.suffix}"
                )
                self._check_export_path(export_path, force_out)
                with Writer(export_path) as writer:
                    conn_map = self._set_writer_connections(writer, reader.connections)
                    # Start and end of split
                    a_tstamp = self.etoa(split_tstamps[idx - 1])
                    b_tstamp = self.etoa(split_tstamps[idx])
                    with tqdm(total=reader.message_count, desc=f"Split {idx}") as pbar:
                        for conn, timestamp, data in reader.messages():
                            # if conn.topic == "/events/write_split":
                            #     continue
                            if a_tstamp <= timestamp <= b_tstamp:
                                writer.write(conn_map[conn.id], timestamp, data)
                            elif timestamp > b_tstamp:
                                break
                            pbar.update(1)
        print(f"[split] Splitting done ! Exported in {outbag_path}_[1-{idx}]")
