import psycopg2
import psycopg2.extras
from typing import Tuple, Dict, Any
from .base import Store


class PostgresStore(Store):
    def __init__(self, name: str, database: str, user: str, password: str):
        self.meta = {
            "name": name,
            "type": "postgres",
        }
        self.conn = psycopg2.connect(
            host="localhost",
            database=database,
            user=user,
            password=password,
        )

    def read(self) -> dict:
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            """
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.column_default,
                c.is_nullable,
                c.data_type,
                tc.constraint_type = 'PRIMARY KEY' as is_primary_key
            FROM information_schema.columns AS c
				JOIN pg_class AS pgc
					ON c.table_schema = pgc.relnamespace::regnamespace::text
					AND c.table_name = pgc.relname
                LEFT JOIN information_schema.key_column_usage AS kcu
                    on c.table_catalog = kcu.table_catalog
                    AND c.table_schema = kcu.table_schema
                    AND c.table_name = kcu.table_name 
                    AND c.column_name = kcu.column_name
                LEFT JOIN information_schema.table_constraints AS tc
                    ON kcu.table_catalog = tc.table_catalog
                    AND kcu.table_schema = tc.table_schema
                    AND kcu.table_name = tc.table_name 
                    AND kcu.constraint_name = tc.constraint_name
            WHERE 
				pgc.relispartition = false AND
                c.table_schema NOT IN ('information_schema', 'pg_catalog') 
                AND c.table_name NOT IN ('migrations')
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
                field["default"] = self._clean_column_default(default)
            is_primary_key = row["is_primary_key"]
            if is_primary_key is not None:
                field["primary_key"] = is_primary_key

            fields[field_name] = field

            table["fields"] = fields
            table_lookup[table_key] = table

        return {
            **self.meta,
            "tables": self._table_lookup_to_list(table_lookup),
        }

    @staticmethod
    def _table_lookup_to_list(table_lookup: Dict[Tuple, Dict]) -> list:
        tables = []
        for table in table_lookup.values():
            table["fields"] = list(table.get("fields", {}).values())
            tables.append(table)
        return tables

    @staticmethod
    def _clean_column_default(value: str) -> Any:
        if value.endswith("::text"):
            # Unwrap value cast to text as a string
            value = value[0 : -len("::text")]
            if value[0] == value[-1] == "'" and value.count("'") == 2:
                value = value[1:-1]

        return value
