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
            select
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.column_default,
                c.is_nullable,
                c.data_type,
                tc.constraint_type = 'PRIMARY KEY' as is_primary_key
            from information_schema.columns as c
                join pg_class as pgc
                    on c.table_schema = pgc.relnamespace::regnamespace::text
                    and c.table_name = pgc.relname
                left join information_schema.key_column_usage as kcu
                    on c.table_catalog = kcu.table_catalog
                    and c.table_schema = kcu.table_schema
                    and c.table_name = kcu.table_name 
                    and c.column_name = kcu.column_name
                left join information_schema.table_constraints as tc
                    on kcu.table_catalog = tc.table_catalog
                    and kcu.table_schema = tc.table_schema
                    and kcu.table_name = tc.table_name 
                    and kcu.constraint_name = tc.constraint_name
            where
                pgc.relispartition = false
                and pgc.relkind in ('r', 'v', 'm', 'p')
                and c.table_schema not in ('information_schema', 'pg_catalog') 
                and c.table_name not in ('migrations')
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
