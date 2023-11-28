import click

from rosbag_tools import (
    __version__,
    clip,
    compute_duration,
    export_odometry,
    split,
    topic_compare,
    topic_remove,
)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli_main():
    """A ROS-agnostic toolbox for common rosbag operations"""
    pass


cli_main.add_command(clip)
cli_main.add_command(split)
cli_main.add_command(compute_duration)
cli_main.add_command(export_odometry)
cli_main.add_command(topic_compare)
cli_main.add_command(topic_remove)


if __name__ == "__main__":
    cli_main()
