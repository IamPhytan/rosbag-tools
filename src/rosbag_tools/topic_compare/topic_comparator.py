"""Comparator class to compare topic consistency between rosbags in a dataset"""

from __future__ import annotations

import json
import warnings
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING

# Condition based on optional plt dependency
try:
    mtp = None
    import matplotlib as mtp
    import matplotlib.pyplot as plt
except ImportError:
    pass

import yaml
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag2 import Reader as Reader2
from tqdm import tqdm

if TYPE_CHECKING:
    from typing import List, Optional


class BagTopicComparator:
    """Rosbag Comparator : Assess the topic consistency of a rosbag dataset.
    Determines which topics are missing for each rosbag, by comparing with others"""

    def __init__(self, path: Path | str) -> None:
        """Instantiate BagTopicComparator

        Args:
            path: Path to a dataset directory that contains rosbag files
        """
        self._folder = Path(path)
        self.topics = {}

    @property
    def folder(self):
        """The folder property."""
        return self._folder

    @folder.setter
    def folder(self, value: Path | str):
        """Setter for `folder`"""
        if Path(value).is_dir():
            self._folder = value
        else:
            raise ValueError(f"{value} is not a valid directory")

    @classmethod
    def from_dict(cls, topics: dict) -> BagTopicComparator:
        """Instantiate RosbagComparator with a topics dictionary

        Args:
            topics (dict): Topics dictionary

        Returns:
            RosbagComparator: Instance of RosbagComparator
        """
        folder_name = Path.cwd()
        rbag_comp = cls(folder_name)
        rbag_comp.topics = topics
        return rbag_comp

    @classmethod
    def from_json(cls, json_path: Path | str) -> BagTopicComparator:
        """Instantiate RosbagComparator from a JSON file path

        Args:
            json_path (Path | str): Path to a JSON file

        Returns:
            RosbagComparator: Instance of RosbagComparator
        """
        with open(json_path, "r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> BagTopicComparator:
        """Instantiate RosbagComparator from a YAML file path

        Args:
            yaml_path: Path to a YAML file

        Returns:
            RosbagComparator: Instance of RosbagComparator
        """
        with open(yaml_path, "r", encoding="utf-8") as file:
            return cls.from_dict(yaml.safe_load(file))

    def extract_data(self) -> None:
        """Extract all the topics contained in the rosbags in the path self.folder"""
        paths_ros1 = self.folder.glob("*.bag")
        paths_ros2 = (p.parent for p in self.folder.glob("**/*.db3"))
        paths = list(paths_ros1) + list(paths_ros2)

        if len(paths) == 0:
            # Empty list of paths
            raise RuntimeWarning(f"Specified folder {self.folder} contains no bagfiles")

        if self.topics:
            # Topics have already been extracted
            warnings.warn(
                "Topics are already exported, yet the topics dict will be recreated.",
                RuntimeWarning,
            )

        # Create a dictionary with the list of topics for each bag file
        # {file1: ["/topic1", ...], ...}
        topics = {}
        print(
            f"Extracting topics from {len(paths)} rosbags in {self.folder.resolve().name}"
        )
        with tqdm(total=len(paths)) as pbar:
            for bagfile in paths:
                pbar.set_description(bagfile.stem)
                topics[bagfile.stem] = self.get_topics(bagfile)
                pbar.update(1)

        # Make a set with all the topics and get the missing topics
        # for each file
        common_set = set().union(*topics.values())
        differences = {stem: common_set - set(top) for stem, top in topics.items()}
        differences = {s: list(d) for s, d in differences.items()}

        self.topics = {
            "topics": topics,
            "difference": differences,
            "common": list(common_set),
        }

    @staticmethod
    def get_topics(filename: Path | str) -> List[str]:
        """Get a list of the topics in a rosbag file

        Args:
            filename: path of the rosbag file

        Returns:
            List[str]: list of the topics contained in the rosbag file
        """
        ros1 = filename.suffix == ".bag"
        Reader = Reader1 if ros1 else Reader2
        with Reader(filename) as bag:
            return list(bag.topics.keys())

    def _check_data_extraction(self, caller_name: str):
        """Assert that extract_data() was called"""
        if not self.topics:
            raise RuntimeError(
                "Topics are not extracted. "
                f"Call 'extract_data()' before calling '{caller_name}'"
            )

    def export_metadata(self, path: Path | str = None) -> None:
        """Export topics dictionary to a metadata file

        Args:
            path: path of the metadata file. Defaults to None.
            If None, the topics will be saved in topics_<foldername>.json.
        """
        self._check_data_extraction(self.export_metadata.__name__)

        # Default value
        path = f"topics_{self.folder.resolve().name}.json" if path is None else path

        # Infer from path extension
        ext = Path(path).suffix[1:].lower()
        if ext not in ("json", "yaml", "yml"):
            raise NotImplementedError(
                f"Metadata format {ext} is not supported. Try using json or yaml"
            )

        with open(path, "w", encoding="utf-8") as file:
            if ext == "json":
                json.dump(self.topics, file)
            elif ext in ("yaml", "yml"):
                yaml.dump(self.topics, file)

    def to_yaml_str(self) -> str:
        """Exports a yaml-serialized string from the topics dictionary

        Returns:
            str: YAML-serialized string with topics summary
        """
        return yaml.dump(self.topics)

    def plot(self, img_path: Optional[Path | str] = None) -> None:
        """Show the missing topics between the rosbags in each bag using a matplotlib scatterplot

        Args:
            img_path: Figure export path. Defaults to None. If None, the figure will be only displayed
        """

        if not mtp:
            raise ImportError(
                "matplotlib is not included in the installed version of rosbag-tools. Install 'rosbag-tools[plot]'"
            )

        self._check_data_extraction(self.plot.__name__)

        # Get the difference dictionary
        diff = self.topics["difference"]

        # diff : {filename: [topics], filename: [topics], filename:[topics]}
        if all(len(d) == 0 for d in diff.values()):
            raise ValueError(
                "Dataset has no differences : all rosbags have the same topics. "
                "Cannot plot a summary of the topic consistency"
            )

        # Create a set of all topics inside difference values
        diff_set = set(chain.from_iterable(diff.values()))

        # Topics list and sorted topics list
        tops_list = list(diff_set)
        tops_sort = sorted(tops_list)

        # Instantiate figure
        fig, ax = plt.subplots(figsize=(10, 7.5), num="Missing topics comparison")

        # Function to create sorted axes labels
        def axsetter(xunits, yunits, ax=None, sort=True, reversed_y=True):
            ax = ax or plt.gca()
            if sort:
                xunits = sorted(xunits)
                yunits = sorted(yunits, reverse=reversed_y)
            units = plt.plot(
                xunits, [yunits[0]] * len(xunits), [xunits[0]] * len(yunits), yunits
            )
            for unit in units:
                unit.remove()

        # Sort axes labels
        axsetter(list(diff.keys()), tops_list, ax=ax)

        # Sorted diff dict
        diff_sort = {k: sorted(v) for k, v in sorted(diff.items())}

        # Colors normalisation
        cmap = plt.cm.turbo
        norm = mtp.colors.Normalize(vmin=0, vmax=len(tops_sort) - 1)
        colors = {k: norm(i) for i, k in enumerate(tops_sort)}

        for name, tops in diff_sort.items():
            cols = [cmap(colors[top]) for top in tops]
            ax.scatter([name] * len(tops), tops, c=cols)

        # Rotate x axis labels by 45 degrees
        ax.set_xticklabels(sorted(list(diff.keys())), rotation=45, ha="right")

        # Figure parameters
        fig.suptitle(f"Missing topics in the rosbags of '{self.folder.resolve().name}'")
        plt.tight_layout()

        if img_path:
            # Save figure to file
            fig.savefig(img_path or f"missing_topics_{self.folder.resolve().name}.png")
        else:
            # Show figure
            plt.show()
