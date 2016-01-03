#!/bin/bash

set -e

CONF_DIR=~/.bitcoin
CONF_FILE=$CONF_DIR/bitcoin.conf

# Create bitcoin.conf if doesn't exist
if [ ! -f $CONF_FILE ]; then
    mkdir -p $CONF_DIR

    echo "rpcuser=qubinode" >> $CONF_FILE
    echo "rpcpassword=$(dd if=/dev/urandom bs=50 count=1 status=none | base64)" >> $CONF_FILE

    if [ -n $BITCOIN_PRUNE ]; then
        echo "prune=$BITCOIN_PRUNE" >> $CONF_FILE
    fi
fi

exec "$@"
