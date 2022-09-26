#####
## Source Stage
#####
FROM --platform=$BUILDPLATFORM rust:buster AS sources
WORKDIR /app

ENV USER=1000

RUN cargo init
COPY ./Cargo.toml .
COPY ./Cargo.lock .

RUN mkdir -p /app/.cargo && cargo vendor /app/vendor > /app/.cargo/config

#####
## Build Stage 
#####
FROM --platform=$BUILDPLATFORM rust:buster AS builder

WORKDIR /app

ARG TARGETPLATFORM

## Select the right target for cross-compilation
RUN case "$TARGETPLATFORM" in \
      "linux/arm/v7") echo armv7-unknown-linux-gnueabihf > /rust_target.txt ;; \
      "linux/arm64") echo aarch64-unknown-linux-gnu > /rust_target.txt ;; \
      "linux/amd64") echo x86_64-unknown-linux-gnu > /rust_target.txt ;; \
      *) exit 1 ;; \
    esac

## Install dependencies for both targets
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y g++-arm-linux-gnueabihf \
                       g++-aarch64-linux-gnu \
                       libc6-dev-armhf-cross \
                       libc6-dev-arm64-cross
                       
RUN rustup target add $(cat /rust_target.txt)

ENV USER=1000

COPY ./Cargo.toml /app/Cargo.toml
COPY ./Cargo.lock /app/Cargo.lock
COPY ./src /app/src
COPY --from=sources /app/.cargo /app/.cargo
COPY --from=sources /app/vendor /app/vendor

RUN cargo build --release --offline --target $(cat /rust_target.txt)
RUN strip /app/target/$(cat /rust_target)/release/j1939d

######
### Runtime Stage
######
FROM debian:buster
WORKDIR /app

RUN apt-get update && apt-get install -y libssl1.1

COPY --from=builder /app/target/release/j1939d .

ENTRYPOINT [ "./j1939d" ]
