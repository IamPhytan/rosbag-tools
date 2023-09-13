# `topic-remove`

> filter out topics from a rosbag

## Use case

Say you have too much topics in a rosbag (ROS 1 or ROS 2) and that you want to keep a copy of this rosbag without data from a specific sensor. `rosbag-tools topic-remove` will :

* Filter out topics based on their name
* Filter out topics based on [glob](https://en.wikipedia.org/wiki/Glob_(programming))-like wildcard patterns
* Preserve your original rosbag

## Usage

`topic-remove` can be used both as a command line application and in Python code.

### Command line

A basic use of `topic-remove` is to simply call it from the command line.

```console
rosbag-tools topic-remove /path/to/rosbag -t /topic/to_delete -t /another/topic/to/remove
rosbag-tools topic-remove /path/to/rosbag -t *sensor*
```

Here are all the CLI options of `rosbag-tools topic-remove`:

```console
$ rosbag-tools topic-remove -h
Usage: rosbag-tools topic-remove [OPTIONS] INBAG

  Remove topics from INBAG

  INBAG is the path to a rosbag file
  Can be a bag in ROS 1 or in ROS 2

Options:
  -o, --output, --outbag TEXT  Filtered bag. Defaults to INBAG_filt
  -t, --topics TEXT
  -f, --force-overwriting      Force output file overwriting
  -h, --help                   Show this message and exit.
```

### Python Code API

You can also call `rosbag-tools topic-remove` directly into your Python code :

```py
from rosbag_tools.topic_remove import BagTopicRemover

data_path = "path/to/a/rosbag.bag"  # ROS 1
data_path = "path/to/a/rosbag"  # ROS 2
topic_remover = BagTopicRemover(data_path)

# Change the input bag
topic_remover.inbag = "path/to/another/rosbag"

# Remove /cmd_vel
topic_remover.remove("/cmd_vel")

# Remove /cmd_vel
topic_remover.remove("/cmd_vel")

# Remove all camera info topics
topic_remover.remove("/*/camera_info")

# Remove all topics from the IMU and from the GPS
topic_remover.remove(("/imu/*", "/gps/*"))

# Export a rosbag with all topics filtered
topic_remover.export("path/to/save/this/filtered/rosbag.bag")  # ROS 1
topic_remover.export("path/to/save/that/filtered/rosbag")  # ROS 2
```
