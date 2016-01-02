#!/bin/bash

# Quit script on any error
set -e

echo Installing Dependencies...
apt-get update
apt-get install -y python-setuptools python-dev gcc

echo Installing required Python packages...
easy_install pip
pip install requests python-digitalocean pycrypto docopt paramiko

echo Fetching Python script...
#if [ ! -f deploylib.py ]; then
#    curl blah > /tmp/ python $@
#fi

echo Running Python script... $@
python qubinode.py $@

