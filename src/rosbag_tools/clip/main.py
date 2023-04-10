from pathlib import Path
import click
from .clipper import BagClipper


@click.command(
    "clip",
    short_help="split or clip out a section of a long rosbag",
)
@click.argument(
    "inbag",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "-o",
    "--output",
    "--outbag",
    "outbag",
    help="Clipped bag. Defaults to INBAG_clip",
)
@click.option(
    "-s",
    "--start",
    "start_time",
    default=None,
    type=click.FLOAT,
    help="Start of the clip, in elapsed seconds since the start of the rosbag",
)
@click.option(
    "-e",
    "--end",
    "end_time",
    default=None,
    type=click.FLOAT,
    help="End of the clip, in elapsed seconds since the start of the rosbag",
)
@click.option(
    "-f",
    "--force-overwriting",
    "force",
    help="Force output file overwriting",
    is_flag=True,
)
def cli(inbag, outbag, force, start_time=None, end_time=None):
    """Clip out a portion of INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS 1 or in ROS 2
    """
    print(inbag, outbag, start_time, end_time)
    clipper = BagClipper(inbag)
