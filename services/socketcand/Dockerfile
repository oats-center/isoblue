
# Builder

FROM buildpack-deps:buster

ARG commit=ae0af08

WORKDIR /usr/src/app

RUN apt-get -y update

RUN git clone https://github.com/linux-can/socketcand.git

WORKDIR /usr/src/app/socketcand

RUN git checkout $commit 

RUN ./autogen.sh && ./configure

RUN make 

# Runtime

FROM debian:buster-slim

WORKDIR /usr/src/app

COPY --from=0 /usr/src/app/socketcand/socketcand .

COPY socketcand.sh .

CMD ["./socketcand.sh"]
