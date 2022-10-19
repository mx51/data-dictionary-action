import os
import sys
import argparse
import logging
from .command import Generate, Validate

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "command",
    choices=["generate", "validate"],
    help="Command to execute",
)
args = parser.parse_args(args=sys.argv[1:])

GITHUB_WORKSPACE = os.environ["GITHUB_WORKSPACE"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_REPOSITORY_NAME = GITHUB_REPOSITORY.split("/").pop()
GITHUB_REPOSITORY_URL = "https://github.com/" + GITHUB_REPOSITORY

if args.command == "generate":
    store_type = os.environ["STORE_TYPE"]
    # Import modules inside branch with appropriate dependencies loaded
    if store_type == "postgres":
        from .store.postgres import PostgresStore

        store = PostgresStore(
            name=os.environ["STORE_NAME"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
    else:
        raise ValueError(f"Store {store_type} not found")

    Generate(
        workspace=GITHUB_WORKSPACE,
        store=store,
        source={
            "name": GITHUB_REPOSITORY_NAME,
            "url": GITHUB_REPOSITORY_URL,
        },
    ).execute()

elif args.command == "validate":
    Validate(
        workspace=GITHUB_WORKSPACE,
        github_repository=GITHUB_REPOSITORY,
        github_token=os.getenv("GITHUB_TOKEN"),
        github_pull=os.getenv("GITHUB_PULL"),
        github_commit=os.getenv("GITHUB_COMMIT"),
    ).execute()
