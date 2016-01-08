# Qubinode

[![Build Status](https://travis-ci.org/gak/qubinode.svg?branch=develop)](https://travis-ci.org/gak/qubinode)

Taken from the words "**Qu**ick **Bi**tcoin **No**de **De**ploy", pronounced qui-bee-node.

## Warning!

This project is currently under construction! The odds are this won't work for you :)

It is in currently in development so it will probably change for the better, day by day.

Also please note that the script currently runs bitcoind as root, and will default to a non-privilieged user in near future.

## Overview

The goal of this project is to easily deploy a Bitcoin node on an Ubuntu Linux host, initially aiming for Digital Ocean and Google Cloud Platform.

### Features - Working

 * Single liner automated command to deploy to a DigitalOcean host with hardcoded values, i.e. BitcoinXT, 512mb instance, blockchain pruning.
 * Ability to enter in an API key so the user doesn't need to create the host or log into the VM.

### Features - In progress

 * The choice of Bitcoin version and distribution.
 * OS X compatibility

### Features - Near future

 * Ability to run this from Windows, maybe via a simple GUI window
 * A check to see if the port is accessable

## Usage

### Overview

There are different ways of using Qubinode shown in the sections below, ordered by easiest difficulty first.

You will need a DigitalOcean account and have generated a "Personal Access Token" in the "API" section.
This token can be deleted after the Bitcoin node has been deployed.

The core of Qubinode is a single python script (qubinode.py) which relies on some dependencies.

There is also a bootstrap shell script which sets up a system (Ubuntu 14.04 only at the moment) system with the correct packages to be able to run the python script.

### One liner to spawn a VM

This one liner will probably only work on Ubuntu or Debian based systems. It has only been tested on Ubuntu 14.04.

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s spawn do
```

### Locally install on an existing Ubuntu 14.04 Linux host

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s install
```

### Spawn a VM from Linux or OS X without bootstrap script

You'll need to install some packages:

 * python (2.7+)
 * python pip or easy_install
 * python development libs (python-dev or python-devel)
 * gcc

Next, install the python dependencies using either `easy_install` or `pip install`:

```
pip install requests python-digitalocean pycrypto docopt paramiko
```

Fetch the `qubinode.py` Python script:

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/qubinode.py > qubinode.py
```

Now you can run it. Here is an example interactive session:

```
root@3444c31d49bf:~# python qubinode.py 
Usage:
  qubinode.py spawn (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                    [options]
  qubinode.py local [--release=<version>] [--prune=<MB>]
                    [--swapfile-size=<MB>] [--swapfile-path=<path>]
  qubinode.py list-versions
  qubinode.py list-providers

root@3444c31d49bf:~# python qubinode.py spawn digitalocean

We will now:
 - Generate or reuse an SSH key pair in *TODO* some directory.
 - Create a $5/mo, 512MB, 1 CPU instance in a random data center.

Once started:
 - A SSH key pair will be left in *TODO* some directory which can
   be used for SSHing into the droplet.
 - Your droplet will continue living forever until you stop it.
 - Your DigitalOcean access token will not be saved to disk and
   will be forgotten once the script has ended.

Press Ctrl-C to abort!

Enter a DigitalOcean access token: ABCD1234

[...snip...]

Downloading https://github.com/bitcoinxt/bitcoinxt/releases/download/v0.11D/bitcoin-xt-0.11.0-D-linux64.tar.gz
Downloading https://github.com/bitcoinxt/bitcoinxt/releases/download/v0.11D/bitcoin-xt-0.11.0-D-linux64.tar.gz complete...
Checking sha256 of package...
Installing files...
Creating boot scripts...
Creating logrotate configuration...
Creating bitcoin.conf
Starting daemon...
Done!
```

### Locally install on a Linux host

Similar to above, install the dependencies to allow qubinode.py to run.

There are a few options to customise the install:

```
root@3444c31d49bf:~# python qubinode.py local --help
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode.py spawn (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                    [options]
  qubinode.py local [--release=<version>] [--prune=<MB>]
                    [--swapfile-size=<MB>] [--swapfile-path=<path>]
  qubinode.py list-versions
  qubinode.py list-providers

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  -b --batch                 Non-interactive and choose all options by default.

Install options:
  -s --swapfile=<MB>         Create a swapfile
  --swapfile-path=<path>     Specify swapfile path [default: /swapfile]

Bitcoin options:
  -r --release=<version>     Bitcoin node release [default: XT/0.11D]
  -p --prune=<MB>            Blockchain pruning [default: 2048]

Spawn options:
  --priv-key-path=<path>     [default: ~/.ssh/qubinode]
  --pub-key-path=<path>      [default: ~/.ssh/qubinode.pub]

DigitalOcean options:
  --do-size=<slug>           Size of the provider's instance [default: 512mb]
```

You can simply run the following to install to your own Linux host:

```
root@3444c31d49bf:~# python qubinode.py local --prune=2048 --release=BU/0.11.2

Swapfile already set up...
Checking sha256 of package...
bitcoinUnlimited-0.11.2/
bitcoinUnlimited-0.11.2/bin/
bitcoinUnlimited-0.11.2/bin/bitcoin-cli
bitcoinUnlimited-0.11.2/bin/bitcoind
bitcoinUnlimited-0.11.2/bin/bitcoin-qt
bitcoinUnlimited-0.11.2/bin/bitcoin-tx
bitcoinUnlimited-0.11.2/bin/test_bitcoin
bitcoinUnlimited-0.11.2/bin/test_bitcoin-qt
bitcoinUnlimited-0.11.2/include/
bitcoinUnlimited-0.11.2/include/bitcoinconsensus.h
bitcoinUnlimited-0.11.2/lib/
bitcoinUnlimited-0.11.2/lib/libbitcoinconsensus.so
bitcoinUnlimited-0.11.2/lib/libbitcoinconsensus.so.0
bitcoinUnlimited-0.11.2/lib/libbitcoinconsensus.so.0.0.0
Installing files...
'bin/bitcoin-qt' -> '/usr/bin/bitcoin-qt'
'bin/bitcoin-tx' -> '/usr/bin/bitcoin-tx'
'bin/bitcoin-cli' -> '/usr/bin/bitcoin-cli'
'bin/test_bitcoin' -> '/usr/bin/test_bitcoin'
'bin/test_bitcoin-qt' -> '/usr/bin/test_bitcoin-qt'
'bin/bitcoind' -> '/usr/bin/bitcoind'
'include/bitcoinconsensus.h' -> '/usr/include/bitcoinconsensus.h'
'lib/libbitcoinconsensus.so.0.0.0' -> '/usr/lib/libbitcoinconsensus.so.0.0.0'
removed '/usr/lib/libbitcoinconsensus.so'
'lib/libbitcoinconsensus.so' -> '/usr/lib/libbitcoinconsensus.so'
removed '/usr/lib/libbitcoinconsensus.so.0'
'lib/libbitcoinconsensus.so.0' -> '/usr/lib/libbitcoinconsensus.so.0'
Creating boot scripts...
Creating logrotate configuration...
Creating bitcoin.conf
Starting daemon...
```

## Detailed steps

 * curl downloads and executes a bash script (one liner)
 * bash script:
  * installs python with build tools (apt based at the moment)
  * installs required python libraries
  * downloads the python qubinode script and executes with the `spawn do` argument
 * qubinode:
  * asks the user for a DO access token
  * sets up a new do VM
  * uploads itself to the VM
  * remotely executes qubinode.py with the `install` argument on the VM 
 * qubinode on the VM:
  * creates a swapfile if one doesn't exist on /swapfile
  * downloads the requested version of bitcoin
  * verifies hash
  * extracts
  * installs
  * creates upstart file
  * creates a bitcoin.conf with 5GB pruning and random RPC creds
  * starts the node
 
