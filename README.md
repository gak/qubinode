QuBiNoDe - Quick Bitcoin Node Deploy

The goal of this project is to easily deploy a Bitcoin node on an Ubuntu Linux host, initially aiming for Digital Ocean and Google Cloud.

Core functionality:
 * A "One click" installer
 * Ability to enter in an API key so the user doesn't need to log into the box
 * The choice of Bitcoin version and distribution

Aiming for:

 * Minimum Linux skills needed, assuming a Windows or OS X user
 * Cross platform including Windows
 * A check to see if the port is accessable

Ideally it would be running a Python script, then being asked a few questions:
```
# python quibinode.py

C: Bitcoin Core
X: BitcoinXT
U: Bitcoin Unlimited
Which distribution of Bitcoin would you like deployed [C,X,U] ?

Possible versions: 0.10.1, 0.10.2, 0.11.0.
Which version would you like to install [Enter for latest] ?

D: Digital Ocean
G: Google Cloud
Which provider to install to [D,G]?
```

or on the host:
```
curl https://github.com/gak/qubinode/deploy.sh | sh
```
