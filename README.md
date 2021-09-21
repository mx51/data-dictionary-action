# data-dictionary-action

GitHub Action for generating and checking freshness of `data.json` data dictionaries.

## Inputs

* `store-name` - Name of the data store.
* `store-type` - Type of the data store.
    - [`postgres`](https://www.postgresql.org/)
* `tool-type` - Type of the data tool (e.g. migration).
    - [`rubenv-sql-migrate`](https://github.com/rubenv/sql-migrate)
* `tool-path` - Path to the data tool files (e.g. migration).
* `repo-token` - GitHub auth token for pull request comments (NOT for commits).

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
```
