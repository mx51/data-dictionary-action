import psycopg2
import psycopg2.extras
from typing import Tuple, Dict


def read_store(name: str, database: str, user: str, password: str) -> dict:
    """Reads store from PostgreSQL database.

    Args:
        name (str): Store name.
        database (str): PostgreSQL database name.
        user (str): PostgreSQL user.
        password (str): PostgreSQL password.

    Returns:
        dict: Store entry dictionary.
    """

    conn = psycopg2.connect(
        host="localhost",
        database=database,
        user=user,
        password=password,
    )

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        """
        select
            table_schema,
            table_name,
            column_name,
            ordinal_position,
            column_default,
            is_nullable,
            data_type
        from information_schema.columns 
        where 
            table_schema not in ('information_schema', 'pg_catalog') 
            and table_name not in ('migrations')
        ;"""
    )

    table_lookup: Dict[Tuple, Dict] = {}

    for row in cur.fetchall():
        table_schema = row["table_schema"]
        table_name = row["table_name"]
        table_key = (table_schema, table_name)

        table = table_lookup.get(table_key, {})
        table["name"] = table_name
        table["schema"] = table_schema
        table["description"] = ""

        fields = table.get("fields", {})
        field_name = row["column_name"]

        field = {
            ("ord",): row["ordinal_position"],
            "name": field_name,
            "data_type": row["data_type"],
            "description": "",
            "nullable": row["is_nullable"] == "YES",
        }
        default = row["column_default"]
        if default is not None:
            field["default"] = default

        fields[field_name] = field

        table["fields"] = fields
        table_lookup[table_key] = table

    tables = []
    for table in table_lookup.values():
        table["fields"] = list(table.get("fields", {}).values())
        tables.append(table)

    return {
        "name": name,
        "type": "postgres",
        "tables": tables,
    }
