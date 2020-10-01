
FROM debian:buster-backports

WORKDIR /usr/src/app

RUN apt-get -y update

RUN apt-get install -y --no-install-recommends autoconf autotools-dev automake make build-essential libconfig-dev linux-headers-$(uname -r) git ca-certificates  

RUN git clone https://github.com/linux-can/socketcand.git

WORKDIR /usr/src/app/socketcand

RUN ./autogen.sh && ./configure

RUN make && make install



CMD ["socketcand"]
