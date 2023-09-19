from pathlib import Path

import click

from rosbag_tools.clip.clipper import BagClipper
from rosbag_tools.utils import custom_message_path


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
@custom_message_path
def cli(inbag, outbag, force, start_time=None, end_time=None):
    """Clip out a portion of INBAG

    INBAG is the path to a rosbag file
    Can be a bag in ROS 1 or in ROS 2
    """
    clipper = BagClipper(inbag)
    if outbag:
        clipper.clip_rosbag(
            start=start_time,
            end=end_time,
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
        clipper.clip_rosbag(
            start=start_time, end=end_time, outbag_path=outpath_default, force_out=force
        )
