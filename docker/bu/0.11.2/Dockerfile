FROM qubinode_base

RUN wget http://www.bitcoinunlimited.info/public/downloads/bitcoinUnlimited-0.11.2-linux64.tar.gz
RUN echo "c6e83e5910d6b4ad852ac6d6a9ec6c92001a5070bb51d4292577174f22495355  bitcoinUnlimited-0.11.2-linux64.tar.gz" | sha256sum -c
RUN tar xf bitcoinUnlimited-0.11.2-linux64.tar.gz
RUN cp -pr bitcoinUnlimited-0.11.2/* /usr/
