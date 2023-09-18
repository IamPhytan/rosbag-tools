from pathlib import Path
import click
from .splitter import BagSplitter


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
    help="Csv file containing timestamps representing elapsed seconds since the start of the rosbag. Each timestamp is on an individual line.",
)
@click.option(
    "-f",
    "--force-overwriting",
    "force",
    help="Force output file overwriting",
    is_flag=True,
)
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
        inpath = Path(inbag)
        outdir_default = inpath.parent / "rosbags-clips"
        outdir_default.mkdir(parents=True, exist_ok=True)
        n_clips = len(list(outdir_default.glob(f"{inpath.stem}*")))
        print(n_clips)
        out_fname = f"{inpath.stem}_clip_{n_clips:02d}{inpath.suffix}"
        outpath_default = outdir_default / out_fname
        splitter.split_rosbag(
            timestamps=timestamps, outbag_path=outpath_default, force_out=force
        )
