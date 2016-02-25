FROM ubuntu:14.04

RUN mkdir /root/.ssh
RUN chmod 700 /root/.ssh

ADD ssh-keys/test.pub /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

