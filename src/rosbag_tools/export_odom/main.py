from pathlib import Path

import click

from rosbag_tools.export_odom.odometry_exporter import OdometryExporter
from rosbag_tools.utils import custom_message_path, slugify_topic


@click.command(
    "export-odometry",
    short_help="export odometry topics from a rosbag to TUM file format",
)
@click.argument(
    "inbag",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "-t",
    "--odom-topic",
    "odom_topic",
    required=True,
    help="Odometry topic to export.",
    type=click.STRING,
)
@click.option(
    "--format",
    "--traj-form",
    "--trajectory-format",
    "odom_format",
    help="Trajectory format, as listed in https://github.com/MichaelGrupp/evo/wiki/Formats. Defaults to 'tum'.",
    type=click.STRING,
    default="tum",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    "out_path",
    help="Exported odometry file. Defaults to INBAG_topic.txt.",
)
@click.option(
    "-f",
    "--force-overwriting",
    "force",
    help="Force output file overwriting",
    is_flag=True,
)
@custom_message_path
def cli(inbag, odom_topic, out_path, odom_format, force: bool):
    """Export odometry topic from INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS 1 or in ROS 2
    """

    # Default path:
    # /path/to/my/rosbag => /path/to/my/rosbag_topic.txt
    # /path/to/my/rosbag.bag => /path/to/my/rosbag_topic.txt

    inpath = Path(inbag)
    odom_exp = OdometryExporter(inbag)
    odom_exp.export_odometry(
        odom_topic,
        export_format=odom_format,
        export_path=out_path,
        force_output_overwrite=force,
    )
