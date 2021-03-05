FROM --platform=$BUILDPLATFORM rust as planner
WORKDIR /app

RUN cargo install cargo-chef
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM --platform=$BUILDPLATFORM rust as cacher
WORKDIR /app

RUN cargo install cargo-chef
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json

FROM rust as builder
WORKDIR /app
COPY . .
COPY --from=cacher /app/target target
COPY --from=cacher $CARGO_HOME $CARGO_HOME

RUN cargo build --release

FROM debian:buster-slim
WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/periodic/gps-exporter
ADD run-gps-exporter /etc/periodic/gps-exporter/run-gps-exporter
RUN chmod +x /etc/periodic/gps-exporter/run-gps-exporter

ADD crontab /etc/cron.d/gps-exporter
RUN crontab /etc/cron.d/gps-exporter

COPY --from=builder /app/target/release/gps-exporter .

ENTRYPOINT echo "The time is $(date +%Y/%m/%d-%H:%M:%S)" && cron -f -l 8 -L /proc/1/fd/1


