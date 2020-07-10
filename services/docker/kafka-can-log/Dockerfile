FROM buildpack-deps:buster AS builder

RUN apt-get update && \
      apt-get install -y --no-install-recommends \
      automake \
      libsasl2-2 \
      libsasl2-dev \
      libssl-dev \
      librdkafka1 \
      librdkafka-dev \
      libavro23 \
      libavro-dev

COPY . /build

WORKDIR /build

RUN autoreconf --install || exit 1
RUN /build/configure CFLAGS="-DDEBUG" && make

FROM debian:buster
WORKDIR /usr/app

COPY --from=builder /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=builder /build/kafka_can_log/kafka_can_log .
COPY --from=builder /build/start.sh .

CMD ["./start.sh"]
