from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, cast

from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag1 import Writer as Writer1
from rosbags.rosbag2 import Reader as Reader2
from rosbags.rosbag2 import Writer as Writer2

if TYPE_CHECKING:
    from typing import Sequence, Tuple, Type


class ROSBagTool:
    """ROSBagTool - Base class for a tool that acts on a single rosbag"""

    def __init__(self, path: Path | str) -> None:
        """Create a BagTopicRemover instance

        Args:
            path: Path to the input rosbag
        """
        self._tool_name: str = None
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
        is_ros1 = path.is_file() and path.suffix == ".bag"
        is_ros2 = path.is_dir() and len(tuple(path.glob("*.db3"))) > 0
        if is_ros1:
            path.unlink()
        elif is_ros2:
            shutil.rmtree(path)
        else:
            raise ValueError(f"Path {path} is not a valid rosbag")

    def _check_export_path(self, export_path: Path, force_out: bool) -> None:
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
        if export_path.exists() and force_out:
            self._delete_rosbag(export_path)


class DatasetTool:
    pass
