from pathlib import Path

import click

from rosbag_tools.topic_remove.topic_remover import BagTopicRemover
from rosbag_tools.utils import custom_message_path


@click.command(
    "topic-remove",
    short_help="filter out topics from a rosbag",
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
    help="Filtered bag. Defaults to INBAG_filt",
)
@click.option(
    "-t",
    "--topics",
    type=click.STRING,
    multiple=True,
)
@click.option(
    "-f",
    "--force-overwriting",
    "force",
    help="Force output file overwriting",
    is_flag=True,
)
@custom_message_path
def cli(inbag, outbag, topics, force):
    """Remove topics from INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS 1 or in ROS 2
    """
    inpath = Path(inbag)

    rosbag_rem = BagTopicRemover(inbag)
    rosbag_rem.remove(topics)
    if outbag:
        outpath = Path(outbag)
        rosbag_rem.export(outpath, force_output_overwrite=force)
    else:
        # Default path:
        # /path/to/my/rosbag => /path/to/my/rosbag_filt
        # /path/to/my/rosbag.bag => /path/to/my/rosbag_filt.bag
        inpath = Path(inpath)
        def_outfname = f"{inpath.stem}_filt{inpath.suffix}"
        default_outpath = inpath.parent / def_outfname
        rosbag_rem.export(default_outpath, force_output_overwrite=force)
