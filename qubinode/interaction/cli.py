import sys

from qubinode.provider.generic import GenericProvider
from .interaction import Interaction
from ..local_installer import LocalInstaller


class CommandLineInteraction(Interaction):
    def setup(self):
        print('setup in cli')

    def run(self):
        if self.cfg.list_releases:
            self.list_releases()
            return

        self.ask_release()

        if self.cfg.spawn_vm:
            self.boot()

        elif self.cfg.local:
            LocalInstaller(self.cfg).setup()

        elif self.cfg.deploy:
            GenericProvider(self.cfg).setup()

        else:
            print('Unknown command!')

    def list_releases(self):
        for code, variant in self.releases.iteritems():
            print(' - ({}) {}'.format(code, variant['title']))

    def ask_release(self):
        if self.cfg.release != 'ask':
            pass
        elif self.cfg.batch:
            self.cfg.release = 'xt:0.11.0d'
        else:
            self.list_releases()
            self.cfg.release = raw_input('Which release to install? ')

        if self.cfg.release not in self.releases:
            print('Unknown release: {}'.format(self.cfg.release))
            sys.exit(-1)
