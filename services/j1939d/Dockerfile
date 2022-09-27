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
## Cross build Stage 
#####
FROM --platform=$BUILDPLATFORM rust:buster AS cross-builder

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
#RUN cargo install cross --git https://github.com/cross-rs/cross
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y g++-arm-linux-gnueabihf \
                       g++-aarch64-linux-gnu \
                       libc6-dev-armhf-cross \
                       libc6-dev-arm64-cross
                       
RUN rustup target add $(cat /rust_target.txt)
RUN rustup toolchain install stable-$(cat /rust_target.txt)

ENV USER=1000

COPY ./Cargo.toml /app/Cargo.toml
COPY ./Cargo.lock /app/Cargo.lock
COPY ./src /app/src
COPY --from=sources /app/.cargo /app/.cargo
COPY --from=sources /app/vendor /app/vendor

ENV CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=arm-linux-gnueabihf-gcc \
    CC_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-gcc \
    CXX_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-g++

ENV CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc \
    CC_aarch64_unknown_linux_gnu=aarch64-linux-gnu-gcc \
    CXX_aarch64_unknown_linux_gnu=aarch64-linux-gnu-g++

#RUN cross build --release --offline --target $(cat /rust_target.txt)
RUN cargo build --release --offline --target $(cat /rust_target.txt)
RUN cp /app/target/$(cat /rust_target.txt)/release/j1939d .

######
## Post-build Stage
######
FROM rust:buster AS post-builder
WORKDIR /app

COPY --from=cross-builder /app/j1939d . 

RUN strip j1939d

######
### Runtime Stage
######
FROM debian:buster
WORKDIR /app

RUN apt-get update && apt-get install -y libssl1.1

COPY --from=post-builder /app/j1939d .

ENTRYPOINT [ "./j1939d" ]
