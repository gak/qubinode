#!/usr/bin/env python
'''
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode.py spawn (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                    [options]
  qubinode.py local [--release=<version>] [--prune=<MB>]
                    [--swapfile-size=<MB>] [--swapfile-path=<path>]
  qubinode.py list-versions
  qubinode.py list-providers

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  -b --batch                 Non-interactive and choose all options by default.

Install options:
  -s --swapfile=<MB>         Create a swapfile
  --swapfile-path=<path>     Specify swapfile path [default: /swapfile]

Bitcoin options:
  -r --release=<version>     Bitcoin node release [default: XT/0.11D]
  -p --prune=<MB>            Blockchain pruning [default: 2048]

Spawn options:
  --priv-key-path=<path>     [default: ~/.ssh/qubinode]
  --pub-key-path=<path>      [default: ~/.ssh/qubinode.pub]

DigitalOcean options:
  --do-size=<slug>           Size of the provider's instance [default: 512mb]

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
import traceback
import time

import requests
from docopt import docopt
from Crypto.PublicKey import RSA
import paramiko
import digitalocean as do


__version__ = '0.0.1'


NAMES = {
    'XT': 'BitcoinXT',
    'BU': 'Bitcoin Unlimited',
}


RELEASES = {
    'XT/0.11D': {
        'url': 'https://github.com/bitcoinxt/bitcoinxt/releases/download/v0.11D/bitcoin-xt-0.11.0-D-linux64.tar.gz',
        'dir': 'bitcoin-xt-0.11.0-D',
        'sha256': 'ba0e8d553271687bc8184a4a7070e5d350171036f13c838db49bb0aabe5c5e49',
        'install': 'copy_to_root',
    },
    'BU/0.11.2': {
        'url': 'http://www.bitcoinunlimited.info/public/downloads/bitcoinUnlimited-0.11.2-linux64.tar.gz',
        'dir': 'bitcoinUnlimited-0.11.2',
        'sha256': 'c6e83e5910d6b4ad852ac6d6a9ec6c92001a5070bb51d4292577174f22495355',
        'install': 'copy_to_root',
    },
}


PROVIDERS = {
    'do': {
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


class Qubinode:
    def run(self):
        self.config = Config()
        self.config.setup()

        if self.config.spawn:
            self.boot()

        if self.config.local:
            Installer(self.config).setup()

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

    def ask_version(self):
        #for version, release in VERSIONS.items():
        #    print('{}: {}'.format(version, NAMES[version.split('/')[0]]
        self.release = 'BU/0.11.2'
        # self.release = 'XT/0.11D'


class Provider:
    def __init__(self, config):
        self.config = config
        self.ensure_key_pairs()

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
        # TODO: Use fabric api for this
        try:
            if sftp.lstat(filename):
                sftp.unlink(filename)
        except IOError:
            pass

        sftp.put(filename, os.path.join('qubinode', filename))

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
        self.channel.exec_command(
                'bash -c "cd qubinode && bash bootstrap.sh local '
                '--swapfile-size=2048 --prune=2048"'
            )

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
        print(self.pub_key)

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


class Installer:
    def __init__(self, config):
        self.config = config
        self.release = RELEASES[self.config.release]
        self.filename = self.release['url'].split('/')[-1]
        self.data_dir = os.path.expanduser('~/.bitcoin')

    def setup(self):
        self.swap()
        self.docker()
        self.fetch()
        self.checksum()
        self.extract()
        self.install()
        self.upstart()
        self.logrotate()
        self.configure()
        self.restart()

    def shell(self, cmd):
        return subprocess.call(cmd, shell=True)

    def random_string(self, length=40):
        return ''.join([
            random.choice(string.ascii_letters)
            for a in xrange(length) 
        ])

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

    def docker(self):
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

    def fetch(self):
        if os.path.exists(self.filename):
            return
        url = self.release['url']
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
        if downloaded_hash == self.release['sha256']:
            return

        raise ChecksumException(
            '{} from {} expected {} got {}'.format(
                self.filename,
                self.release['url'],
                self.release['sha256'],
                downloaded_hash,
            )
        )

    def extract(self):
        self.shell('tar xvf {}'.format(self.filename))

        if os.path.exists(self.release['dir']):
            return

        raise ExtractionException('Could not see extracted directory')

    def install(self):
        '''
        Dynamically get the method for installing files. e.g. "copy_to_root"
        would translate to self.copy_to_root().
        '''
        print('Installing files...')
        fun = getattr(self, self.release['install'])
        fun()

    def upstart(self):
        '''
        Create an upstart script so bitcoind can start on boot.
        '''
        print('Creating boot scripts...')
        with open('/etc/init/bitcoind.conf', 'w') as f:
            f.write(textwrap.dedent('''
            description "bitcoind"

            start on filesystem
            stop on runlevel [!2345]
            respawn
            respawn limit 10 180
            kill timeout 60

            script
            user=root
            home=/root/.bitcoin
            cmd=/usr/bin/bitcoind
            args="-disablewallet -printtoconsole"
            pidfile=$home/bitcoind.pid
            exec start-stop-daemon --start --make-pidfile -c $user --chdir $home --pidfile $pidfile --exec $cmd -- $args
            end script
            '''))

    def logrotate(self):
        # XXX currently not used because upstart is handling printtoconsole
        # XXX instead of generating a debug.log.
        print('Creating logrotate configuration...')
        with open('/etc/logrotate.d/bitcoin-debug-log', 'w') as f:
            f.write(textwrap.dedent('''
	    /root/.bitcoin/debug.log
	    {
		rotate 5
		copytruncate
		daily
		missingok
		notifempty
		compress
		delaycompress
		sharedscripts
	    }
            '''))

    def configure(self):
        print('Creating bitcoin.conf')
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        with open(os.path.join(self.data_dir, 'bitcoin.conf'), 'w') as f:
            if self.config.prune:
                f.write('prune={}\n'.format(self.config.prune))
            f.write('rpcuser={}\n'.format(self.random_string()))
            f.write('rpcpassword={}\n'.format(self.random_string()))

    def restart(self):
        print('Starting daemon...')
        self.shell('stop bitcoind')
        self.shell('start bitcoind')

    def copy_to_root(self):
        '''
        Copies all directories and files from the extracted directory
        into /usr/.
        
        e.g. bitcoind-xt-0.11D/bin/bitcoind -> /usr/bin/bitcoind
        '''
        self.shell('cd {} && cp -vr * /usr/'.format(
            self.release['dir'],
        ))

        if os.path.exists('/usr/bin/bitcoind'):
            return

        raise InstallationException('/usr/bin/bitcoind does not exist')


if __name__ == '__main__':
    Qubinode().run()

