FROM alpine:latest

RUN apk update && apk add curl \
    && curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/bin/mc \
    && chmod +x /usr/bin/mc

WORKDIR /root/
ADD save_result.sh /root/
