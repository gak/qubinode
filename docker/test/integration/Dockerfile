FROM qubinode_test_quick

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# SSH login fix. Otherwise user is kicked off after login
# RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

CMD /usr/sbin/sshd -D

