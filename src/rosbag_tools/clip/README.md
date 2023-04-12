`clip`

> split or clip out a section of a long rosbag

## Use case

Say you have a long rosbag that contains a whole run of your robot. You may want to only look at a certain event, be it a robot failure, or a highlight of the run. `rosbag-tools clip` will:

* extract data that were published between two times
* use elapsed time values (_between a minute and 90 seconds since the beginning_, _first 20 seconds of the run_) to specify the limits of the clip
* help you multiple clips from the same rosbag

## Usage

`clip` can be used both as a command line application and in Python code.

### Command line

A basic use of `clip` is to simply call it from the command line.

```console
rosbag-tools clip /path/to/rosbag -o /path/to/clip -s start -e end
```

Here are all the CLI options of `rosbag-tools clip`:

```console
$ rosbag-tools clip -h
Usage: rosbag-tools clip [OPTIONS] INBAG

  Clip out a portion of INBAG

  INBAG is the path to a rosbag file Can be a bag in ROS 1 or in ROS 2

Options:
  -o, --output, --outbag TEXT  Clipped bag. Defaults to INBAG_clip
  -s, --start FLOAT            Start of the clip, in elapsed seconds since the
                               start of the rosbag
  -e, --end FLOAT              End of the clip, in elapsed seconds since the
                               start of the rosbag
  -f, --force-overwriting      Force output file overwriting
  -h, --help                   Show this message and exit.
```

### Python Code API

You can also call `rosbag-tools topic-remove` directly into your Python code :

```py
from rosbag_tools.clip import BagClipper

data_path = "path/to/a/rosbag.bag"  # ROS 1
data_path = "path/to/a/rosbag"  # ROS 2
clipper = BagClipper(data_path)

# Change the input bag
clipper.inbag = "path/to/another/rosbag"

# Export a clip that starts at 4s and ends at 42s
clipper.clip_rosbag(start=4, end=42, outbag_path="path/to/clip")

# Save a clip between 25s and the end
clipper.clip_rosbag(start=25, outbag_path="/clip/out/first/25/seconds")

# Save a clip with the first 20 seconds
clipper.clip_rosbag(first=20, outbag_path="/first/20/seconds")
```
