#!/bin/bash

poetry run python src/main.py $@
poetry run python src/parse_tags.py
poetry run python src/sync_db_to_stash.py
