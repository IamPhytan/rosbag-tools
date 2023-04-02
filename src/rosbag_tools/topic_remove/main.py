from pathlib import Path
import click
from .topic_remover import BagTopicRemover


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
def cli(inbag, outbag, topics, force):
    """Remove topics from INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS1 or in ROS2
    """
    inpath = Path(inbag)
    outpath = Path(outbag)

    rosbag_rem = BagTopicRemover(inbag)
    rosbag_rem.remove(topics)
    if outpath:
        rosbag_rem.export(outpath, force_output_overwrite=force)
    else:
        # Default path:
        # /path/to/my/rosbag => /path/to/my/rosbag_filt
        # /path/to/my/rosbag.bag => /path/to/my/rosbag_filt.bag
        inpath = Path(inpath)
        def_outfname = f"{inpath.stem}_filt{inpath.suffix}"
        default_outpath = inpath.parent / def_outfname
        rosbag_rem.export(default_outpath, force_output_overwrite=force)
