'''
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode
  qubinode spawn-vm (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                       [options]
  qubinode local [options]
  qubinode list-releases
  qubinode list-providers

Options:
  -h --help                  Show this screen
  --version                  Show version
  -b --batch                 Non-interactive and choose all options by default
  -g --gui                   Interact with a GUI window [default: True]
  -c --cli                   Interact with a console

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
import os

from docopt import docopt

from src.entrypoint import PROVIDERS, __version__


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

    def get_interaction(self):
        if self.gui:
            return Gui()
