FROM golang:1.21-alpine

RUN apk update && apk add bash build-base

# Temporary fix for https://github.com/mattn/go-sqlite3/pull/1177. We can remove this once rubenv-sql-migrate is updated to use the patched version of go-sqllite3.
ENV CGO_CFLAGS="-D_LARGEFILE64_SOURCE"

ARG tool_type=rubenv-sql-migrate
RUN if [ "$tool_type" = "rubenv-sql-migrate" ]; then \
    go install github.com/rubenv/sql-migrate/...@latest; \
  fi

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
