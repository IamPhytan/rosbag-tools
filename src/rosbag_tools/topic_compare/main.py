from pathlib import Path

import click

from rosbag_tools.topic_compare.topic_comparator import BagTopicComparator
from rosbag_tools.utils import custom_message_path


@click.command(
    "topic-compare",
    short_help="check topic consistency between rosbags in a directory",
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
    "-p",
    "--plot",
    help="Plotting mode : display a summary plot",
    is_flag=True,
)
@click.option(
    "--fig",
    "--summary-figure-path",
    help="Topic consistency figure export path",
)
@custom_message_path
def cli(bagfolder, metadata, plot, fig, *args):
    """Compare rosbag files that are stored in BAGFOLDER

    BAGFOLDER is the path to a dataset directory
    """
    data_path = Path(bagfolder)
    is_plot = plot
    rosbag_comp = BagTopicComparator(data_path)
    rosbag_comp.extract_data()
    if metadata is not None:
        rosbag_comp.export_metadata(metadata)
    if is_plot:
        if fig is not None:
            rosbag_comp.plot(fig)
        else:
            rosbag_comp.plot()
    if not metadata and not is_plot:
        # Default behavior, without any arguments
        topics_desc = rosbag_comp.to_yaml_str()
        print(topics_desc)
