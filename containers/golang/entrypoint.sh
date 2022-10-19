#!/bin/bash

set -e

if [[ -z "$STORE_TYPE" ]]; then
    echo "ERROR: missing STORE_TYPE"
    exit 1
fi
if [[ -z "$TOOL_TYPE" ]]; then
    echo "ERROR: missing TOOL_TYPE"
    exit 1
fi
if [[ -z "$TOOL_PATH" ]]; then
    echo "ERROR: missing TOOL_PATH"
    exit 1
fi

case "$TOOL_TYPE" in

    rubenv-sql-migrate)
        case "$STORE_TYPE" in
            postgres) 
                dialect=postgres 
                ;;
            *) 
                echo "ERROR: no store type for '$STORE_TYPE'"
                exit 2
        esac

        cat << EOF > ./dbconfig.yml
development:
  dialect: $dialect
  datasource: host=172.17.0.1 dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD} sslmode=disable
  dir: ./workspace/${TOOL_PATH}
  table: migrations
EOF

        echo "Migrating github.com/rubenv/sql-migrate..."
        sql-migrate up
        ;;

    *)
        echo "ERROR: no tool type for '$TOOL_TYPE'"
        exit 2

esac
