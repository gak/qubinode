import os

from Crypto.PublicKey import RSA
from fabric.context_managers import settings
from fabric.contrib.project import rsync_project
from fabric.operations import run, put

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


class Provider(object):
    def __init__(self, config):
        self.config = config
        self.ensure_key_pairs()

    def ip_address(self):
        raise NotImplementedError

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

    def with_env(self):
        return {
            'host_string': self.ip_address(),
            'disable_known_hosts': True,
            'key': self.config.priv_key_path,
        }

    def deploy(self):
        self.upload()
        self.run()
        self.show_connection_instructions()

    def upload(self):
        print('Uploading Qubinode...')
        with settings(**self.with_env()):
            put(os.path.join(self.config.base_dir, 'bootstrap.sh'))
            rsync_project('qubinode', self.config.base_dir)

    def run(self):
        print('Executing Qubinode on host...')
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

        with settings(**self.with_env()):
            run(cmd)

        print('Done!')

    def show_connection_instructions(self):
        print('Host Address is {}'.format(self.ip_address()))
        print('You can access the VM via this command:')
        print('\nssh -i {} root@{}\n'.format(
                self.config.priv_key_path, self.ip_address()
        ))

