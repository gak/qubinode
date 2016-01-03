FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y wget

ADD docker-entrypoint.sh /docker-entrypoint.sh

VOLUME /root/.bitcoin/

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD bitcoind -printtoconsole -disablewallet
