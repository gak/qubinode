FROM qubinode_base

RUN wget https://github.com/bitcoinclassic/bitcoinclassic/releases/download/v0.11.2.cl1/bitcoin-0.11.2-linux64.tar.gz
RUN echo "ba0e8d553271687bc8184a4a703f4eb95a832c205d1fe3b3f4537df667f17f3a6be61416d11597feb666bde4ca70e5d350171036f13c838db49bb0aabe5c5e49  bitcoin-0.11.2-linux64.tar.gz" | sha256sum -c
RUN tar xf bitcoin-0.11.2-linux64.tar.gz
RUN cp -pr bitcoin-0.11.2-linux64/* /usr/
