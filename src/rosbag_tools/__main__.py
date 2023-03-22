import click
from . import topic_compare

from . import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli_main():
    """A ROS-agnostic toolbox for common rosbag operations"""
    pass


cli_main.add_command(topic_compare)


if __name__ == "__main__":
    cli_main()
