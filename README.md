# data-dictionary-action

GitHub Action for generating and checking freshness of `data.json` data dictionaries.

## Inputs

* `store-name` - Name of the data store.
* `store-type` - Type of the data store.
    - [`postgres`](https://www.postgresql.org/)
* `tool-type` - Type of the data tool (e.g. migration).
    - [`rubenv-sql-migrate`](https://github.com/rubenv/sql-migrate)
* `tool-path` - Path to the data tool files (e.g. migration).
* `repo-token` - GitHub auth token for pull request comments (NOT for commits). Defaults to `${{ github.token }}`.
* `data-dictionary-app-id` - Data Dictionary GitHub App ID.
* `data-dictionary-app-private-key` - Data Dictionary GitHub App private key.
* `data-dictionary-repo` - Data Dictionary repo name. Defaults to `data-dictionary`.
* `data-dictionary-ref` - Data Dictionary branch reference. Defaults to `master`.
* `data-dictionary-workflow` - Data Dictionary workflow name. Defaults to `build.yml`.

## Example

Below is an example recommended GitHub Actions workflow:

```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize]
    branches:
      - master
    paths:
      - "schema/**"
      - "data.json"

jobs:
  tag:
    runs-on: ubuntu-latest
    name: data-dictionary
    steps:
      - uses: actions/checkout@v2
        with:
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: 2

      - uses: mx51/data-dictionary-action@master
        with:
          store-name: my-store-name
          store-type: postgres
          tool-type: rubenv-sql-migrate
          tool-path: schema
          data-dictionary-app-id: ${{ secrets.DATA_DICTIONARY_APP_ID }}
          data-dictionary-app-private-key: ${{ secrets.DATA_DICTIONARY_APP_PRIVATE_KEY }}
```

## Development

For local development, ensure the following are installed:

- Docker
- Python 3.10+

The following environment variables are required to be set (e.g. `.env` file):

- `GITHUB_REPOSITORY` - org/repo that you are testing against (see [default environment variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables))
- `GITHUB_WORKSPACE` - path to directory you are testing against (see [default environment variables](https://docs.github.com/en/actions/learn-github-actions/environment-variables#default-environment-variables))
- `STORE_NAME` (see `inputs.store-name`)
- `STORE_TYPE` (see `inputs.store-type`)
- `TOOL_TYPE` (see `inputs.tool-type`)
- `TOOL_PATH` (see `inputs.tool-path`)

If you want to test Git actions (committing and pushing changes), set the following variables as well:

- `GITHUB_TOKEN` (see `inputs.repo-token`)
- `GITHUB_PULL` (see `github.event.pull_request.number`)

Once everything is set, execute the action script:

```shell
make run
```
