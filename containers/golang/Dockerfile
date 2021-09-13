FROM golang:1.17-alpine

RUN apk update && apk add bash build-base

RUN go get -v github.com/rubenv/sql-migrate/...

WORKDIR /

COPY entrypoint.sh ./

ENTRYPOINT [ "/entrypoint.sh" ]
