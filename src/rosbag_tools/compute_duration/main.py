from datetime import timedelta
from pathlib import Path

import click

from rosbag_tools.compute_duration.duration_calculator import DurationCalculator
from rosbag_tools.utils import custom_message_path


@click.command(
    "compute-duration",
    short_help="compute the duration of every rosbag in a folder",
)
@click.argument(
    "bagfolder",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "-m",
    "--metadata",
    type=click.Path(),
    help="Metadata summary output path",
)
@click.option(
    "--total",
    help="Total duration of all rosbags",
    is_flag=True,
)
@custom_message_path
def cli(bagfolder, metadata, total, *args):
    """Retrieve the duration of every rosbag in BAGFOLDER

    BAGFOLDER is the path to a dataset directory
    """
    data_path = Path(bagfolder)
    is_total = total
    rosbag_duracomp = DurationCalculator(data_path)
    rosbag_duracomp.extract_data()
    if metadata is not None:
        rosbag_duracomp.export_metadata(metadata)
    if is_total:
        total = timedelta(seconds=rosbag_duracomp.total)
        print(f"{str(total):0>8}")
    if not metadata and not is_total:
        # Default behavior, without any arguments
        durations_desc = rosbag_duracomp.to_yaml_str()
        print(durations_desc)
