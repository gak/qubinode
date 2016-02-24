'''
Qubinode - Quick Bitcoin Node Deploy

Usage:
  qubinode gui
  qubinode spawn-vm (do|digitalocean) [--do-size=<slug>] [--do-token=<token>]
                    [options]
  qubinode deploy --address=<address [options]
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

Host options:
  --address=<address>        Address of host
  --default-keys             Normal SSH configuration for keys [default: False]
  --priv-key-path=<path>     [default: ~/.ssh/qubinode]
  --pub-key-path=<path>      [default: ~/.ssh/qubinode.pub]

DigitalOcean options:
  --do-token=<token>         Digital Ocean API token
  --do-size=<slug>           Size of the provider's instance [default: 512mb]

'''
import os
import sys

import yaml
from docopt import docopt

from .interaction.cli import CommandLineInteraction
from .interaction.gui import GraphicalInteraction
from .settings.providers import PROVIDERS
from .settings.app import __version__


class Config(object):
    def __init__(self):
        self.args = {}
        self.settings = None

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

    def parse_args(self, argv):
        self.args = docopt(__doc__, version=__version__, argv=argv)

    def setup(self, gui=False):
        argv = sys.argv[1:]
        if gui:
            argv.insert(0, 'gui')

        self.parse_args(argv)
        self.settings = yaml.load(open('settings.yaml'))
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
        Allows attribute access using underscore characters,

        e.g.: --priv-key-path -> self.config.priv_key_path
        '''
        for k, v in self.args.items():
            self.args[k.replace('--', '').replace('-', '_')] = v

    def get_interaction(self):
        if self.gui:
            return GraphicalInteraction(self)
        else:
            return CommandLineInteraction(self)
