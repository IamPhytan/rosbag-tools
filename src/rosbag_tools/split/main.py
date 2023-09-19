from pathlib import Path
import click
from .splitter import BagSplitter
from ..utils import custom_message_path


@click.command(
    "split",
    short_help="split a rosbag into two or multiple files",
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
    help="Basename of the split bag files. Defaults to INBAG_COUNT",
)
@click.option(
    "-t",
    "--timestamps",
    default=None,
    type=str,
    help="List of timestamps in the format [S., S.], in elapsed seconds since the start of the rosbag",
)
@click.option(
    "--timestamps_file",
    type=str,
    help="Text file containing timestamps representing elapsed seconds since the start of the rosbag. Each timestamp "
         "is on an individual line.",
)
@click.option(
    "-f",
    "--force-overwriting",
    "force",
    help="Force output file overwriting",
    is_flag=True,
)
@custom_message_path
def cli(inbag, outbag, force, timestamps=None, timestamps_file=None):
    """Split out an INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS 1 or in ROS 2
    """
    # TODO: Add default behavior
    splitter = BagSplitter(inbag)
    if timestamps_file is not None:
        timestamps = []
        with open(timestamps_file) as file:
            for line in file.readlines():
                timestamps.append(line)
    elif timestamps is not None:
        timestamps = timestamps.replace("[", "")
        timestamps = timestamps.replace("]", "")
        timestamps = timestamps.replace(" ", "")
        timestamps = timestamps.split(",")
    timestamps = [float(s) for s in timestamps]
    if outbag:
        splitter.split_rosbag(
            timestamps=timestamps,
            outbag_path=outbag,
            force_out=force,
        )
    else:
        path = Path(inbag)
        path = path.with_name(path.stem + "_split" + path.suffix)
        splitter.split_rosbag(timestamps=timestamps, outbag_path=path, force_out=force)
