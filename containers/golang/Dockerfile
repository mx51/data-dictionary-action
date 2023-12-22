FROM golang:1.21-alpine

RUN apk update && apk add bash build-base

ARG tool_type=rubenv-sql-migrate
RUN if [ "$tool_type" = "rubenv-sql-migrate" ]; then \
    # CGO_CFLAGS is a temporary fix for https://github.com/mattn/go-sqlite3/pull/1177.
    CGO_CFLAGS="-D_LARGEFILE64_SOURCE" go install github.com/rubenv/sql-migrate/...@latest; \
  fi

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
