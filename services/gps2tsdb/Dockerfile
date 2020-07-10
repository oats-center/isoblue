#####
# Build stage
#####
FROM --platform=$BUILDPLATFORM rust as builder

ARG BUILDPLATFORM
ARG TARGETPLATFORM

#ARG BUILD_DATE
#ARG GIT_REF
#ARG VERSION

RUN echo "b BUILD: ${BUILDPLATFORM} TARGET: ${TARGETPLATFORM}"

WORKDIR /tmp/build

# Build the dependencies to improve Docker cache
#COPY Cargo.toml Cargo.lock ./
#RUN mkdir src/
#RUN echo "fn main() {println!(\"if you see this, the build broke\")}" > src/main.rs
#RUN cargo build --release
#RUN rm -rf target/release/deps/gps2tsdb*

RUN rustup target add armv7-unknown-linux-gnueabihf
RUN apt update && apt install --yes gcc-arm-linux-gnueabihf

# Do the full build
COPY . .
RUN cargo build --release --target=armv7-unknown-linux-gnueabihf

#####
# Final stage
#####
FROM --platform=$TARGETPLATFORM debian:buster-slim

ARG TARGETPLATFORM
ARG BUILD_DATE
ARG GIT_REF
ARG VERSION

LABEL maintainer="abalmos" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/oats-group/isoblue-avena" \
  org.opencontainers.image.source="https://github.com/oats-group/isoblue-avena" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$GIT_REF \
  org.opencontainers.image.vendor="OATS Center" \
  org.opencontainers.image.title="gps2tsdb" \
  org.opencontainers.image.description="Moves GPSD reports into Timescale DB" \
  org.opencontainers.image.licenses="MIT"

COPY --from=builder /tmp/build/target/armv7-unknown-linux-gnueabihf/relesae/gps2tsdb /usr/local/bin/gps2tsdb

CMD ["/usr/local/bin/gps2tsdb"]
