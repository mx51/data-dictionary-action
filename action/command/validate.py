import json
import logging
from typing import Optional

import requests

from .base import Command


class Validate(Command):
    def __init__(
        self,
        workspace: str,
        github_repository: str,
        github_token: Optional[str],
        github_pull: Optional[str],
        github_commit: Optional[str],
    ):
        super().__init__(workspace)
        self.github_repository = github_repository
        self.github_token = github_token
        self.github_pull = github_pull
        self.github_commit = github_commit

    def execute(self):
        errors = []

        data = self.read_data()
        for store in data.get("stores", []):
            if not store or "name" not in store:
                logging.warning("Found invalid store: %s", store)
                continue

            store_path = store["name"]

            for table in store.get("tables", []):
                if not table or "name" not in table:
                    logging.warning("Found invalid table: %s", table)
                    continue

                table_path = f"{store_path}.{table['name']}"

                if not table.get("description"):
                    error = f"Missing description in table `{table_path}`"
                    logging.error(error)
                    errors.append(error)

                for field in table.get("fields", []):
                    if not field or "name" not in field:
                        logging.warning("Found invalid field: %s", field)
                        continue

                    field_path = f"{table_path}.{field['name']}"

                    if not field.get("description"):
                        error = f"Missing description in field `{field_path}`"
                        logging.error(error)
                        errors.append(error)

        if errors:
            self._github_request(
                method="post",
                context=f"issues/{self.github_pull}/comments",
                data={
                    "body": (
                        f"### :no_entry_sign: Validation errors in `data.json` {self.github_commit}\n\n"
                        + "\n".join([f"- {error}" for error in errors])
                    ),
                },
            )

    def _github_request(self, method: str, context: str, data: dict):
        if not self.github_token:
            logging.warning(
                "Skipping GitHub API request (no token): %s %s %s",
                method,
                context,
                data,
            )
            return

        r = requests.request(
            method=method,
            url=f"https://api.github.com/repos/{self.github_repository}/{context}",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.github_token}",
            },
            data=json.dumps(data),
            timeout=30,
        )
        if not r.ok:
            logging.error("Failed to create pull comment: %s", r)
