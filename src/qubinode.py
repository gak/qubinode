#!/usr/bin/env python
'''
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode.py spawn
  qubinode.py local

Options:
  -h --help     Show this screen.
  --version     Show version.
'''
import os
import sys
import glob
import shutil
import string
import functools
import random
import hashlib
import subprocess
import textwrap

import requests
from docopt import docopt
from Crypto.PublicKey import RSA
import digitalocean as do


__version__ = '0.0.1'


NAMES = {
    'XT': 'BitcoinXT',
}


VERSIONS = {
    'XT/0.11D': {
        'url': 'https://github.com/bitcoinxt/bitcoinxt/releases/download/v0.11D/bitcoin-xt-0.11.0-D-linux64.tar.gz',
        'dir': 'bitcoin-xt-0.11.0-D',
        'sha256': 'ba0e8d553271687bc8184a4a7070e5d350171036f13c838db49bb0aabe5c5e49',
        'install': 'copy_to_root',
    },
}


PROVIDERS = {
    'DO': {
        'name': 'DigitalOcean',
        'class': 'DigitalOcean',
    }
}


class ChecksumException(Exception):
    pass


class ExtractionException(Exception):
    pass


class InstallationException(Exception):
    pass


class Config:
    def __init__(self):
        self.priv_key_path = 'key'
        self.pub_key_path = 'key.pub'

    def parse_args(self):
        self.args = docopt(__doc__, version=__version__)
        print(self.args)

    def ask(self):
        self.ask_version()
        # self.ask_key_path()
        self.ask_provider()

    def ask_provider(self):
        self.provider = PROVIDERS['DO']

    def ask_version(self):
        #for version, target in VERSIONS.items():
        #    print('{}: {}'.format(version, NAMES[version.split('/')[0]]
        self.target = 'XT/0.11D'


class Provider:
    def __init__(self, config):
        self.config = config
        self.ensure_key_pairs()

    def ensure_key_pairs(self):
        if not os.path.exists(self.config.priv_key_path):
            self.generate_key_pairs()
        self.load_key_pairs()

    def generate_key_pairs(self):
        key = RSA.generate(2048)

        with open(self.config.priv_key_path, 'w') as f:
            f.write(key.exportKey('PEM'))
        with open(self.config.pub_key_path, 'w') as f:
            f.write(key.publickey().exportKey('OpenSSH'))

        os.chmod(self.config.priv_key_path, 0600)

    def load_key_pairs(self):
        self.pub_key = open(self.config.pub_key_path).read()
        self.priv_key = open(self.config.priv_key_path).read()


class DigitalOcean(Provider):
    def setup(self):
        self.ask_token()
        self.prepare_ssh()
        self.get_regions()
        self.choose_random_region()
        self.create_droplet()
        self.wait_for_droplet()

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

        self.token = raw_input('Enter a generated DigitalOcean access token: ')
        self.manager = functools.partial(do.Manager, token=self.token)
        self.droplet = functools.partial(do.Droplet, token=self.token)
        self.ssh_do = functools.partial(do.SSHKey, token=self.token)

    def prepare_ssh(self):
        self.ssh_id = self.ssh_do(name='qubinode', public_key=self.pub_key)
        if not self.ssh_id.load_by_pub_key(self.pub_key):
            self.ssh_id.create()

    def get_regions(self):
        self.regions = self.manager().get_all_regions()

    def choose_random_region(self):
        self.region = random.choice(self.regions).slug

    def create_droplet(self):
        self.instance = self.droplet(
            name='qubinode',
            region=self.region,
            image='ubuntu-14-04-x64',
            size_slug='512mb',
            ssh_keys=[self.pub_key],
        )
        self.instance.create()

    def wait_for_droplet(self):
        print('Waiting for Droplet (1-2 minutes)...')

        while True:
            print('...')
            actions = self.instance.get_actions()
            for action in actions:
                action.load()
                print(action.status)
                if action.status == 'completed':
                    return True

    def ip_address(self):
        return self.instance.ip_address


class Installer:
    def __init__(self, config):
        self.config = config
        self.target = VERSIONS[self.config.target]
        self.filename = self.target['url'].split('/')[-1]
        self.data_dir = os.path.expanduser('~/.bitcoin')

    def setup(self):
        self.boot()
        self.swap()
        self.fetch()
        self.checksum()
        self.extract()
        self.install()
        self.upstart()
        self.configure()
        self.restart()

    def shell(self, cmd):
        return subprocess.call(cmd, shell=True)

    def random_string(self, length=40):
        return ''.join([
            random.choice(string.ascii_letters)
            for a in xrange(length) 
        ])

    def boot(self):
        '''
        Run the provider class that will start the VM.
        '''
        fun = globals()[self.config.provider['class']]
        fun(self.config).setup()

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

    def fetch(self):
        if os.path.exists(self.filename):
            return
        url = self.target['url']
        print('Downloading {}'.format(url))
        r = requests.get(url, stream=True)
	with open(self.filename, 'wb') as f:
	    for chunk in r.iter_content(chunk_size=1024): 
		if chunk:
		    f.write(chunk)
        print('Downloading {} complete...'.format(url))

    def downloaded_hash(self):
        return hashlib.sha256(open(self.filename, 'rb').read()).hexdigest()

    def checksum(self):
        print('Checking sha256 of package...')
        downloaded_hash = self.downloaded_hash()
        if downloaded_hash == self.target['sha256']:
            return

        raise ChecksumException(
            '{} from {} expected {} got {}'.format(
                self.filename,
                self.target['url'],
                self.target['sha256'],
                downloaded_hash,
            )
        )

    def extract(self):
        self.shell('tar xvf {}'.format(self.filename))

        if os.path.exists(self.target['dir']):
            return

        raise ExtractionException('Could not see extracted directory')

    def install(self):
        '''
        Dynamically get the method for installing files. e.g. "copy_to_root"
        would translate to self.copy_to_root().
        '''
        print('Installing files...')
        fun = getattr(self, self.target['install'])
        fun()

    def upstart(self):
        '''
        Create an upstart script so bitcoind can start on boot.
        '''
        print('Creating boot scripts...')
        with open('/etc/init/bitcoind', 'w') as f:
            f.write(textwrap.dedent('''
            description "bitcoind"

            start on filesystem
            stop on runlevel [!2345]
            oom score -500
            expect fork
            respawn
            respawn limit 10 60 # 10 times in 60 seconds

            script
            user=root
            home=/root/.bitcoind
            cmd=/usr/bin/bitcoind -daemon
            pidfile=$home/bitcoind.pid
            [[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
            [[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
            exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile --startas $cmd -b -m
            end script
            '''))

    def configure(self):
        print('Creating bitcoin.conf')
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        with open(os.path.join(self.data_dir, 'bitcoin.conf'), 'w') as f:
            f.write('prune={}'.format(1024 * 5))
            f.write('rpcuser={}'.format(self.random_string()))
            f.write('rpcpassword={}'.format(self.random_string()))

    def restart(self):
        print('Starting daemon...')
        self.shell('restart bitcoind')

    def copy_to_root(self):
        '''
        Copies all directories and files from the extracted directory
        into /usr/.
        
        e.g. bitcoind-xt-0.11D/bin/bitcoind -> /usr/bin/bitcoind
        '''
        self.shell('cd {} && cp -vr * /usr/'.format(
            self.target['dir']
        ))

        if os.path.exists('/usr/bin/bitcoind'):
            return

        raise InstallationException('/usr/bin/bitcoind does not exist')


if __name__ == '__main__':
    config = Config()
    config.parse_args()
    config.ask()
    Installer(config).setup()

