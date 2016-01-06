#!/bin/bash

set -ex

CONF_DIR=~/.bitcoin
CONF_FILE=$CONF_DIR/bitcoin.conf

# Create bitcoin.conf if doesn't exist
if [ ! -f $CONF_FILE ]; then
    mkdir -p $CONF_DIR
    cd $CONF_DIR

    echo "rpcuser=qubinode" >> $CONF_FILE
    echo "rpcpassword=$(dd if=/dev/urandom bs=50 count=1 status=none | base64)" >> $CONF_FILE

    if [ -n $BITCOIN_PRUNE ]; then
        echo "prune=$BITCOIN_PRUNE" >> $CONF_FILE
    fi

    if [ -n $BITCOIN_BOOTSTRAP ]; then
        curl $BITCOIN_BOOTSTRAP > bootstrap
        tar xvf bootstrap
    fi
fi

exec "$@"
