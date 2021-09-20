#!/bin/bash

set -e

ACTION_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/.."

if [[ -z "$GITHUB_WORKSPACE" ]]; then
    echo "Required: GITHUB_WORKSPACE"
    exit 1
fi
if [[ -z "$GITHUB_REPOSITORY" ]]; then
    echo "Required: GITHUB_REPOSITORY"
    exit 1
fi
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "Required: GITHUB_TOKEN"
    exit 1
fi
if [[ -z "$GITHUB_PULL" ]]; then
    echo "Required: GITHUB_PULL"
    exit 1
fi

cd $GITHUB_WORKSPACE

echo "Configuring git..."
git config user.name github-actions
git config user.email github-actions@github.com

if git ls-files --modified --others --exclude-standard | grep data.json > /dev/null ; then
    echo "Committing data.json changes..."
    git add data.json
    git commit -m "Update data.json"
    git push
fi

export GITHUB_COMMIT=`git rev-parse HEAD`

cd $ACTION_PATH

python3 -m action validate
