Changelog
=========

0.0.7
-----------------------------

- Add `rosbag-tools topic-compare` example to the documentation.
- Extend the custom msg path decorator for multiple custom message paths.

0.0.6
-----------------------------

- Add citation file to the repository.
- Added `rosbag-tools split`. Thanks to @boxanm for the contribution !
- Unify exceptions in a common file for all tools.
- Update tools for [rosbags v0.9.16](https://gitlab.com/ternaris/rosbags/-/tags/v0.9.16)
- Add a command decorator to specify custom msg paths for any tool. Can be used when a specific message type is unknown to rosbags.

0.0.5
-----------------------------

- Add `rosbag-tools compute-duration`.

0.0.4
-----------------------------

- Fix bug in the default behaviour of `topic-remove`. Thanks to @jmfortin for reporting the error.
- Add a [release procedure](RELEASE.md)

0.0.3
-----------------------------

- Fix references to [ROS 2](https://twitter.com/OpenRoboticsOrg/status/1631760751026376704)
- Add `clip`
- Fix typos in docstrings

0.0.2
-----------------------------

- Add `topic-remove`

0.0.1
-----------------------------

- Add `topic-compare`