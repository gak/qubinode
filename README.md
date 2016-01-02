# Qubinode

Taken from the words "**Qu**ick **Bi**tcoin **No**de **De**ploy", pronounced qui-bee-node.

## Warning!

This project is currently under construction! The odds are this won't work for you :)

It is in currently in development so it will probably change for the better, day by day.

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

The core of this is a single python script (qubinode.py) which relies on some dependencies.

There is also a bootstrap shell script which sets up a system (Ubuntu 12.04 only at the moment) system with the correct packages to be able to run the python script.

### One liner to spawn a VM

You will need a DigitalOcean account and have generated a "Personal Access Token" in the "API" section.
This token can be deleted after the Bitcoin node has been deployed.

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s spawn do
```

### On an existing Ubuntu 14.04 Linux host

**NOTE** This assumes an empty system as it sets up a swapfile, etc.

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s install
```

### On other Linux hosts

You'll need to install some packages:

 * python (2.7+)
 * python pip or easy_install
 * python development libs (python-dev or python-devel)
 * gcc

Next, install the python dependencies using either `easy_install` or `pip install`:

```
pip install requests python-digitalocean pycrypto docopt paramiko
```

Fetch the library:

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/qubinode.py
```

Now you can run it. Here is an example interactive session:

```
root@3444c31d49bf:# python qubinode.py 
Usage:
  qubinode.py spawn (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                    [options]
  qubinode.py local [--release=<version>] [--prune=<MB>]
                    [--swapfile-size=<MB>] [--swapfile-path=<path>]
  qubinode.py list-versions
  qubinode.py list-providers

root@3444c31d49bf:# python qubinode.py spawn do

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

## Detailed steps

 * curl downloads a bash script (one liner)
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
 
