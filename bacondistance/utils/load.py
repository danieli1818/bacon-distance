"""This module provides utility functions for loading a MoviesActorsDataset
from JSON files.

Functions:
- load_dataset(file_path: str | Path) -> MoviesActorsDataset:
    Loads and deserializes a MoviesActorsDataset from a specified JSON file.

Example usage:
    from dataset_loader import load_dataset

    dataset = load_dataset("path/to/dataset.json")
"""

import json
from pathlib import Path

from bacondistance.utils.models import MoviesActorsDataset


def load_dataset(file_path: str | Path) -> MoviesActorsDataset:
    """Loads a `MoviesActorsDataset` from a JSON file.

    Reads the JSON content at the specified file path and deserializes it into
    a `MoviesActorsDataset` object.

    Args:
        file_path (str | Path): Path to the JSON file containing the dataset.

    Returns:
        MoviesActorsDataset: The loaded dataset.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValidationError: If the data does not match the expected schema for
        `MoviesActorsDataset`.
    """
    file_path = Path(file_path)
    with open(file_path) as fd:
        return MoviesActorsDataset(**json.load(fd))
