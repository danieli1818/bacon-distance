# Bacon Distance Project - Milestone #2

## 🎯 Objective
The goal of this milestone is to use the scripts created in the previous milestones in a web app to calculate bacon distances of actors.

## 🧱 Project Structure (Current Stage)
Milestone-0 focuses on creating the foundational database using a Python script called `generate_db.py`.
Milestone-1 focuses on calculating the "Bacon Distance" of a given actor using a Python script called `bacon_distance.py`.
Milestone-2 focuses on creating a web app to allow the user to easily query bacon distances of actors.

## 📄 File: `bacondistance/scripts/generate_db.py`
This script generates a database file in JSON format containing:
- A mapping from each movie to the list of actors in it.
- A mapping from each actor to the mapping of their co-actors and the amount of shared movies they have.

Usage example:
```shell
poetry run python bacondistance/scripts/generate_db.py -tb ./datasources/title.basics.tsv -tp ./datasources/title.principals.tsv -nb ./datasources/name.basics.tsv -o ./datasources/dataset.json
```

Where the tsvs files are from IMDB:
https://developer.imdb.com/non-commercial-datasets/.
And the dataset.json is the output dataset file.

## 🧠 Data Format

The generated JSON file looks like this:

```json
{
  "movies_casts": {
    "Fast & Furious": ["Vin Diesel", "Gal Gadot"],
    "Justice League": ["Gal Gadot", "Ben Affleck"],
    "Footloose": ["Kevin Bacon", "Gal Gadot", "Ben Affleck"]
  },
  "actors_graph": {
    "Vin Diesel": {"Gal Gadot": 1},
    "Gal Gadot": {"Vin Diesel": 1, "Ben Affleck": 2, "Kevin Bacon": 1},
    "Ben Affleck": {"Gal Gadot": 2, "Kevin Bacon": 1},
    "Kevin Bacon": {"Gal Gadot": 1, "Ben Affleck": 1}
  }
}
```

An example can be seen in `examples/dataset_example.json`.

## 📄 File: `bacondistance/scripts/bacon_distance.py`
This script calculates the bacon distance of the given actor, according to the given dataset from milestone-0.

Usage example:
```shell
poetry run python bacondistance/scripts/bacon_distance.py -ac "Gal Gadot" -ds ./datasources/dataset.json
```

Where the ac is the actor name and the dataset.json is the dataset file from milestone-0.

## 🌐 Bacon Distance Web App
This app is divided into backend in the `bacondistance/api` directory
and the frontend in the `frontend` directory.
To run the web app after creating a venv using poetry, you need to run from the root project directory:
```shell
poetry run uvicorn bacondistance.api.main:app --reload
```
Then use a browser to connect to the web app.
The app is using the dataset in the `examples/dataset_example.json`,
you can easily change it in the `bacondistance/utils/paths.py` file in the `DEFAULT_DATASET_PATH` variable.
