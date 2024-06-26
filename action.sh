#!/bin/bash

set -e

ACTION_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [[ -z "$STORE_NAME" ]]; then
    echo "ERROR: missing STORE_NAME"
    exit 1
fi
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
if [[ -z "$GITHUB_WORKSPACE" ]]; then
    echo "ERROR: missing GITHUB_WORKSPACE"
    exit 1
fi
if [[ -z "$GITHUB_REPOSITORY" ]]; then
    echo "ERROR: missing GITHUB_REPOSITORY"
    exit 1
fi
if [[ -z "$GITHUB_TOKEN" ]] || [[ -z "$GITHUB_PULL" ]]; then
    echo "WARNING: missing GITHUB_TOKEN or GITHUB_PULL, skipping git actions"
    SKIP_GIT=1
fi
if [[ -z "$REQUIRED_ROLES" ]]; then
    echo "WARNING: missing REQUIRED_ROLES, consider adding them to the action config"
fi
if [[ -z "$PROTO_PATH" ]]; then
    echo "INFO: missing PROTO_PATH, skipping reading proto files for values"
fi
if [[ -z "$EXCLUDE_TABLES" ]]; then
    if [ "$TOOL_TYPE" = "rubenv-sql-migrate" ]; then
        export EXCLUDE_TABLES=migrations
    fi
fi


DOCKER_CLEANUP=""

cleanup () {
    echo "Cleaning up..."
    if [[ ! -z "$DOCKER_CLEANUP" ]]; then
        docker rm --force $DOCKER_CLEANUP
    fi
}

trap cleanup EXIT

prepare () {
    pip3 install -r $ACTION_PATH/requirements.txt
}

generate () {
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
                -v $ACTION_PATH/containers/postgres/initdb.sh:/docker-entrypoint-initdb.d/initdb.sh \
                -p 5432:5432 \
                -e POSTGRES_DB=${DB_NAME} \
                -e POSTGRES_USER=${DB_USER} \
                -e POSTGRES_PASSWORD=${DB_PASSWORD} \
                -e REQUIRED_ROLES="${REQUIRED_ROLES}" \
                --name $postgres_container \
                postgres:14

            DOCKER_CLEANUP="$postgres_container $DOCKER_CLEANUP"
            ;;

        *)
            echo "ERROR: no store type for '$STORE_TYPE'"
            exit 2

    esac

    case "$TOOL_TYPE" in

        rubenv-sql-migrate|shell-script)
            docker build -t data-dictionary-golang ./containers/golang --build-arg tool_type=$TOOL_TYPE

            docker run --rm \
                -v $GITHUB_WORKSPACE:/workspace \
                -e STORE_TYPE \
                -e TOOL_TYPE \
                -e TOOL_PATH \
                -e DB_NAME \
                -e DB_USER \
                -e DB_PASSWORD \
                -e GITHUB_TOKEN \
                --name data-dictionary-golang \
                data-dictionary-golang
            ;;

        *)
            echo "ERROR: no tool type for '$TOOL_TYPE'"
            exit 2

    esac

    python3 -m action generate
}

validate () {
    cd $GITHUB_WORKSPACE

    if [[ -z "$SKIP_GIT" ]]; then
        if git ls-files --modified --others --exclude-standard | grep data.json > /dev/null ; then
            echo "Committing data.json changes..."
            git add data.json
            git commit -m "Update data.json"
            git push
        fi

        export GITHUB_COMMIT=`git rev-parse HEAD`
    fi

    cd $ACTION_PATH

    python3 -m action validate
}

cd $GITHUB_WORKSPACE

if [[ -z "$SKIP_GIT" ]]; then
    echo "Configuring git..."
    git config user.name github-actions
    git config user.email github-actions@github.com

    if ! git diff --name-only HEAD~1 HEAD > /dev/null ; then
        echo "Failed to fetch HEAD~1, ensure actions/checkout fetch-depth is 2 or more..."
        exit 1
    fi
fi

prepare
generate
validate
