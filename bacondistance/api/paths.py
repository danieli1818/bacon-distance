import os.path

from bacondistance.utils.paths import FRONTEND_DIR_PATH, PROJECT_ROOT_DIR_PATH

DATA_PATH = PROJECT_ROOT_DIR_PATH / "data"
DATASET_PATH = DATA_PATH / "dataset.json"
FRONTEND_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), FRONTEND_DIR_PATH
)

TITLE_BASICS_IMDB_DATA_PATH = DATA_PATH / "title.basics.tsv"
TITLE_PRINCIPALS_IMDB_DATA_PATH = DATA_PATH / "title.principals.tsv"
NAME_BASICS_IMDB_DATA_PATH = DATA_PATH / "name.basics.tsv"
