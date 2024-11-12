FROM golang:1.23-alpine

RUN apk update && apk add bash build-base git

RUN go env -w GOFLAGS="-buildvcs=false"

ARG tool_type=rubenv-sql-migrate
RUN if [ "$tool_type" = "rubenv-sql-migrate" ]; then \
    go install github.com/rubenv/sql-migrate/...@latest; \
  fi

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
