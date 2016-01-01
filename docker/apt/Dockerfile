FROM qubinode_upstart

RUN apt-get update
RUN apt-get install -y python-setuptools python-dev gcc
RUN easy_install pip
RUN pip install requests python-digitalocean pycrypto docopt paramiko

