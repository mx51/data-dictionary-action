import os
import sys
import json
import logging
from pathlib import Path

from .state import merge, validate

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

STORE_NAME = os.environ["STORE_NAME"]
STORE_TYPE = os.environ["STORE_TYPE"]
TOOL_TYPE = os.environ["TOOL_TYPE"]
TOOL_PATH = os.environ["TOOL_PATH"]
GITHUB_WORKSPACE = os.environ["GITHUB_WORKSPACE"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_REPOSITORY_NAME = GITHUB_REPOSITORY.split("/").pop()
GITHUB_REPOSITORY_URL = "https://github.com/" + GITHUB_REPOSITORY

path = Path(GITHUB_WORKSPACE) / "data.json"
data = {}

if path.exists():
    try:
        with open(path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        logging.warning("Failed to parse existing data.json")
else:
    logging.warning("Failed to find data.json")

# Import modules inside branch with appropriate dependencies loaded
if STORE_TYPE == "postgres":
    from .store.postgres import read_store

    store = read_store(
        name=STORE_NAME,
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
else:
    logging.critical("Store %s not found", STORE_TYPE)
    sys.exit(1)

merge(
    data=data,
    source={
        "name": GITHUB_REPOSITORY_NAME,
        "url": GITHUB_REPOSITORY_URL,
    },
    store=store,
)

with open(path, mode="w", encoding="utf-8") as f:
    json.dump(data, f, skipkeys=True, indent=4)

if not validate(data):
    logging.critical("Validation failed, check logs above for errors")
    sys.exit(1)
