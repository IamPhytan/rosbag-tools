from pathlib import Path

import click

from .topic_comparator import BagTopicComparator


@click.command("topic-compare")
@click.argument(
    "bagfolder",
    type=click.Path(exists=True),
    help="Dataset directory path",
)
@click.argument(
    "-m",
    "--metadata",
    type=click.Path(),
    help="Metadata summary output path",
)
@click.argument(
    "-p",
    "--plot",
    help="Plotting mode : display a summary plot",
    is_flag=True,
)
@click.argument(
    "--fig",
    "--summary-figure-path",
    help="Path for saving a topic consistency figure",
)
def cli():
    """Main function"""
    args = parse_arguments()
    data_path = Path(args.bagfolder)
    is_plot = args.plot
    rosbag_comp = BagTopicComparator(data_path)
    rosbag_comp.extract_data()
    if args.metadata:
        rosbag_comp.export_metadata(args.metadata)
    if is_plot:
        if args.fig:
            rosbag_comp.plot(args.fig)
        else:
            rosbag_comp.plot()
    if not args.metadata and not is_plot:
        # Default behavior, without any arguments
        topics_desc = rosbag_comp.to_yaml_str()
        print(topics_desc)
