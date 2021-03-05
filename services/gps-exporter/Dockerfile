#####
## Source Stage
#####
FROM --platform=$BUILDPLATFORM rust:slim-buster as sources
WORKDIR /app

RUN cargo init
COPY ./Cargo.toml .
COPY ./Cargo.lock .

RUN mkdir -p /app/.cargo && cargo vendor /app/vendor > /app/.cargo/config

#####
## Build Stage
#####
FROM rust:slim-buster as builder
WORKDIR /app

COPY ./Cargo.toml /app/Cargo.toml
COPY ./Cargo.lock /app/Cargo.lock
COPY ./src /app/src
COPY --from=sources /app/.cargo /app/.cargo
COPY --from=sources /app/vendor /app/vendor

RUN cargo build --release --offline

######
### Runtime Stage
######
FROM debian:buster
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/periodic/gps-exporter
ADD run-gps-exporter /etc/periodic/gps-exporter/run-gps-exporter
RUN chmod +x /etc/periodic/gps-exporter/run-gps-exporter

ADD crontab /etc/cron.d/gps-exporter
RUN crontab /etc/cron.d/gps-exporter

COPY --from=builder /app/target/release/gps-exporter .

ENTRYPOINT echo "The time is $(date +%Y/%m/%d-%H:%M:%S)" && cron -f -l 8 -L /proc/1/fd/1
