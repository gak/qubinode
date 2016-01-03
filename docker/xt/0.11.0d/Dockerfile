FROM qubinode_base

RUN wget https://github.com/bitcoinxt/bitcoinxt/releases/download/v0.11D/bitcoin-xt-0.11.0-D-linux64.tar.gz
RUN echo "ba0e8d553271687bc8184a4a7070e5d350171036f13c838db49bb0aabe5c5e49  bitcoin-xt-0.11.0-D-linux64.tar.gz" | sha256sum -c
RUN tar xf bitcoin-xt-0.11.0-D-linux64.tar.gz
RUN cp -pr bitcoin-xt-0.11.0-D/* /usr/
