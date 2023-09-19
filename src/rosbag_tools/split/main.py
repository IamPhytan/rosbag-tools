from pathlib import Path

import click
import json

from rosbag_tools import exceptions
from rosbag_tools.split.splitter import BagSplitter
from rosbag_tools.utils import custom_message_path


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
    help="List of timestamps in the format '[S., S.]', in elapsed seconds since the start of the rosbag",
)
@click.option(
    "--timestamps-file",
    "timestamps_file",
    type=click.Path(exists=True),
    help="Path to a file containing timestamps representing elapsed seconds since the start of the rosbag. "
    "Each timestamp is on an individual line.",
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
    splitter = BagSplitter(inbag)
    if timestamps_file is not None:
        # Received path to timestamps file
        tstamp_path = Path(timestamps_file)
        tstamps_values = tstamp_path.read_text(encoding="utf-8").splitlines()
        if not tstamps_values:
            raise exceptions.FileContentError(
                f"Timestamps file '{tstamp_path.resolve()}' is empty"
            )
        isContentNumeric = all(t.replace(".", "").isdigit() for t in tstamps_values)
        if not isContentNumeric:
            raise exceptions.FileContentError(
                f"Timestamps file '{tstamp_path.resolve()}' contains "
                "values that cannot be interpreted as timestamps"
            )
    elif timestamps is not None:
        # Received list of timestamps
        tstamps_values = json.loads(timestamps)
    else:
        tstamps_values = []
    tstamps = [float(v) for v in tstamps_values]
    if outbag:
        splitter.split_rosbag(
            timestamps=tstamps,
            outbag_path=outbag,
            force_out=force,
        )
    else:
        inpath = Path(inbag)
        outpath = inpath.with_name(inpath.stem + "_split" + inpath.suffix)
        splitter.split_rosbag(
            timestamps=tstamps,
            outbag_path=outpath,
            force_out=force,
        )
