# QuBiNoDe - Quick Bitcoin Node Deploy

**WARNING** This project is currently under construction! Most things here probably won't work, and the code is probably only useful for developers.

The goal of this project is to easily deploy a Bitcoin node on an Ubuntu Linux host, initially aiming for Digital Ocean and Google Cloud Platform.

## Features - Initially

 * An almost completely automated installer from Linux or OS X.
 * Ability to enter in an API key so the user doesn't need to create the host or log into the VM.
 * The choice of Bitcoin version and distribution.

## Features - Near future

 * Ability to run this from Windows, maybe via a simple GUI window
 * A check to see if the port is accessable

## How to use

### Spawn to a new host

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
 ** installs python with build tools (apt based at the moment)
 ** installs required python libraries
 ** downloads the python qubinode script and executes with the `spawn` argument
 * qubinode:
 ** sets up a new VM
 ** uploads itself to the VM and executes with the `install` argument
 * qubinode on the VM:
 ** creates a 2GB swapfile if one doesn't exist on /swapfile
 ** downloads the requested version of bitcoin
 ** verifies hash
 ** extracts
 ** installs
 ** creates upstart file
 ** creates a bitcoin.conf with 5GB pruning and random rpc creds
 ** starts the node
 
