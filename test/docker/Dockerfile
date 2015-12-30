FROM ubuntu-upstart:14.04

RUN apt-get install -y python
RUN apt-get install -y python-setuptools
RUN dpkg-divert --local --rename --add /sbin/initctl && ln -s /bin/true /sbin/initctl

