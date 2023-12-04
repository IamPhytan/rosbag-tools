"""odometry exporter class to export odometry topics from a rosbag"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from rosbags.highlevel import AnyReader
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
    ODOM_MSG_TYPES = ["nav_msgs/msg/Odometry"]
    TUM_FIRST_ROW = "# timestamp tx ty tz qx qy qz qw"

    def __init__(self, path: Path | str) -> None:
        super().__init__(path, "export-odometry")

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

        # Reader
        with AnyReader([self.inbag]) as reader:
            # Check that odom_topic is a odom topic
            connections = [x for x in reader.connections if x.topic == odom_topic]
            msgtypes = [conn.msgtype for conn in connections]
            if not all([mtype in self.ODOM_MSG_TYPES for mtype in msgtypes]):
                raise ValueError(
                    f"Topic {odom_topic} is not an odometry topic. s"
                    f"Choose a topic that has one of the following msg types : {', '.join(self.ODOM_MSG_TYPES)}."
                )

            msgcount = [conn.msgcount for conn in connections]
            odom_data = []
            with tqdm(total=sum(msgcount)) as pbar:
                for conn, timestamp, data in reader.messages(connections=connections):
                    msg = reader.deserialize(data, conn.msgtype)

                    tstamp = msg.header.stamp
                    tstamp_s = tstamp.nanosec / 1e9 + tstamp.sec
                    pose = msg.pose.pose
                    position = pose.position
                    orient = pose.orientation
                    time_dat = {
                        "timestamp": tstamp_s,
                        "tx": position.x,
                        "ty": position.y,
                        "tz": position.z,
                        "qx": orient.x,
                        "qy": orient.y,
                        "qz": orient.z,
                        "qw": orient.w,
                    }
                    odom_data.append(time_dat)

                    # Update progress bar
                    pbar.update(1)

        # Export to TUM
        df = pd.DataFrame(odom_data)
        df = df[self.TUM_FIRST_ROW[2:].split()]
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(f"{self.TUM_FIRST_ROW}\n")
        df.to_csv(outpath, index=False, header=False, mode="a", sep=" ")

        print(f"[export-odometry] Done ! Exported in {outpath}")
