#!/bin/bash

set -ex

echo Installing Dependencies...
apt-get update
apt-get install -y python-setuptools python-dev gcc

echo Installing required Python packages...
easy_install pip
pip install requests python-digitalocean pycrypto docopt paramiko

echo Running Qubinode with args: $@
qubinode $@

