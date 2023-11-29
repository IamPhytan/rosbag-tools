"""odometry exporter class to export odometry topics from a rosbag"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, cast

from rosbags.interfaces import ConnectionExtRosbag1, ConnectionExtRosbag2
from tqdm import tqdm

from rosbag_tools.base import ROSBagTool
from rosbag_tools.exceptions import FileContentError
from rosbag_tools.utils import slugify_topic

if TYPE_CHECKING:
    from typing import Sequence, Tuple, Type


class OdometryExporter(ROSBagTool):
    """Topic Remover : Remove topics from a rosbag"""

    ALL_ODOM_FORMATS = ("tum", "bag", "euroc", "kitti", "bag2")
    ODOM_EXTS = {
        "tum": ".txt",
        "bag": ".bag",
        "euroc": ".csv",
        "kitti": ".txt",
        "bag2": "",
    }

    def __init__(self, path: Path | str) -> None:
        self._tool_name = "export-odometry"
        super().__init__(path)

    def export_odometry(
        self,
        odom_topic: str,
        export_format: str | None = "tum",
        export_path: Path | str | None = None,
        force_output_overwrite: bool = False,
    ) -> None:
        """Export odometry topic to 'out_path'

        Args:
            odom_topic (str): odometry topic to export.
            export_format (str): Odometry format. Defaults to "tum".
            export_path (Path | str) : Export path. Defaults to None. If None, the odometry will be exported in `{inbag}_{odom_topic}.{ext}`
            force_output_overwrite (bool): Force output overwriting if export_path already exists. Defaults to False.

        Raises:
            NotImplementedError: _description_
        """

        # Check odom_topic
        slug_odom_topic = slugify_topic(odom_topic)
        slug_topics = (slugify_topic(topic) for topic in self.topics)
        if slug_odom_topic not in slug_topics:
            raise FileContentError(f"Topic {odom_topic} not found in bag {self._inbag}")

        # Check odom format
        exp_form = export_format.lower()
        if exp_form not in self.ALL_ODOM_FORMATS:
            raise ValueError(f"Odom format {export_format} is unknown")
        if exp_form != "tum":
            # TODO: Implement other odom formats
            # Only tum is implemented as of now
            raise NotImplementedError("As of now, only the 'tum' format is supported.")

        # Check export_path
        export_ext = self.ODOM_EXTS[exp_form]
        if export_path is not None:
            # Export path was given as a method argument
            outpath = Path(export_path)
            if outpath.suffix != export_ext:
                raise ValueError(
                    f"File extension is not compatible with odom format '{exp_form}'. "
                    f"[Expected {export_ext}; got {outpath.suffix}]"
                )
        else:
            # Default filename : `{inbag}_{odom_topic}.{ext}`
            outfname = self.inbag.with_stem(
                f"{self.inbag.stem}_{slug_odom_topic}"
            ).with_suffix(export_ext)
            outfname = f"{self.inbag.stem}_{slug_odom_topic}{export_ext}"
            outpath = self.inbag.parent / outfname

        self._check_export_path(export_path=outpath, force_out=force_output_overwrite)

        # Reader / Writer classes
        Reader = self.get_reader_class(self.inbag)

        with Reader(self.inbag) as reader:
            # TODO: Check that odom_topic is a odom topic
            conn_map = {}


        args = {
            "odom_topic": odom_topic,
            "export_format": export_format,
            "export_path": export_path,
            "outpath": outpath,
            "force_output_overwrite": force_output_overwrite,
        }

        print(args)
        return args
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
