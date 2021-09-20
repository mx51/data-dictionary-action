import logging
from .base import Command


class Validate(Command):
    def __init__(self, workspace: str, token: str):
        super().__init__(workspace)
        if not token:
            logging.critical("Token missing!")

    def execute(self):
        data = self.read_data()

        valid = True

        for store in data.get("stores", []):
            store_path = [store["name"]]

            for table in store.get("tables", []):
                table_path = store_path + [table["name"]]

                valid &= self._validate_description(table, table_path)

                for field in table.get("fields", []):
                    field_path = table_path + [field["name"]]

                    valid &= self._validate_description(field, field_path)

        return valid

    @staticmethod
    def _validate_description(item: dict, path: list) -> bool:
        description = item.get("description")

        if not description:
            logging.critical("Missing description in %s", ".".join(path))
            return False

        return True
