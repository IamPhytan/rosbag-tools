"""ROSBag clipper class"""

from __future__ import annotations

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
    from typing import Optional, Type


class UnknownStartTimeError(ValueError):
    """Exception for start times"""

    pass


class UnknownEndTimeError(ValueError):
    """Exception for end times"""

    pass


class UnorderedTimeError(ValueError):
    """Exception for time order (Start < End)"""

    pass


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
        self.in_path: Path = Path(path)

    @property
    def in_path(self):
        """Path to input rosbag"""
        return self._in_path

    @in_path.setter
    def in_path(self, value: Path | str):
        # Check that path exists
        if not Path(value).exists():
            raise FileNotFoundError(
                f"File {value} is not an existing file. Please provide a path that exists in your file system"
            )
        self._in_path = Path(value)
        Reader = self.get_reader_class(self._in_path)
        with Reader(self._in_path) as bag:
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

    def delete_rosbag(self, path: Path | str):
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
        self, start: Optional[float] = None, end: Optional[float] = None
    ):
        """Check that clip limits are in the range of the bag

        Args:
            start (float, optional): Starting time. Defaults to None.
            end (float, optional): Ending time. Defaults to None.

        Raises:
            UnknownStartTimeError: _raised if `start` is not in the rosbag_
            UnknownEndTimeError: _raised if `end` is not in the rosbag_
            UnorderedTimeError: _raised f `end` < `start`_
        """
        slimit = start is not None
        elimit = end is not None
        start_ns = start * 10**9 if slimit else start
        end_ns = end * 10**9 if elimit else end
        if slimit and start_ns < 0 and start_ns > self._bag_duration:
            raise UnknownStartTimeError(
                f"Start time ({start} s) is not in the bag. "
                f"Start time should be defined between 0 and {self._bag_duration} s."
            )
        if elimit and end_ns < 0 and end_ns > self._bag_duration:
            raise UnknownEndTimeError(
                f"End time ({end} s) is not in the bag. "
                f"End time should be defined between 0 and {self._bag_duration} s."
            )
        if slimit and elimit and end < start:
            raise UnorderedTimeError(
                f"Start time (s: {start}) should come " f"before ending time (e: {end})."
            )

    def clip_rosbag(
        self,
        start: Optional[float] = None,
        end: Optional[float] = None,
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
            start_ns = start * 10**9
            s_cliptstamp = self._bag_start + start_ns

        if end is None:
            e_cliptstamp = self._bag_end
        else:
            end_ns = end * 10**9
            e_cliptstamp = self._bag_start + end_ns

        # Check Export Path
        export_path = Path(outbag_path)
        if export_path == self._in_path:
            raise FileExistsError(
                f"Cannot use same file as input and output [{export_path}]"
            )
        if export_path.exists() and not force_out:
            raise FileExistsError(
                f"Path {outbag_path} already exists. "
                "Use 'force_out=True' or 'rosbag-tools clip -f' to "
                f"export to {outbag_path} even if output bag already exists."
            )
        if export_path.exists() and force_out:
            warnings.warn(
                f"Output path {export_path} already exists, output overwriting flag has been set, deleting old output file"
            )
            self.delete_rosbag(export_path)

        # Reader / Writer classes
        Reader = self.get_reader_class(self._in_path)
        Writer = self.get_writer_class(outbag_path)
        if self._is_ros1_reader != self._is_ros1_writer:
            raise NotImplementedError(
                "Rosbag conversion (ROS 1->ROS 2 / ROS 2->ROS 1) is not supported. "
                "Use `rosbags` to convert your rosbag before using `rosbag-tools clip`."
            )
        with Reader(self._in_path) as reader, Writer(export_path) as writer:
            conn_map = {}
            ConnectionExt = (
                ConnectionExtRosbag1 if self._is_ros1_writer else ConnectionExtRosbag2
            )
            for conn in reader.connections:
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
                        ext.serialization_format,
                        ext.offered_qos_profiles,
                    )

            with tqdm(total=reader.message_count) as pbar:
                for conn, timestamp, data in reader.messages():
                    if s_cliptstamp <= timestamp <= e_cliptstamp:
                        writer.write(conn_map[conn.id], timestamp, data)
                    pbar.update(1)

        print(f"[clip] Clipping done ! Exported in {outbag_path}")
