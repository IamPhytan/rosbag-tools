# rosbag-tools

> A ROS-agnostic toolbox for common rosbag operations

This package bundles different tools that can be applied on ROS 1 or ROS 2 rosbags with no dependency on the ROS software stack.

## Installation

`rosbag-tools` can be installed from PyPi :

```sh
pip install rosbag-tools
```

Some tools, like [`topic-compare`](src/rosbag_tools/topic_compare), have a graphing feature that requires `matplotlib`. Install `rosbag-tools[plot]` to install graph dependencies.

```sh
pip install rosbag-tools[plot]
```

`rosbag-tools` being a CLI application, it can be quickly installed with [pipx](https://github.com/pypa/pipx):

```sh
pipx install rosbag-tools
pipx install rosbag-tools[plot] # with plot
```

## Tools

* [`clip`](src/rosbag_tools/clip)
* [`split`](src/rosbag_tools/split)
* [`compute-duration`](src/rosbag_tools/compute_duration)
* [`export-odometry`](src/rosbag_tools/export_odometry)
* [`topic-compare`](src/rosbag_tools/topic_compare)
* [`topic-remove`](src/rosbag_tools/topic_remove)

## Usage

Each tool in `rosbag-tools` can be used both as a command line application and in Python code.

### Command line

A basic use of `rosbag-tools` is to simply call it from the command line.

```console
rosbag-tools `command` <options>
```

## Contributing

Pull requests and issues are welcome ! Don't hesitate to contribute !

(Recommended) [flit](https://flit.pypa.io) is used to package this module. Development packages can be installed using `flit` :

```console
python -m venv venv
source venv/bin/activate
pip install flit
flit install
```

(Alternative) Development requirements can be installed using pip :

```console
python -m venv venv
source venv/bin/activate
pip install -r requirements/requirements-dev.txt
```

## Acknowledgements

This package relies strongly on [`rosbags`](https://ternaris.gitlab.io/rosbags) for working with rosbags. Hats off to the team at [Ternaris](https://ternaris.com) for developing and maintaining it.

## License

This project is licensed under a [GNU GPLv3](LICENSE) license.
