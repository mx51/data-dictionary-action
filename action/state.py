import logging
from typing import List, Optional


def _find_by_name(items: List[dict], matching: dict, name="name") -> Optional[dict]:
    for item in items:
        if item[name] == matching[name]:
            return item
    return None


def _copy_keys(source: dict, target: dict, exclude=()):
    for key, val in source.items():
        if key not in exclude:
            target[key] = val


def merge(data: dict, source: str, store: dict):
    """Merge existing data state with target.

    Args:
        data (dict): Data state.
        source (str): New source.
        store (dict): New store.
    """

    data["source"] = {
        **data.get("source", {}),
        **source,
    }

    existing_stores = data.get("stores", [])
    if not existing_stores:
        data["stores"] = [store]
        return

    existing_store = None
    for s in existing_stores:
        if s.get("name") == store.get("name"):
            existing_store = s
            break

    # Leave unrelated stores, copy keys from new store to existing
    _copy_keys(source=store, target=existing_store, exclude=("tables",))

    tables = store.get("tables", [])
    for table in tables:
        existing_table = _find_by_name(existing_store.get("tables", []), table)
        if existing_table:
            _copy_keys(source=existing_table, target=table, exclude=("fields",))
            for field in table.get("fields", []):
                existing_field = _find_by_name(existing_table.get("fields", []), field)
                if existing_field:
                    _copy_keys(source=existing_field, target=field)

        table.get("fields", []).sort(key=lambda x: x.get(("ord",)))

    tables.sort(key=lambda x: x["name"])

    existing_store["tables"] = tables


def _validate_description(item: dict, path: list) -> bool:
    description = item.get("description")

    if not description:
        logging.critical("Missing description in %s", ".".join(path))
        return False

    return True


def validate(data: dict):
    """Validates current state of data. This relies on automatic fixes made by above functions.

    Args:
        data (dict): Data state.

    Returns:
        bool: True for valid, invalid otherwise.
    """

    valid = True

    for store in data.get("stores", []):
        store_path = [store["name"]]

        for table in store.get("tables", []):
            table_path = store_path + [table["name"]]

            valid &= _validate_description(table, table_path)

            for field in table.get("fields", []):
                field_path = table_path + [field["name"]]

                valid &= _validate_description(field, field_path)

    return valid
