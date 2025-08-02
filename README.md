# Bacon Distance Project - Milestone #0

## 🎯 Objective
The goal of this milestone is to generate a structured dataset that will later allow us to compute distances between actors, and specifically the "Bacon Distance" (i.e., the minimal number of connections between an actor and Kevin Bacon based on shared movie appearances).

## 🧱 Project Structure (Current Stage)
This milestone focuses on creating the foundational database using a Python script called `generate_db.py`.

## 📄 File: `generate_db.py`
This script generates a database file in JSON format containing:
- A mapping from each movie to the list of actors in it.
- A mapping from each actor to the mapping of their co-actors and the amount of shared movies they have.

Usage example:
```shell
python3 generate_db.py -tb ./datasources/title.basics.tsv -tp ./datasources/title.principals.tsv -nb ./datasources/name.basics.tsv -o ./datasources/dataset.json
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
