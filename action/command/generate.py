from typing import Optional, List
from .base import Command
from ..store import Store


class Generate(Command):
    def __init__(self, workspace: str, store: Store, source: dict):
        super().__init__(workspace)
        self.store = store
        self.source = source

    def execute(self):
        data = self.read_data()
        if data is None:
            data = {}

        store = self.store.read()

        self.merge_data(data, store)
        self.write_data(data)

    def merge_data(self, data: dict, store: dict):
        data["source"] = {
            **data.get("source", {}),
            **self.source,
        }

        self._sort_store(store)

        existing_stores = data.get("stores", [])
        existing_store = self._find_by_name(existing_stores, store)
        if not existing_store:
            data["stores"] = existing_stores + [store]
            return

        # Leave unrelated stores, copy keys from new store to existing
        self._copy_keys(
            source=store,
            target=existing_store,
            exclude=("tables", "type"),
        )

        tables = store.get("tables", [])
        for table in tables:
            existing_table = self._find_by_name(existing_store.get("tables", []), table)
            if existing_table:
                self._copy_keys(
                    source=existing_table,
                    target=table,
                    exclude=("fields", "schema"),
                )
                for field in table.get("fields", []):
                    existing_field = self._find_by_name(
                        existing_table.get("fields", []), field
                    )
                    if existing_field:
                        self._copy_keys(
                            source=existing_field,
                            target=field,
                            exclude=("data_type", "nullable", "primary_key", "default"),
                        )

        existing_store["tables"] = tables

    @staticmethod
    def _sort_store(store: dict):
        tables = store.get("tables", [])
        for table in tables:
            table.get("fields", []).sort(key=lambda x: x.get(("ord",)))

        tables.sort(key=lambda x: x["name"])

    @staticmethod
    def _find_by_name(items: List[dict], matching: dict, name="name") -> Optional[dict]:
        for item in items:
            if item[name] == matching[name]:
                return item
        return None

    @staticmethod
    def _copy_keys(source: dict, target: dict, exclude=()):
        for key, val in source.items():
            if key not in exclude:
                target[key] = val
