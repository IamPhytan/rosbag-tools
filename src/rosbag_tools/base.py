from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.rosbag2 import Writer as Writer2

if TYPE_CHECKING:
    from typing import Tuple, Type


class ROSBagTool:
    """ROSBagTool - Base class for a tool that acts on a single rosbag"""

    def __init__(self, path: Path | str, name: str) -> None:
        """Create a BagTopicRemover instance

        Args:
            path: Path to the input rosbag
            name: Tool name
        """
        self._tool_name: str = name
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

    def _delete_rosbag(self, path: Path | str) -> None:
        """Function to delete a rosbag at path `path`, to use with caution

        Args:
            path: Path to rosbag to delete.
        """
        is_ros1 = self.is_ros1bag(path)
        is_ros2 = self.is_ros2bag(path)
        if is_ros1:
            path.unlink()
        elif is_ros2:
            shutil.rmtree(path)
        else:
            raise ValueError(f"Path {path} is not a valid rosbag")

    def _delete_file(self, path: Path | str) -> None:
        """Function to delete a file at path `path`, to use with caution

        Args:
            path: File path to delete.
        """
        if path.exists() and path.is_file():
            path.unlink()
        elif path.exists() and path.is_dir():
            shutil.rmtree(path)
        else:
            raise ValueError(f"Path {path} is not a valid path")

    @staticmethod
    def is_ros1bag(path: Path) -> bool:
        """Is `path` leading to a ROSBag as defined in ROS ?

        Args:
            path (Path): Path to check

        Returns:
            bool: If True, `path` is a ROSBag as defined in ROS 1 (.bag file).
        """
        return path.is_file() and path.suffix == ".bag"

    @staticmethod
    def is_ros2bag(path: Path) -> bool:
        """Is `path` leading to a ROS2Bag, as defined in ROS 2 distros prior to Iron ?
        This function checks that `path` is a ROSBag that complies to the sqlite3 storage protocol.

        Args:
            path (Path): Path to check

        Returns:
            bool: If True, `path` is a ROSBag as defined in first ROS 2 distros (folder with .db3 files).
        """
        return path.is_dir() and len(tuple(path.glob("*.db3"))) > 0

    @staticmethod
    def is_mcap(path: Path) -> bool:
        """Is `path` leading to a ROSBag as defined in ROS 2 distros after humble ?

        Args:
            path (Path): Path to check

        Returns:
            bool: If True, `path` is a ROSBag as defined in recent ROS 2 distros (.mcap file).
        """
        return path.is_file() and path.suffix == ".mcap"

    def _check_export_path(
        self,
        export_path: Path,
        force_out: bool | None = False,
    ):
        """Check that export path doesn't exist yet. If needed, deletes file at path `export_path`

        Args:
            export_path (Path): Path for export file
            force_output_overwrite (bool): Flag to force output overwriting if path already exists. Default to False.

        Raises:
            FileExistsError: Export path is the same as input path
            FileExistsError: Export path already exists and output overwriting flag was not set to True
        """
        if export_path == self._inbag:
            raise FileExistsError(
                f"Cannot use same file as input and output [{export_path}]"
            )
        if export_path.exists() and not force_out:
            raise FileExistsError(
                f"Path {export_path.name} already exists. "
                f"Use 'force_out=True' or 'rosbag-tools {self._tool_name} -f' to "
                f"export to {export_path.name} even if output bag already exists."
            )
        is_deletable: bool = export_path.exists() and force_out
        if is_deletable:
            if self.is_ros1bag(export_path) or self.is_ros2bag(export_path):
                self._delete_rosbag(export_path)
            else:
                self._delete_file(export_path)


class DatasetTool:
    pass
