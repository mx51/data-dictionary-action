#!/bin/bash

set -e

ACTION_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/.."

if [[ -z "$STORE_NAME" ]]; then
    echo "Required: STORE_NAME"
    exit 1
fi
if [[ -z "$STORE_TYPE" ]]; then
    echo "Required: STORE_TYPE"
    exit 1
fi
if [[ -z "$TOOL_TYPE" ]]; then
    echo "Required: TOOL_TYPE"
    exit 1
fi
if [[ -z "$TOOL_PATH" ]]; then
    echo "Required: TOOL_PATH"
    exit 1
fi
if [[ -z "$GITHUB_WORKSPACE" ]]; then
    echo "Required: GITHUB_WORKSPACE"
    exit 1
fi
if [[ -z "$GITHUB_REPOSITORY" ]]; then
    echo "Required: GITHUB_REPOSITORY"
    exit 1
fi

DOCKER_CLEANUP=""

cleanup () {
    echo "Cleaning up..."
    if [[ ! -z "$DOCKER_CLEANUP" ]]; then
        docker rm --force $DOCKER_CLEANUP
    fi
}

trap cleanup EXIT

cd $ACTION_PATH

case "$STORE_TYPE" in

    postgres)
        echo "Configuring 'postgres' store..."
        export DB_NAME=postgres
        export DB_USER=postgres
        export DB_PASSWORD=postgres

        pip3 install -r ./requirements-postgres.txt

        postgres_container=data-dictionary-postgres
        
        docker run -d \
            -p 5432:5432 \
            -e POSTGRES_DB=${DB_NAME} \
            -e POSTGRES_USER=${DB_USER} \
            -e POSTGRES_PASSWORD=${DB_PASSWORD} \
            --name $postgres_container \
            postgres:13

        DOCKER_CLEANUP="$postgres_container $DOCKER_CLEANUP"
        ;;

    *) 
        echo "ERROR: no store type for '$STORE_TYPE'"
        exit 2

esac

case "$TOOL_TYPE" in

    rubenv-sql-migrate)
        docker build -t data-dictionary-golang ./containers/golang

        docker run --rm \
            -v $GITHUB_WORKSPACE:/workspace \
            -e STORE_TYPE \
            -e TOOL_TYPE \
            -e TOOL_PATH \
            -e DB_NAME \
            -e DB_USER \
            -e DB_PASSWORD \
            --name data-dictionary-golang \
            data-dictionary-golang
        ;;

    *)
        echo "ERROR: no tool type for '$TOOL_TYPE'"
        exit 2

esac

python3 -m action generate
