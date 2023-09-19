`split`

> split a long rosbag into several section

## Use case

Say you have a long rosbag that contains several runs of your robot. You may want to separate the rosbag into several files and process each of them individually.

## Usage

`split` can be used both as a command line application and in Python code.

### Command line

A basic use of `split` is to simply call it from the command line.

```console
rosbag-tools split path/to/rosbag -o /path/to/clip -t "[timestamp1, timestamp2]"
```

Here are all the CLI options of `rosbag-tools split`:

```console
$ rosbag-tools split -h
Usage: rosbag-tools split [OPTIONS] INBAG

  Split out an INBAG

  INBAG is the path to a rosbag file Can be a bag in ROS 1 or in ROS 2

Options:
  -o, --output, --outbag TEXT  Basename of the split bag files. Defaults to
                               INBAG_COUNT
  -t, --timestamps TEXT        List of timestamps in the format '[S., S.]', in
                               elapsed seconds since the start of the rosbag
  --timestamps-file PATH       Path to a file containing timestamps
                               representing elapsed seconds since the start of
                               the rosbag. Each timestamp is on an individual
                               line.
  -f, --force-overwriting      Force output file overwriting
  --msg, --msg-path PATH       Custom messages path. Can be a path to a ROS
                               workspace.
  -h, --help                   Show this message and exit.
```

### Python Code API

You can also call `rosbag-tools split` directly into your Python code :

```py
from rosbag_tools.split import BagSplitter

data_path = "path/to/a/rosbag.bag"  # ROS 1
data_path = "path/to/a/rosbag"  # ROS 2
splitter = BagSplitter(data_path)

# Change the input bag
splitter.inbag = "path/to/another/rosbag"

# Split the bagfile at 42 seconds
splitter.split_rosbag(timestamps=[42.0], outbag_path="path/to/clip")

# Save 3 bagfiles
splitter.split_rosbag(timestamps=[10.0, 42.0], outbag_path="/clip/out/first/25/seconds")
```
