import os
import sys

import paramiko
from Crypto.PublicKey import RSA

from entrypoint import FILE_PATH


class Provider(object):
    def __init__(self, config):
        self.config = config
        self.ensure_key_pairs()

    def ipaddress(self):
        raise NotImplementedError()

    def ensure_key_pairs(self):
        if not os.path.exists(self.config.priv_key_path):
            self.generate_key_pairs()
        self.load_key_pairs()

    def ensure_key_paths(self):
        try:
            os.makedirs(os.path.dirname(self.config.priv_key_path))
        except OSError:
            pass

        try:
            os.makedirs(os.path.dirname(self.config.priv_key_path))
        except OSError:
            pass

    def generate_key_pairs(self):
        self.ensure_key_paths()

        key = RSA.generate(2048)

        with open(self.config.priv_key_path, 'w') as f:
            f.write(key.exportKey('PEM'))
            f.write('\n')
        with open(self.config.pub_key_path, 'w') as f:
            f.write(key.publickey().exportKey('OpenSSH'))

        os.chmod(self.config.priv_key_path, 0600)

    def load_key_pairs(self):
        self.pub_key = open(self.config.pub_key_path).read()
        self.priv_key = open(self.config.priv_key_path).read()

    def connect(self):
        # TODO: Use fabric api for this
        print('Connecting to {}...'.format(self.ip_address))
        pkey = paramiko.RSAKey.from_private_key_file(
                self.config.priv_key_path
        )
        self.transport = paramiko.Transport((self.ip_address, 22))
        self.transport.connect(username='root', pkey=pkey)

    def remote_put(self, sftp, filename):
        src = os.path.join(FILE_PATH, filename)
        # TODO: Use fabric api for this
        try:
            if sftp.lstat(filename):
                sftp.unlink(filename)
        except IOError:
            pass

        sftp.put(src, os.path.join('qubinode', filename))

    def deploy(self):
        # TODO: Use fabric api for this
        print('Uploading Qubinode...')
        sftp = paramiko.SFTPClient.from_transport(self.transport)

        try:
            sftp.lstat('qubinode')
        except IOError:
            sftp.mkdir('qubinode')

        self.remote_put(sftp, 'bootstrap.sh')
        self.remote_put(sftp, 'qubinode.py')

    def run(self):
        # TODO: Use fabric api for this
        print('Executing Qubinode on host...')
        self.channel = self.transport.open_channel('session')

        cmd = [
            'bash -c "cd qubinode && bash bootstrap.sh local',
            '--release={}'.format(self.config.release),
        ]

        if self.config.prune:
            cmd.append('--prune={}'.format(self.config.prune))

        if self.config.bootstrap:
            cmd.append('--bootstrap={}'.format(self.config.bootstrap))

        cmd.append('"')

        cmd = ' '.join(cmd)
        print(cmd)

        self.channel.exec_command(cmd)

        while not self.channel.exit_status_ready():
            while self.channel.recv_ready():
                data = self.channel.recv(1024 * 8)
                sys.stdout.write(data)
            while self.channel.recv_stderr_ready():
                data = self.channel.recv_stderr(1024 * 8)
                sys.stdout.write(data)

        status = self.channel.recv_exit_status()
        if status:
            raise Exception('Error with status code: {}'.format(status))

        print('Done!')
