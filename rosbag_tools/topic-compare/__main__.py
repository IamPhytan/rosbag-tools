"""Rosbag topic comparator

Compares topics consistency between rosbags in a dataset directory

Usage:
------

 $ rosbag-topic-compare [OPTIONS] BAGFOLDER

Compare topics in different rosbags inside BAGFOLDER
    and summarize the comparison in a JSON or YAML file:

 $ rosbag-topic-compare path/to/BAGFOLDER -o rostopics.json
 $ rosbag-topic-compare path/to/BAGFOLDER -o rostopics.yaml

Compare topics in rosbags inside BAGFOLDER, summarize in a JSON file
    and plot a figure to show missing topics in each rosbag:

 $ rosbag-topic-compare path/to/BAGFOLDER -p

Compare topics in rosbags inside BAGFOLDER,
    show a topic consistency summary
    and save it in `dataset_consistency.png`:

 $ rosbag-topic-compare path/to/BAGFOLDER -p --fig dataset_consistency.png

Available options are:

options:
  -h, --help            show this help message and exit
  -m METADATA, --metadata METADATA
                        Metadata summary output path
  -p, --plot            Plotting mode : display a summary plot
  --fig FIG, --summary-figure-path FIG
                        Path for saving a topic consistency figure

Version:
--------

- rosbag-topic-compare v0.0.3
"""

from rosbag_tools.main import cli

if __name__ == "__main__":
    cli()
