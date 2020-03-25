FROM buildpack-deps:buster AS builder
#TODO: arm build, FROM balenalib/apalis-imx6q-debian:latest-build as builder

RUN apt-get update && \
      apt-get install -y --no-install-recommends \
      libsasl2-2 \
      libsasl2-dev \
      libssl-dev \
      librdkafka1 \
      librdkafka-dev \
      libavro23 \
      libavro-dev
COPY . /build

WORKDIR /build

RUN /build/configure CFLAGS="-DDEBUG" && make

FROM debian:buster
#TODO: arm run container, FROM balenalib/apalis-imx6q-debian:latest-run
WORKDIR /usr/app
COPY --from=builder /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
#TODO: 1. change to arm lib dirs
#      2. static build
COPY --from=builder /build/kafka_can_log/kafka_can_log .
COPY --from=builder /build/start.sh .

CMD ["./start.sh"]
