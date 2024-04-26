from pathlib import Path
from typing import List, Optional

from ..proto import ProtoReader
from ..store import Store
from .base import Command


class Generate(Command):
    def __init__(
        self,
        workspace: str,
        store: Store,
        source: dict,
        proto_path: Optional[str] = "",
    ):
        """Creates a new instance of Generate.

        Args:
            workspace (str): The workspace to generate on.
            store (Store): The store instance.
            source (dict): The source name.
            proto_path (str, optional): Path to the proto files. Defaults to "".
        """
        super().__init__(workspace=workspace)
        self.store = store
        self.source = source
        self.proto_path = proto_path

    def execute(self):
        """Read sources and update the data dictionary."""
        data = self.read_data()
        if data is None:
            data = {}

        store = self.store.read()

        if self.proto_path:
            proto_reader = ProtoReader(proto_path=self._workspace / Path(self.proto_path))
            proto = proto_reader.read()
        else:
            proto = {}

        self.merge_data(data, store, proto)
        self.write_data(data)

    def merge_data(self, data: dict, store: dict, proto: dict):
        """Merge new data into the data dictionary.

        Args:
            data (dict): Existing data dictionary.
            store (dict): Store data.
            proto (dict): Proto data.
        """
        data["source"] = data.get("source", {}) | self.source

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
                    if proto_type := field.get("proto_type"):
                        proto_values = proto.get(proto_type)
                        if proto_values:
                            field["values"] = proto_values

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
