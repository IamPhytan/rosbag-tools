# `export-odometry`

> export odometry topics from a rosbag to TUM file format

## Use case

Say you have too much topics in a rosbag (ROS 1 or ROS 2) and that you want to keep a copy of this rosbag without data from a specific sensor. `rosbag-tools export-odometry` provides a fast way to :

* Export odometry topics in the [TUM trajectory format](https://vision.in.tum.de/data/datasets/rgbd-dataset/file_formats)
* Preserve your original rosbag

## Usage

`export-odometry` can be used both as a command line application and in Python code.

### Command line

A basic use of `export-odometry` is to simply call it from the command line.

```console
rosbag-tools export-odometry /path/to/rosbag -t /odometry/topic
rosbag-tools export-odometry /path/to/rosbag -t /odom/topic --format tum -o output.txt
```

Here are all the CLI options of `rosbag-tools export-odometry`:

```console
$ rosbag-tools export-odometry -h
Usage: rosbag-tools export-odometry [OPTIONS] INBAG

  Export odometry topic from INBAG

  INBAG is the path to a rosbag file
  Can be a bag in ROS 1 or in ROS 2

Options:
  -t, --odom-topic TEXT           Odometry topic to export.  [required]
  --format, --traj-form, --trajectory-format TEXT
                                  Trajectory format, as listed in https://gith
                                  ub.com/MichaelGrupp/evo/wiki/Formats.
                                  Defaults to 'tum'.  [default: tum]
  -o, --output TEXT               Exported odometry file. Defaults to
                                  INBAG_topic.txt.
  -f, --force-overwriting         Force output file overwriting
  --msg, --msg-path PATH          Custom messages path. Can be a path to a ROS
                                  workspace.
  -h, --help                      Show this message and exit.
```

### Python Code API

You can also call `rosbag-tools export-odometry` directly into your Python code :

```py
from rosbag_tools.export_odom import OdometryExporter

data_path = "path/to/a/rosbag.bag"  # ROS 1
data_path = "path/to/a/rosbag"  # ROS 2
odom_exporter = OdometryExporter(data_path)

# Change the input bag
odom_exporter.inbag = "path/to/another/rosbag"

# Export /odom messages in a TUM file
odom_exporter.export_odometry("/odom", export_format="tum", export_path="/path/to/tum/file.txt")

# Export /imu/odom messages in default path
odom_exporter.inbag = "/path/to/file.bag"
odom_exporter.export_odometry("/odom")  # Exports to /path/to/file_imu_odom.txt
```
