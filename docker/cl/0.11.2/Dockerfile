FROM qubinode_base

RUN wget https://github.com/bitcoinclassic/bitcoinclassic/releases/download/v0.11.2.cl1/bitcoin-0.11.2-linux64.tar.gz
RUN echo "3f4eb95a832c205d1fe3b3f4537df667f17f3a6be61416d11597feb666bde4ca  bitcoin-0.11.2-linux64.tar.gz" | sha256sum -c
RUN tar xf bitcoin-0.11.2-linux64.tar.gz
RUN cp -pr bitcoin-0.11.2-linux64/* /usr/
