"""Calculator class to compute the duration of all rosbags in a dataset"""

from __future__ import annotations

import json
import warnings
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from rosbags.rosbag1 import Reader as Reader1
from rosbags.rosbag2 import Reader as Reader2
from tqdm import tqdm

if TYPE_CHECKING:
    from typing import List, Optional


class DurationCalculator:
    """Duration Calculator : Compute the duration of every rosbag in a dataset."""

    def __init__(self, path: Path | str) -> None:
        """Instantiate DurationCalculator

        Args:
            path: Path to a dataset directory that contains rosbag files
        """
        self._folder = Path(path)
        self.TOTAL_KEY = "Total duration"
        self.durations = {}

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

    @property
    def total(self) -> float:
        """The total property."""
        durations = (dur for k, dur in self.durations.items() if k != self.TOTAL_KEY)
        return sum(durations)

    @classmethod
    def from_dict(cls, durations: dict) -> DurationCalculator:
        """Instantiate DurationCalculator with a duration dictionary

        Args:
            durations (dict): Duration dictionary

        Returns:
            DurationCalculator: Instance of DurationCalculator
        """
        folder_name = Path.cwd()
        rbag_comp = cls(folder_name)
        rbag_comp.durations = durations
        return rbag_comp

    @classmethod
    def from_json(cls, json_path: Path | str) -> DurationCalculator:
        """Instantiate DurationCalculator from a JSON file path

        Args:
            json_path (Path | str): Path to a JSON file

        Returns:
            DurationCalculator: Instance of DurationCalculator
        """
        with open(json_path, "r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> DurationCalculator:
        """Instantiate DurationCalculator from a YAML file path

        Args:
            yaml_path: Path to a YAML file

        Returns:
            DurationCalculator: Instance of DurationCalculator
        """
        with open(yaml_path, "r", encoding="utf-8") as file:
            return cls.from_dict(yaml.safe_load(file))

    def extract_data(self) -> None:
        """Extract the durations of all the rosbags in the path self.folder"""
        paths_ros1 = self.folder.glob("*.bag")
        paths_ros2 = (p.parent for p in self.folder.glob("**/*.db3"))
        paths = list(paths_ros1) + list(paths_ros2)

        if len(paths) == 0:
            # Empty list of paths
            raise RuntimeWarning(f"Specified folder {self.folder} contains no bagfiles")

        if self.durations:
            # Durations have already been extracted
            warnings.warn(
                "Durations are already exported, yet the durations dict will be recreated.",
                RuntimeWarning,
            )

        # Create a dictionary with the durations for each bag file
        # {file1: duration1, ...}
        durations = {}
        print(
            f"Extracting durations from {len(paths)} rosbags in {self.folder.resolve().name}"
        )
        with tqdm(total=len(paths)) as pbar:
            for bagfile in paths:
                pbar.set_description(bagfile.stem)
                durations[bagfile.stem] = self.get_duration(bagfile)
                pbar.update(1)

        self.durations = durations
        self._compute_total()

    @staticmethod
    def get_duration(filename: Path | str) -> float:
        """Get the duration of a rosbag file

        Args:
            filename: path of the rosbag file

        Returns:
            float: duration in the rosbag file
        """
        ros1 = filename.suffix == ".bag"
        Reader = Reader1 if ros1 else Reader2
        with Reader(filename) as bag:
            return (bag.duration) / 1e9

    def _check_data_extraction(self, caller_name: str):
        """Assert that extract_data() was called"""
        if not self.durations:
            raise RuntimeError(
                "Durations are not extracted. "
                f"Call 'extract_data()' before calling '{caller_name}'"
            )

    def _compute_total(self) -> None:
        self._check_data_extraction(self._compute_total.__name__)
        self.durations[self.TOTAL_KEY] = self.total

    def export_metadata(self, path: Path | str = None) -> None:
        """Export duration dictionary to a metadata file

        Args:
            path: path of the metadata file. Defaults to None.
            If None, the durations will be saved in durations_<foldername>.json.
        """
        self._check_data_extraction(self.export_metadata.__name__)

        # Default value
        path = f"durations_{self.folder.resolve().name}.json" if path is None else path

        # Infer from path extension
        ext = Path(path).suffix[1:].lower()
        if ext not in ("json", "yaml", "yml"):
            raise NotImplementedError(
                f"Metadata format {ext} is not supported. Try using json or yaml"
            )

        self._compute_total()

        with open(path, "w", encoding="utf-8") as file:
            if ext == "json":
                json.dump(self.durations, file)
            elif ext in ("yaml", "yml"):
                yaml.dump(self.durations, file)

    def to_yaml_str(self) -> str:
        """Exports a yaml-serialized string from the durations dictionary

        Returns:
            str: YAML-serialized string with durations summary
        """
        self._compute_total()
        time_pprint = lambda t: f"{str(timedelta(seconds=t)):0>8}"
        durations = {k: time_pprint(t) for k, t in self.durations.items()}

        return yaml.dump(durations)
