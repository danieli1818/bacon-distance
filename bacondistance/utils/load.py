import json

from bacondistance.utils.models import MoviesActorsDataset


def load_dataset(file_path: str) -> MoviesActorsDataset:
    """
    Loads the dataset from the give json file path.

    :param file_path: The file path to the dataset.
    :return: The loaded movies dataset.
    """
    with open(file_path, 'rt') as fd:
        return MoviesActorsDataset(**json.load(fd))
