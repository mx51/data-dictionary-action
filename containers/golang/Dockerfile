FROM golang:1.21-alpine3.18

RUN apk update && apk add bash build-base

#ENV CGO_CFLAGS="-D_LARGEFILE64_SOURCE"

ARG tool_type=rubenv-sql-migrate
RUN if [ "$tool_type" = "rubenv-sql-migrate" ]; then \
    go install github.com/rubenv/sql-migrate/...@latest; \
  fi

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
