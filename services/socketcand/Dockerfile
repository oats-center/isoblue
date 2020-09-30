
FROM debian:buster-backports

WORKDIR /usr/src/app

RUN apt-get -y update

RUN apt-get install -y --no-install-recommends autoconf autotools-dev automake make build-essential libconfig-dev linux-headers-$(uname -r) 

COPY socketcand-src ./

RUN ./autogen.sh

RUN ./configure

RUN make && make install

CMD ["socketcand"]
