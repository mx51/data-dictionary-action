FROM golang:1.20-alpine

RUN apk update && apk add bash build-base

ARG tool_type=rubenv-sql-migrate
RUN if [ "$tool_type" = "rubenv-sql-migrate" ]; then \
    go get -v github.com/rubenv/sql-migrate/...; \
  fi

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
