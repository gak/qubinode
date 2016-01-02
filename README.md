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

You will need a Digital Ocean account and have generated a "Personal Access Token" in the "API" section.
This token can be deleted after the Bitcoin node has been deployed.

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s spawn
```

### On an existing Ubuntu 14.04 Linux host

**NOTE** This assumes an empty system as it sets up a swapfile, etc.

```
\curl https://raw.githubusercontent.com/gak/qubinode/develop/src/bootstrap.sh | bash -s install
```

## Detailed notes

 * curl downloads a bash script
 * bash script:
  * installs python with build tools (apt based at the moment)
  * installs required python libraries
  * downloads the python qubinode script and executes with the `spawn` argument
 * qubinode:
  * sets up a new VM
  * uploads itself to the VM and executes with the `install` argument
 * qubinode on the VM:
  * creates a 2GB swapfile if one doesn't exist on /swapfile
  * downloads the requested version of bitcoin
  * verifies hash
  * extracts
  * installs
  * creates upstart file
  * creates a bitcoin.conf with 5GB pruning and random rpc creds
  * starts the node
 
