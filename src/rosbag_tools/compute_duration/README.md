# `compute-duration`

> compute the duration of every rosbag in a folder

## Use case

This tool can be used to retreive the duration of every rosbag in a dataset. It can be used to summarize the content of a dataset with rosbag files.
`rosbag-tools compute-duration` will :

* compute the duration of every rosbag in your dataset
* return the total record duration of the dataset

## Usage

`compute-duration` can be used both as a command line application and in Python code.

### Command line

A basic use of `compute-duration` is to simply call it with the path of the folder that contains rosbags. This will simply print out a YAML string with a summary of the durations.

```console
rosbag-tools compute-duration /path/to/folder/with/rosbags
```

You can also simply get the total duration of your dataset with the `--total` flag.

```console
rosbag-tools compute-duration /path/to/your/rosbag/dataset --total
```

Here are all the CLI options of `compute-duration`:

```console
$ rosbag-tools compute-duration -h
Usage: rosbag-tools compute-duration [OPTIONS] BAGFOLDER

  Retrieve the duration of every rosbag in BAGFOLDER

  BAGFOLDER is the path to a dataset directory

Options:
  -m, --metadata PATH  Metadata summary output path
  --total              Total duration of all rosbags
  -h, --help           Show this message and exit.

```

### Python Code API

You can also call `rosbag-tools compute-duration` directly into your Python code :

```py
from rosbag_tools.compute_duration import DurationCalculator

data_path = "/path/to/folder/with/rosbags"
duration_calculator = DurationCalculator(data_path)

# This step may take time as it open each rosbag separately
# Will show a progress bar
duration_calculator.extract_data()

# Export summary to a JSON file
duration_calculator.export_metadata()  # Defaults to durations_<foldername>.json
duration_calculator.export_metadata("durations.json")
duration_calculator.export_metadata("durations.yaml")

# Get the total duration of all rosbags
total_duration = duration_calculator.total

# Create a new comparator from exported metadata
duration_calculator = DurationCalculator.from_json("durations.json")
duration_calculator = DurationCalculator.from_yaml("durations.yaml")
```
