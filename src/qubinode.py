#!/usr/bin/env python
'''
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode.py spawn-vm (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                       [options]
  qubinode.py local [options]
  qubinode.py list-releases
  qubinode.py list-providers

Options:
  -h --help                  Show this screen
  --version                  Show version
  -b --batch                 Non-interactive and choose all options by default

Install options:
  -s --swapfile=<MB>         Create a swapfile
  --swapfile-path=<path>     Specify swapfile path [default: /swapfile]

Bitcoin options:
  -r --release=<version>     Bitcoin node release [default: ask]
  -p --prune=<MB>            Blockchain pruning [default: 5000]
  -o --bootstrap=<URL>       URL to bootstrap or tarball of blockchain dirs

Spawn options:
  --priv-key-path=<path>     [default: ~/.ssh/qubinode]
  --pub-key-path=<path>      [default: ~/.ssh/qubinode.pub]

DigitalOcean options:
  --do-size=<slug>           Size of the provider's instance [default: 512mb]

'''
import functools
import os
import random
import subprocess
import sys
import textwrap
import time
import traceback

import digitalocean as do
import paramiko
from Crypto.PublicKey import RSA
from docopt import docopt

__version__ = '0.0.1'

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

NAMES = {
    'bc': 'Bitcoin Core',
    'xt': 'BitcoinXT',
    'bu': 'Bitcoin Unlimited',
}

# Not sure what to put in here yet... I'm sure there will be something
RELEASES = {
    'xt:0.11.0d': {},
    'bu:0.11.2': {},
}

PROVIDERS = {
    'do': {
        'name': 'DigitalOcean',
        'class': 'DigitalOcean',
    }
}


class Qubinode:
    def __init__(self):
        self.config = Config()

    def run(self):
        self.config.setup()

        if self.config.list_releases:
            self.list_releases()
            return

        self.ask_release()

        if self.config.spawn_vm:
            self.boot()

        if self.config.local:
            LocalInstaller(self.config).setup()

    def list_releases(self):
        for release, info in RELEASES.items():
            print(' - {}'.format(release))

    def ask_release(self):
        if self.config.release != 'ask':
            pass
        elif self.config.batch:
            self.config.release = 'xt:0.11.0d'
        else:
            self.list_releases()
            self.config.release = raw_input('Which release to install? ')

        if self.config.release not in RELEASES:
            print('Unknown release: {}'.format(self.config.release))
            sys.exit(-1)

    def boot(self):
        '''
        Run the provider class that will start the VM.

        e.g. the "do" provider will instantiate the DigitalOcean class.
        '''
        fun = globals()[self.config.provider['class']]
        fun(self.config).setup()


class Config(object):
    def __init__(self):
        self.args = {}

    def __getattribute__(self, key):
        '''
        Allows attribute access to the docopt args dictionary.

        e.g. config.batch instead of config.args.batch
        '''
        if key != 'args' and key in self.args:
            return self.args[key]
        else:
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key != 'args' and key in self.args:
            self.args[key] = value
        else:
            return object.__setattr__(self, key, value)

    @property
    def provider_key(self):
        if self.do or self.digitalocean:
            return 'do'

    @property
    def provider(self):
        return PROVIDERS[self.provider_key]

    def parse_args(self):
        self.args = docopt(__doc__, version=__version__)

    def setup(self):
        self.parse_args()
        # self.ask()
        self.normalise()

    def normalise_path(self, key):
        self.args[key] = os.path.expanduser(self.args[key])
        self.args[key] = os.path.abspath(self.args[key])

    def normalise(self):
        self.normalise_path('--priv-key-path')
        self.normalise_path('--pub-key-path')
        self.normalise_args()

    def normalise_args(self):
        '''
        Allows attribute access using allow characters,

        e.g.: --priv-key-path -> self.config.priv_key_path
        '''
        for k, v in self.args.items():
            self.args[k.replace('--', '').replace('-', '_')] = v


class Provider:
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


class DigitalOcean(Provider):
    def setup(self):
        self.prepare_token()
        self.prepare_ssh()
        self.get_regions()
        self.choose_random_region()
        self.create_droplet()
        try:
            self.wait_for_droplet()
            self.wait_for_ssh()
            self.connect()
            self.deploy()
            self.run()
            self.show_connection_instructions()
        except Exception:
            traceback.print_exc()
            print('\n\nThe was an error during the creation process.')
            destroy = raw_input(
                    '\nWould you like to destroy the vm at {}? '.format(
                            self.ip_address,
                    )
            )
            if destroy and destroy.lower()[0] == 'y':
                self.destroy_with_retry()

    def destroy_with_retry(self):
        print('Destroying!')

        attempts = 10
        while attempts:
            attempts -= 1
            try:
                self.instance.destroy()
                print('Done!')
                return
            except do.baseapi.DataReadError:
                traceback.print_exc()
                print('Something went wrong (still booting?)')
                print('Retrying with {} attempts left...'.format(attempts))
                time.sleep(5)

    def prepare_token(self):
        if self.config.do_token:
            self.token = self.config.do_token
        else:
            self.ask_token()

        self.manager = functools.partial(do.Manager, token=self.token)
        self.droplet = functools.partial(do.Droplet, token=self.token)
        self.ssh_do = functools.partial(do.SSHKey, token=self.token)

    def ask_token(self):
        print(textwrap.dedent('''
            We will now:
             - Generate or reuse an SSH key pair in *TODO* some directory.
             - Create a $5/mo, 512MB, 1 CPU instance in a random data center.

            Once started:
             - A SSH key pair will be left in *TODO* some directory which can
               be used for SSHing into the droplet.
             - Your droplet will continue living forever until you stop it.
             - Your DigitalOcean access token will not be saved to disk and
               will be forgotten once the script has ended.

            Press Ctrl-C to abort!
        '''))

        self.token = raw_input('Enter a DigitalOcean access token: ')

    def prepare_ssh(self):
        self.ssh_id = self.ssh_do(name='qubinode', public_key=self.pub_key)
        if not self.ssh_id.load_by_pub_key(self.pub_key):
            print('Putting public key into DO account...')
            self.ssh_id.create()

    def get_regions(self):
        self.regions = self.manager().get_all_regions()

    def choose_random_region(self):
        self.region = random.choice(self.regions).slug

    def create_droplet(self):
        print('Creating droplet: {} {}'.format(
                self.config.do_size,
                self.region,
        ))
        self.instance = self.droplet(
                name='qubinode',
                region=self.region,
                image='ubuntu-14-04-x64',
                size_slug=self.config.do_size,
                ssh_keys=[self.pub_key],
        )
        self.instance.create()

    def wait_for_droplet(self):
        print('\nWaiting for Droplet (few minutes)...')

        # This fetches metadata on the VM, including the the IP address.
        time.sleep(10)
        self.instance.load()
        self.show_connection_instructions()

        while True:
            time.sleep(2)
            sys.stdout.write('.')
            sys.stdout.flush()
            actions = self.instance.get_actions()
            for action in actions:
                action.load()
                if action.status == 'completed':
                    return

    def show_connection_instructions(self):
        print('IP Address is {}'.format(self.ip_address))
        print('You can access the VM via this command:')
        print('\nssh -i {} root@{}\n'.format(
                self.config.priv_key_path, self.ip_address
        ))

    def wait_for_ssh(self):
        print('\nWaiting a bit for for SSH...')
        time.sleep(10)

    @property
    def ip_address(self):
        return self.instance.ip_address


class LocalInstaller:
    def __init__(self, config):
        self.config = config

    def setup(self):
        self.swap()
        self.docker_install()
        self.docker_run()

    def shell(self, cmd):
        return subprocess.call(cmd, shell=True)

    def create_file(self, filename, content):
        open(filename, 'w').write(content)

    def swap(self, mb=2048):
        '''
        Creates and activates a swapfile, defaulting to 2GB.

        Also adds it to /etc/fstab
        '''
        if os.path.exists('/swapfile'):
            print('Swapfile already set up...')
            return

        print('Setting up swapfile')
        self.shell('fallocate -l {}M /swapfile'.format(mb))
        self.shell('chmod 600 /swapfile')
        self.shell('mkswap /swapfile')
        self.shell('swapon /swapfile')

        open('/etc/fstab', 'a').write('\n/swapfile none swap defaults 0 0\n')

    def docker_install(self):
        self.shell(
                'apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 '
                '--recv-keys 58118E89F3A912897C070ADBF76221572C52609D'
        )
        self.create_file(
                '/etc/apt/sources.list.d/docker.list',
                'deb https://apt.dockerproject.org/repo ubuntu-trusty main'
        )
        self.shell('apt-get update')
        self.shell('apt-get install -y docker-engine')

    def docker_run_cmd(self):
        cmd = [
            'docker run',
            '--log-driver=json-file',
            '--log-opt="max-size=1m"',
            '--log-opt="max-file=10"',
            '-d',
            '--restart=always',
            '--volume=/var/bitcoin:/root/.bitcoin',
            '--publish=8333:8333',
        ]

        if self.config.prune:
            cmd.append('-e BITCOIN_PRUNE={}'.format(self.config.prune))

        if self.config.bootstrap:
            cmd.append('-e BITCOIN_BOOTSTRAP={}'.format(self.config.bootstrap))

        cmd.append('qubinode/{}'.format(self.config.release))
        return ' '.join(cmd)

    def docker_run(self):
        cmd = self.docker_run_cmd()
        print('Executing {}'.format(cmd))
        self.shell(cmd)


if __name__ == '__main__':
    Qubinode().run()
