import logging
import json
import jsoncfg
from jsoncfg.config_classes import (
    ConfigNode,
    ConfigJSONObject,
    ConfigJSONArray,
    ConfigJSONScalar,
)
import requests
from typing import Any
from .base import Command


class Validate(Command):
    def __init__(
        self,
        workspace: str,
        github_repository: str,
        github_token: str,
        github_commit: str,
        github_pull: str,
    ):
        super().__init__(workspace)
        self.github_repository = github_repository
        self.github_token = github_token
        self.github_commit = github_commit
        self.github_pull = github_pull
        self.github_path = "data.json"

    def execute(self):
        data = jsoncfg.load_config(str(self.data_path))
        data, _ = self._augment(data)

        valid = True

        stores, stores_line = data.get("stores", (None, None))
        if stores:
            for store, store_line in stores:
                if not store:
                    self._error("Empty store.", stores_line)
                    continue

                valid &= self._validate_description(store, store_line)

                tables, tables_line = store.get("tables", (None, None))
                if tables:
                    for table, table_line in tables:
                        if not table:
                            self._error("Empty table.", tables_line)
                            continue

                        valid &= self._validate_description(table, table_line)

                        fields, fields_line = table.get("fields", (None, None))
                        if fields:
                            for field, field_line in fields:
                                if not field:
                                    self._error("Empty field.", fields_line)
                                    continue

                                valid &= self._validate_description(field, field_line)

        return valid

    def _validate_description(self, item: dict, line: int) -> bool:
        description, description_line = item.get("description", (None, None))
        line = description_line if description_line else line

        if not description:
            self._error("Missing description.", line)
            return False

        return True

    def _error(self, message: str, line: int):
        logging.critical("L%s: %s", line, message)

        self._github_request(
            method="post",
            context=f"pulls/{self.github_pull}/comments",
            data={
                "body": message,
                "path": self.github_path,
                "side": "RIGHT",
                "line": line,
                "commit_id": self.github_commit,
            },
        )

    def _github_request(self, method: str, context: str, data: dict):
        r = requests.request(
            method=method,
            url=f"https://api.github.com/repos/{self.github_repository}/{context}",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.github_token}",
            },
            data=json.dumps(data),
        )
        if not r.ok:
            logging.error("Failed to create pull comment: %s", r)

    @staticmethod
    def _augment(element: ConfigNode) -> Any:
        line = jsoncfg.node_location(element).line
        if isinstance(element, ConfigJSONObject):
            output_dict = {}
            for key, value in element:
                output_dict[key] = Validate._augment(value)
            return (output_dict, line)
        elif isinstance(element, ConfigJSONArray):
            output_list = []
            for item in element:
                output_list.append(Validate._augment(item))
            return (output_list, line)
        elif isinstance(element, ConfigJSONScalar):
            return (element(), line)
        else:
            raise ValueError(f"Unknown element type: {element}")
