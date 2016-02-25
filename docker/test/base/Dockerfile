FROM ubuntu:14.04

RUN mkdir /root/.ssh
RUN chmod 700 /root/.ssh

ADD ssh-keys/test.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

